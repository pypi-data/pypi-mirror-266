import asyncio
import collections.abc
import dataclasses
import datetime as dt
import functools
import logging
import operator
import re
import shlex
import typing
from typing import Any, Mapping, Sequence

import asyncssh
import backoff
import humanize
import jinja2 as j2
from asyncssh.auth import KbdIntPrompts, KbdIntResponse
from asyncssh.misc import MaybeAwait
from rich.table import Table
from xmanager import xm

from xm_slurm import batching, config, status, utils
from xm_slurm.console import console

SlurmClusterConfig = config.SlurmClusterConfig
ContainerRuntime = config.ContainerRuntime

"""
=== Runtime Configurations ===
With RunC:
    skopeo copy --dest-creds=<username>:<secret> docker://<image>@<digest> oci:<image>:<digest>

    pushd $SLURM_TMPDIR

    umoci raw unpack --rootless --image <image>:<digest> bundle/<digest>
    umoci raw runtime-config --image <image>:<digest> bundle/<digest>/config.json

    runc run -b bundle/<digest> <container-id>

With Singularity / Apptainer:

    apptainer build --fix-perms --sandbox <digest> docker://<image>@<digest>
    apptainer run --compat <digest>
"""

"""
#SBATCH --error=/dev/null
#SBATCH --output=/dev/null
"""

_POLL_INTERVAL = 30.0
_BATCHED_BATCH_SIZE = 16
_BATCHED_TIMEOUT = 0.2


class SlurmExecutionError(Exception): ...


class NoKBAuthSSHClient(asyncssh.SSHClient):
    """SSHClient that does not prompt for keyboard-interactive authentication."""

    def kbdint_auth_requested(self) -> MaybeAwait[str | None]:
        return ""

    def kbdint_challenge_received(
        self, name: str, instructions: str, lang: str, prompts: KbdIntPrompts
    ) -> MaybeAwait[KbdIntResponse | None]:
        del name, instructions, lang, prompts
        return []


def _group_by_cluster(
    clusters: Sequence[SlurmClusterConfig], job_ids: Sequence[str]
) -> dict[SlurmClusterConfig, list[str]]:
    jobs_by_cluster = collections.defaultdict(list)
    for cluster, job_id in zip(clusters, job_ids):
        jobs_by_cluster[cluster].append(job_id)
    return jobs_by_cluster


class _BatchedSlurmHandle:
    @functools.partial(
        batching.batch,
        max_batch_size=_BATCHED_BATCH_SIZE,
        batch_timeout=_BATCHED_TIMEOUT,
    )
    @staticmethod
    async def _batched_get_state(
        clusters: Sequence[SlurmClusterConfig], job_ids: Sequence[str]
    ) -> Sequence[status.SlurmJobState]:
        async def _get_state(
            cluster: SlurmClusterConfig, job_ids: Sequence[str]
        ) -> Sequence[status.SlurmJobState]:
            result = await get_client().run(
                cluster,
                [
                    "sacct",
                    "--jobs",
                    ",".join(job_ids),
                    "--format",
                    "JobID,State",
                    "--allocations",
                    "--noheader",
                    "--parsable2",
                ],
                check=True,
            )

            assert isinstance(result.stdout, str)
            states_by_job_id = {}
            for line in result.stdout.splitlines():
                job_id, state = line.split("|")
                states_by_job_id[job_id] = status.SlurmJobState.from_slurm_str(state)

            job_states = []
            for job_id in job_ids:
                if job_id in states_by_job_id:
                    job_states.append(states_by_job_id[job_id])
                # This is a stupid hack around sacct's inability to display state information for
                # array job elements that haven't begun. We'll assume that if the job ID is not found,
                # and it's an array job, then it's pending.
                elif re.match(r"^\d+_\d+$", job_id) is not None:
                    job_states.append(status.SlurmJobState.PENDING)
                else:
                    raise SlurmExecutionError(f"Failed to find job state info for {job_id}")
            return job_states

        jobs_by_cluster = _group_by_cluster(clusters, job_ids)

        job_states_per_cluster = await asyncio.gather(*[
            _get_state(cluster, job_ids) for cluster, job_ids in jobs_by_cluster.items()
        ])
        job_states_by_cluster: dict[SlurmClusterConfig, dict[str, status.SlurmJobState]] = {}
        for cluster, job_states in zip(clusters, job_states_per_cluster):
            job_states_by_cluster[cluster] = dict(zip(jobs_by_cluster[cluster], job_states))

        job_states = []
        for cluster, job_id in zip(clusters, job_ids):
            job_states.append(job_states_by_cluster[cluster][job_id])
        return job_states

    @functools.partial(
        batching.batch,
        max_batch_size=_BATCHED_BATCH_SIZE,
        batch_timeout=_BATCHED_TIMEOUT,
    )
    @staticmethod
    async def _batched_cancel(
        clusters: Sequence[SlurmClusterConfig], job_ids: Sequence[str]
    ) -> Sequence[None]:
        async def _cancel(cluster: SlurmClusterConfig, job_ids: Sequence[str]) -> None:
            await get_client().run(cluster, ["scancel", " ".join(job_ids)], check=True)

        jobs_by_cluster = _group_by_cluster(clusters, job_ids)
        return await asyncio.gather(*[
            _cancel(cluster, job_ids) for cluster, job_ids in jobs_by_cluster.items()
        ])


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmHandle(_BatchedSlurmHandle):
    """A handle for referring to the launched container."""

    cluster: SlurmClusterConfig
    job_id: str

    def __post_init__(self):
        if re.match(r"^\d+(_\d+|\+\d+)?$", self.job_id) is None:
            raise ValueError(f"Invalid job ID: {self.job_id}")

    @backoff.on_predicate(
        backoff.constant,
        lambda state: state in status.SlurmActiveJobStates,
        jitter=None,
        interval=_POLL_INTERVAL,
    )
    async def wait(self) -> status.SlurmJobState:
        return await self.get_state()

    async def stop(self) -> None:
        await self._batched_cancel(self.cluster, self.job_id)

    async def get_state(self) -> status.SlurmJobState:
        return await self._batched_get_state(self.cluster, self.job_id)


@functools.cache
def get_client() -> "Client":
    return Client()


@functools.cache
def get_template_env(container_runtime: ContainerRuntime) -> j2.Environment:
    template_loader = j2.PackageLoader("xm_slurm", "templates/slurm")
    template_env = j2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=False)

    def _raise_template_exception(msg: str) -> None:
        raise j2.TemplateRuntimeError(msg)

    template_env.globals["raise"] = _raise_template_exception
    template_env.globals["operator"] = operator

    match container_runtime:
        case ContainerRuntime.SINGULARITY | ContainerRuntime.APPTAINER:
            runtime_template = template_env.get_template("runtimes/apptainer.bash.j2")
        case ContainerRuntime.PODMAN:
            runtime_template = template_env.get_template("runtimes/podman.bash.j2")
        case _:
            raise NotImplementedError
    # Update our global env with the runtime template's exported globals
    template_env.globals.update(runtime_template.module.__dict__)

    return template_env


class Client:
    def __init__(self):
        self._connections: dict[SlurmClusterConfig, asyncssh.SSHClientConnection] = {}
        self._connection_lock = asyncio.Lock()

        self._clusters = config.clusters(utils.find_project_root() / "pyproject.toml")

    @backoff.on_exception(backoff.expo, asyncssh.Error, max_tries=5, max_time=60.0)
    async def _setup_remote_connection(self, conn: asyncssh.SSHClientConnection) -> None:
        # Make sure the xm-slurm state directory exists
        await conn.run("mkdir -p ~/.local/state/xm-slurm", check=True)

    async def connection(self, cluster: SlurmClusterConfig) -> asyncssh.SSHClientConnection:
        if cluster not in self._connections:
            async with self._connection_lock:
                try:
                    conn, _ = await asyncssh.create_connection(
                        NoKBAuthSSHClient,
                        host=cluster.host,
                        port=cluster.port or (),
                        username=cluster.user,
                        config=None,
                    )
                    await self._setup_remote_connection(conn)
                    self._connections[cluster] = conn
                except asyncssh.misc.PermissionDenied as ex:
                    raise RuntimeError(f"Permission denied connecting to {cluster.host}") from ex
        return self._connections[cluster]

    @backoff.on_exception(backoff.expo, asyncssh.Error, max_tries=5, max_time=60.0)
    async def run(
        self,
        cluster: SlurmClusterConfig,
        command: xm.SequentialArgs | str | Sequence[str],
        *,
        check: bool = False,
        timeout: float | None = None,
    ) -> asyncssh.SSHCompletedProcess:
        client = await self.connection(cluster)
        if isinstance(command, xm.SequentialArgs):
            command = command.to_list()
        if not isinstance(command, str) and isinstance(command, collections.abc.Sequence):
            command = shlex.join(command)
        assert isinstance(command, str)
        if cluster.cwd:
            logging.debug("Running command on %s: %s from %s", cluster.host, command, cluster.cwd)
            command = f"cd {cluster.cwd} && {command}"
        else:
            logging.debug("Running command on %s: %s", cluster.host, command)

        return await client.run(command, check=check, timeout=timeout)

    async def template(
        self,
        *,
        job: xm.Job | xm.JobGroup,
        cluster: SlurmClusterConfig,
        args: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
        experiment_id: int,
        identity: str | None,
    ) -> str:
        if args is None:
            args = {}

        template_env = get_template_env(cluster.runtime)

        # Sanitize job groups
        if isinstance(job, xm.JobGroup) and len(job.jobs) == 1:
            job = typing.cast(xm.Job, list(job.jobs.values())[0])
        elif isinstance(job, xm.JobGroup) and len(job.jobs) == 0:
            raise ValueError("Job group must have at least one job")

        match job:
            case xm.Job() as job_array if isinstance(args, collections.abc.Sequence):
                template = template_env.get_template("job-array.bash.j2")
                sequential_args = [
                    xm.SequentialArgs.from_collection(trial.get("args", None)) for trial in args
                ]
                env_vars = [trial.get("env_vars") for trial in args]
                if any(env_vars):
                    raise NotImplementedError(
                        "Job arrays over environment variables are not yet supported."
                    )

                return template.render(
                    job=job_array,
                    cluster=cluster,
                    args=sequential_args,
                    env_vars=env_vars,
                    experiment_id=experiment_id,
                    identity=identity,
                )
            case xm.Job() if isinstance(args, collections.abc.Mapping):
                template = template_env.get_template("job.bash.j2")
                sequential_args = xm.SequentialArgs.from_collection(args.get("args", None))
                env_vars = args.get("env_vars", None)
                return template.render(
                    job=job,
                    cluster=cluster,
                    args=sequential_args,
                    env_vars=env_vars,
                    experiment_id=experiment_id,
                    identity=identity,
                )
            case xm.JobGroup() as job_group if isinstance(args, collections.abc.Mapping):
                template = template_env.get_template("job-group.bash.j2")
                sequential_args = {
                    job_name: {
                        "args": args.get(job_name, {}).get("args", None),
                    }
                    for job_name in job_group.jobs.keys()
                }
                env_vars = {
                    job_name: args.get(job_name, {}).get("env_vars", None)
                    for job_name in job_group.jobs.keys()
                }
                return template.render(
                    job_group=job_group,
                    cluster=cluster,
                    args=sequential_args,
                    env_vars=env_vars,
                    experiment_id=experiment_id,
                    identity=identity,
                )
            case _:
                raise ValueError(f"Unsupported job type: {type(job)}")

    async def _select_cluster(
        self,
        *,
        job: xm.Job | xm.JobGroup,
        args: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
        experiment_id: int,
        identity: str | None,
    ) -> tuple[SlurmClusterConfig, dt.datetime | BaseException]:
        assert len(self._clusters) > 0, "Need at least one cluster"

        async def _cluster_eta(cluster: SlurmClusterConfig) -> dt.datetime:
            template = await self.template(
                job=job,
                cluster=cluster,
                args=args,
                experiment_id=experiment_id,
                identity=identity,
            )
            command = f"sbatch --test-only <<'SBATCH_EOF'\n{template}\nSBATCH_EOF"
            result = await self.run(cluster, command)
            if result.returncode != 0:
                raise SlurmExecutionError(
                    f"Failed to test job on host {cluster.host}.\n{result.stderr}"
                )
            assert result.stderr is not None and isinstance(result.stderr, str)
            if match := re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{1,2}:\d{1,2})", result.stderr):
                return dt.datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
            raise SlurmExecutionError(
                f"Failed to parse job ETA on cluster {cluster.host}\n{result.stderr}"
            )

        now = dt.datetime.now()
        etas = await asyncio.gather(
            *[_cluster_eta(cluster) for cluster in self._clusters],
            return_exceptions=True,
        )
        sorted_cluster_etas: list[tuple[SlurmClusterConfig, dt.datetime | BaseException]] = list(
            sorted(
                zip(self._clusters, etas),
                key=lambda x: dt.datetime.max if isinstance(x[1], Exception) else x[1],  # type: ignore
            )
        )

        table = Table(title="Cluster ETAs")
        table.add_column("Cluster", justify="right", style="cyan", no_wrap=True)
        table.add_column("Account", justify="center", style="cyan", no_wrap=True)
        table.add_column("Partition", justify="center", style="cyan", no_wrap=True)
        table.add_column("QoS", justify="center", style="cyan", no_wrap=True)
        table.add_column("Scheduled Time", style="bold magenta")
        for cluster, eta_or_exception in sorted_cluster_etas:
            if isinstance(eta_or_exception, SlurmExecutionError):
                logging.warning(str(eta_or_exception))
                continue
            elif isinstance(eta_or_exception, Exception):
                raise eta_or_exception

            table.add_row(
                cluster.host,
                cluster.account,
                cluster.partition,
                cluster.qos,
                humanize.naturaltime(eta_or_exception, when=now),
            )
        console.print(table)

        return sorted_cluster_etas[0]

    @typing.overload
    async def launch(
        self,
        *,
        job: xm.Job | xm.JobGroup,
        args: Mapping[str, Any] | None,
        experiment_id: int,
        identity: str | None = ...,
    ) -> SlurmHandle: ...

    @typing.overload
    async def launch(
        self,
        *,
        job: xm.Job | xm.JobGroup,
        args: Sequence[Mapping[str, Any]],
        experiment_id: int,
        identity: str | None = ...,
    ) -> Sequence[SlurmHandle]: ...

    async def launch(
        self,
        *,
        job: xm.Job | xm.JobGroup,
        args: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
        experiment_id: int,
        identity: str | None = None,
    ) -> SlurmHandle | Sequence[SlurmHandle]:
        # Select cluster to run on
        cluster, eta_or_exception = await self._select_cluster(
            job=job,
            args=args,
            experiment_id=experiment_id,
            identity=identity,
        )

        # Construct template
        template = await self.template(
            job=job,
            cluster=cluster,
            args=args,
            experiment_id=experiment_id,
            identity=identity,
        )
        logging.debug("Slurm submission script:\n%s", template)

        # Construct and run command on the cluster
        command = f"sbatch --chdir $HOME/.local/state/xm-slurm/{experiment_id} --parsable <<'SBATCH_EOF'\n{template}\nSBATCH_EOF"
        result = await self.run(cluster, command)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to schedule job on {cluster.host}: {result.stderr}")

        assert isinstance(result.stdout, str)
        slurm_job_id, *_ = result.stdout.split(",")
        slurm_job_id = slurm_job_id.strip()

        # If eta_or_exception is an exception, we have already logged the warning
        # se we don't need to do it again here.
        # TODO: Move this into the resource selector.
        if isinstance(eta_or_exception, dt.datetime):
            console.print(
                f"[magenta]:rocket: Job [cyan]{slurm_job_id}[/cyan] will be launched on "
                f"[cyan]{cluster.host}[/cyan] "
                f"{humanize.naturaltime(max(eta_or_exception, dt.datetime.now()), when=dt.datetime.now())}."
            )

        if isinstance(job, xm.Job) and isinstance(args, collections.abc.Sequence):
            return [
                SlurmHandle(cluster=cluster, job_id=f"{slurm_job_id}_{array_index}")
                for array_index in range(len(args))
            ]

        return SlurmHandle(cluster=cluster, job_id=slurm_job_id)


@typing.overload
async def launch(
    *,
    job: xm.Job | xm.JobGroup,
    args: Mapping[str, Any],
    experiment_id: int,
    identity: str | None = ...,
) -> SlurmHandle: ...


@typing.overload
async def launch(
    *,
    job: xm.Job | xm.JobGroup,
    args: Sequence[Mapping[str, Any]],
    experiment_id: int,
    identity: str | None = ...,
) -> Sequence[SlurmHandle]: ...


async def launch(
    *,
    job: xm.Job | xm.JobGroup,
    args: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    experiment_id: int,
    identity: str | None = None,
) -> SlurmHandle | Sequence[SlurmHandle]:
    return await get_client().launch(
        job=job,
        args=args,
        experiment_id=experiment_id,
        identity=identity,
    )
