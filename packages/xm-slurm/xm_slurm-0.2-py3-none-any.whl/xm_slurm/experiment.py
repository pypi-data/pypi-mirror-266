import asyncio
import collections.abc
import contextvars
import dataclasses
import functools
import inspect
import json
import os
import typing
from concurrent import futures
from typing import Any, Awaitable, Callable, Mapping, MutableSet, Sequence

from xmanager import xm
from xmanager.xm import async_packager, id_predictor

from xm_slurm import api, execution
from xm_slurm.console import console
from xm_slurm.packaging import router
from xm_slurm.status import SlurmWorkUnitStatus
from xm_slurm.utils import UserSet

_current_job_array_queue = contextvars.ContextVar[
    asyncio.Queue[tuple[xm.JobGroup, asyncio.Future]] | None
]("_current_job_array_queue", default=None)


def _validate_job(
    job: xm.JobType,
    args_view: Mapping[str, Any],
) -> None:
    if not args_view:
        return
    if not isinstance(args_view, collections.abc.Mapping):
        raise ValueError("Job arguments via `experiment.add` must be mappings")

    if isinstance(job, xm.JobGroup) and len(job.jobs) == 0:
        raise ValueError("Job group is empty")

    if isinstance(job, xm.JobGroup) and any(
        isinstance(child, xm.JobGroup) for child in job.jobs.values()
    ):
        raise ValueError("Nested job groups are not supported")

    allowed_keys = {"args", "env_vars"}
    for key, expanded in args_view.items():
        if isinstance(job, xm.JobGroup) and len(job.jobs) > 1 and key not in job.jobs:
            raise ValueError(
                f"Argument key `{key}` doesn't exist in job group with keys {job.jobs.keys()}"
            )

        if isinstance(job, xm.JobGroup) and key in job.jobs:
            _validate_job(job.jobs[key], expanded)
        elif key not in allowed_keys:
            raise ValueError(f"Only `args` and `env_vars` are supported for args on job {job!r}.")


@dataclasses.dataclass(kw_only=True, frozen=True)
class Artifact:
    name: str
    uri: str

    def __hash__(self) -> int:
        return hash(self.name)


class ContextArtifacts(UserSet[Artifact]):
    def __init__(
        self,
        owner: "SlurmExperiment | SlurmExperimentUnit",
        *,
        artifacts: Sequence[Artifact],
    ):
        super().__init__(
            artifacts,
            on_add=self._on_add_artifact,
            on_remove=self._on_remove_artifact,
            on_discard=self._on_remove_artifact,
        )
        self._owner = owner
        self._create_task = self._owner._create_task

    def _on_add_artifact(self, artifact: Artifact) -> None:
        match self._owner:
            case SlurmExperiment():
                api.client().insert_experiment_artifact(
                    self._owner.experiment_id,
                    api.ArtifactModel(
                        name=artifact.name,
                        uri=artifact.uri,
                    ),
                )
            case SlurmWorkUnit():
                api.client().insert_work_unit_artifact(
                    self._owner.experiment_id,
                    self._owner.work_unit_id,
                    api.ArtifactModel(
                        name=artifact.name,
                        uri=artifact.uri,
                    ),
                )

    def _on_remove_artifact(self, artifact: Artifact) -> None:
        match self._owner:
            case SlurmExperiment():
                api.client().delete_experiment_artifact(self._owner.experiment_id, artifact.name)
            case SlurmWorkUnit():
                api.client().delete_work_unit_artifact(
                    self._owner.experiment_id, self._owner.work_unit_id, artifact.name
                )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmExperimentUnitMetadataContext:
    artifacts: ContextArtifacts


class SlurmExperimentUnit(xm.ExperimentUnit):
    """ExperimentUnit is a collection of semantically associated `Job`s."""

    experiment: "SlurmExperiment"

    def __init__(
        self,
        experiment: xm.Experiment,
        create_task: Callable[[Awaitable[Any]], futures.Future[Any]],
        args: Mapping[str, Any] | None,
        role: xm.ExperimentUnitRole,
    ) -> None:
        super().__init__(experiment, create_task, args, role)
        self._launched_jobs: list[xm.LaunchedJob] = []
        self._execution_handles: list[execution.SlurmHandle] = []
        self._context = SlurmExperimentUnitMetadataContext(
            artifacts=ContextArtifacts(owner=self, artifacts=[]),
        )

    async def _submit_jobs_for_execution(
        self,
        job: xm.Job | xm.JobGroup,
        args_view: Mapping[str, Any],
        identity: str | None = None,
    ) -> execution.SlurmHandle:
        return await execution.launch(
            job=job,
            args=args_view,
            experiment_id=self.experiment_id,
            identity=identity,
        )

    def _ingest_launched_jobs(self, job: xm.JobType, handle: execution.SlurmHandle) -> None:
        match job:
            case xm.JobGroup() as job_group:
                for job in job_group.jobs.values():
                    self._launched_jobs.append(
                        xm.LaunchedJob(
                            name=job.name,  # type: ignore
                            address=str(handle.job_id),
                        )
                    )
            case xm.Job():
                self._launched_jobs.append(
                    xm.LaunchedJob(
                        name=handle.job.name,  # type: ignore
                        address=str(handle.job_id),
                    )
                )

    async def _wait_until_complete(self) -> None:
        try:
            await asyncio.gather(*[handle.wait() for handle in self._execution_handles])
        except RuntimeError as error:
            raise xm.ExperimentUnitFailedError(error)

    def stop(
        self,
        *,
        mark_as_failed: bool = False,
        mark_as_completed: bool = False,
        message: str | None = None,
    ) -> None:
        del mark_as_failed, mark_as_completed, message

        async def _stop_awaitable() -> None:
            try:
                await asyncio.gather(*[handle.stop() for handle in self._execution_handles])
            except RuntimeError as error:
                raise xm.ExperimentUnitFailedError(error)

        self.experiment._create_task(_stop_awaitable())

    async def get_status(self) -> SlurmWorkUnitStatus:
        states = await asyncio.gather(*[handle.get_state() for handle in self._execution_handles])
        return SlurmWorkUnitStatus.aggregate(states)

    def launched_jobs(self) -> list[xm.LaunchedJob]:
        return self._launched_jobs

    @property
    def context(self) -> SlurmExperimentUnitMetadataContext:
        return self._context


class SlurmWorkUnit(xm.WorkUnit, SlurmExperimentUnit):
    def __init__(
        self,
        experiment: "SlurmExperiment",
        create_task: Callable[[Awaitable[Any]], futures.Future],
        args: Mapping[str, Any],
        role: xm.ExperimentUnitRole,
        work_unit_id_predictor: id_predictor.Predictor,
    ) -> None:
        super().__init__(experiment, create_task, args, role)
        self._work_unit_id_predictor = work_unit_id_predictor
        self._work_unit_id = self._work_unit_id_predictor.reserve_id()
        api.client().insert_work_unit(
            self.experiment_id,
            api.WorkUnitPatchModel(
                wid=self.work_unit_id,
                identity=self.identity,
                args=json.dumps(args),
            ),
        )

    def _ingest_handle(self, handle: execution.SlurmHandle) -> None:
        self._execution_handles.append(handle)
        api.client().insert_job(
            self.experiment_id,
            self.work_unit_id,
            api.SlurmJobModel(
                name=self.experiment_unit_name,
                slurm_job_id=handle.job_id,  # type: ignore
                slurm_cluster=handle.cluster.to_json(),
            ),
        )

    async def _launch_job_group(
        self,
        job: xm.JobGroup,
        args_view: Mapping[str, Any],
        identity: str,
    ) -> None:
        global _current_job_array_queue
        _validate_job(job, args_view)

        future = asyncio.Future()
        async with self._work_unit_id_predictor.submit_id(self.work_unit_id):  # type: ignore
            # If we're scheduling as part of a job queue (i.e., the queue is set on the context)
            # then we'll insert the job and current future that'll get resolved to the
            # proper handle.
            if job_array_queue := _current_job_array_queue.get():
                job_array_queue.put_nowait((job, future))
            # Otherwise we'll resolve the future with the scheduled job immediately
            else:
                # Set the result inside of the context manager so we don't get out-of-order
                # id scheduling...
                future.set_result(
                    await self._submit_jobs_for_execution(job, args_view, identity=identity)
                )

        # Wait for the job handle, this is either coming from scheduling the job array
        # or from the single job above.
        handle = await future
        self._ingest_handle(handle)
        self._ingest_launched_jobs(job, handle)

    @property
    def experiment_unit_name(self) -> str:
        return f"{self.experiment_id}_{self._work_unit_id}"

    @property
    def work_unit_id(self) -> int:
        return self._work_unit_id

    def __repr__(self, /) -> str:
        return f"<SlurmWorkUnit {self.experiment_unit_name}>"


class SlurmAuxiliaryUnit(SlurmExperimentUnit):
    """An auxiliary unit operated by the Slurm backend."""

    def _ingest_handle(self, handle: execution.SlurmHandle) -> None:
        del handle
        console.print("[red]Auxiliary units do not currently support ingestion.[/red]")

    async def _launch_job_group(
        self,
        job: xm.Job | xm.JobGroup,
        args_view: Mapping[str, Any],
        identity: str,
    ) -> None:
        _validate_job(job, args_view)

        slurm_handle = await self._submit_jobs_for_execution(job, args_view, identity=identity)
        self._ingest_handle(slurm_handle)
        self._ingest_launched_jobs(job, slurm_handle)

    @property
    def experiment_unit_name(self) -> str:
        return f"{self.experiment_id}_auxiliary"

    def __repr__(self, /) -> str:
        return f"<SlurmAuxiliaryUnit {self.experiment_unit_name}>"


class SlurmExperimentContextAnnotations:
    def __init__(
        self,
        experiment: "SlurmExperiment",
        *,
        title: str,
        tags: set[str] | None = None,
        description: str | None = None,
        note: str | None = None,
    ):
        self._experiment = experiment
        self._create_task = self._experiment._create_task
        self._title = title
        self._tags = UserSet(
            tags or set(),
            on_add=self._on_tag_added,
            on_remove=self._on_tag_removed,
            on_discard=self._on_tag_removed,
        )
        self._description = description or ""
        self._note = note or ""

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.ExperimentPatchModel(title=value),
        )

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.ExperimentPatchModel(description=value),
        )

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def note(self, value: str) -> None:
        self._note = value
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.ExperimentPatchModel(note=value),
        )

    @property
    def tags(self) -> MutableSet[str]:
        return self._tags

    @tags.setter
    def tags(self, tags: set[str]) -> None:
        # TODO(jfarebro): Create custom tag collection
        # and set it here, we need this so we can hook add and remove
        # to mutate the database transparently
        self._tags = UserSet(tags, on_add=self._on_tag_added, on_remove=self._on_tag_removed)
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.ExperimentPatchModel(tags=list(self._tags)),
        )

    def _on_tag_added(self, tag: str) -> None:
        del tag
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.ExperimentPatchModel(tags=list(self._tags)),
        )

    def _on_tag_removed(self, tag: str) -> None:
        del tag
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.ExperimentPatchModel(tags=list(self._tags)),
        )


class SlurmExperimentContextArtifacts(ContextArtifacts):
    def add_graphviz_config(self, config: str) -> None:
        self.add(Artifact(name="GRAPHVIZ", uri=f"graphviz://{config}"))

    def add_python_config(self, config: str) -> None:
        self.add(Artifact(name="PYTHON", uri=config))


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmExperimentMetadataContext:
    annotations: SlurmExperimentContextAnnotations
    artifacts: ContextArtifacts


class SlurmExperiment(xm.Experiment):
    _id: int
    _experiment_units: list[SlurmExperimentUnit]
    _experiment_context: SlurmExperimentMetadataContext
    _work_unit_count: int
    _async_packager = async_packager.AsyncPackager(router.package)

    def __init__(
        self,
        experiment_title: str,
        experiment_id: int,
    ) -> None:
        super().__init__()
        self._id = experiment_id
        self._experiment_units = []
        self._experiment_context = SlurmExperimentMetadataContext(
            annotations=SlurmExperimentContextAnnotations(
                experiment=self,
                title=experiment_title,
            ),
            artifacts=ContextArtifacts(self, artifacts=[]),
        )
        self._work_unit_count = 0

    @typing.overload
    def add(
        self,
        job: xm.AuxiliaryUnitJob,
        args: Mapping[str, Any] | None = ...,
        *,
        identity: str = "",
    ) -> asyncio.Future[SlurmExperimentUnit]: ...

    @typing.overload
    def add(
        self,
        job: xm.JobType,
        args: Mapping[str, Any] | None = ...,
        *,
        role: xm.WorkUnitRole = ...,
        identity: str = "",
    ) -> asyncio.Future[SlurmWorkUnit]: ...

    @typing.overload
    def add(
        self,
        job: xm.JobType,
        args: Mapping[str, Any] | None,
        *,
        role: xm.ExperimentUnitRole,
        identity: str = "",
    ) -> asyncio.Future[SlurmExperimentUnit]: ...

    @typing.overload
    def add(
        self,
        job: xm.JobType,
        args: Mapping[str, Any] | None = ...,
        *,
        role: xm.ExperimentUnitRole,
        identity: str = "",
    ) -> asyncio.Future[SlurmExperimentUnit]: ...

    @typing.overload
    def add(
        self,
        job: xm.Job | xm.JobGeneratorType,
        args: Sequence[Mapping[str, Any]],
        *,
        role: xm.WorkUnitRole = ...,
        identity: str = "",
    ) -> asyncio.Future[Sequence[SlurmWorkUnit]]: ...

    def add(
        self,
        job: xm.JobType,
        args: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
        *,
        role: xm.ExperimentUnitRole = xm.WorkUnitRole(),
        identity: str = "",
    ) -> (
        asyncio.Future[SlurmExperimentUnit]
        | asyncio.Future[SlurmWorkUnit]
        | asyncio.Future[Sequence[SlurmWorkUnit]]
    ):
        if isinstance(args, collections.abc.Sequence):
            if not isinstance(role, xm.WorkUnitRole):
                raise ValueError("Only `xm.WorkUnit`s are supported for job arrays.")
            if identity:
                raise ValueError(
                    "Cannot set an identity on the root add call. "
                    "Please use a job generator and set the identity within."
                )
            if isinstance(job, xm.JobGroup):
                raise ValueError(
                    "Job arrays over `xm.JobGroup`s aren't supported. "
                    "Slurm doesn't support job arrays over heterogeneous jobs. "
                    "Instead you should call `experiment.add` for each of these trials."
                )
            assert isinstance(job, xm.Job) or inspect.iscoroutinefunction(job), "Invalid job type"

            return asyncio.wrap_future(
                self._create_task(self._launch_job_array(job, args, role, identity))
            )
        else:
            return super().add(job, args, role=role, identity=identity)  # type: ignore

    async def _launch_job_array(
        self,
        job: xm.Job | xm.JobGeneratorType,
        args: Sequence[Mapping[str, Any]],
        role: xm.WorkUnitRole,
        identity: str = "",
    ) -> Sequence[SlurmWorkUnit]:
        global _current_job_array_queue

        # Create our job array queue and assign it to the current context
        job_array_queue = asyncio.Queue[tuple[xm.JobGroup, asyncio.Future]](maxsize=len(args))
        _current_job_array_queue.set(job_array_queue)

        # For each trial we'll schedule the job
        # and collect the futures
        wu_futures = []
        for trial in args:
            wu_futures.append(super().add(job, args=trial, role=role, identity=identity))

        # TODO(jfarebro): Set a timeout here
        # We'll wait until XManager has filled the queue.
        # There are two cases here, either we were given an xm.Job
        # in which case this will be trivial and filled immediately.
        # The other case is when you have a job generator and this is less
        # trivial, you have to wait for wu.add to be called.
        while not job_array_queue.full():
            await asyncio.sleep(0.1)

        # All jobs have been resolved
        executable, executor, name = None, None, None
        resolved_args, resolved_env_vars, resolved_futures = [], [], []
        while not job_array_queue.empty():
            # XManager automatically converts jobs to job groups so we must check
            # that there's only a single job in this job group
            job_group_view, future = job_array_queue.get_nowait()
            assert isinstance(job_group_view, xm.JobGroup), "Expected a job group from xm"
            _, job_view = job_group_view.jobs.popitem()

            if len(job_group_view.jobs) != 0 or not isinstance(job_view, xm.Job):
                raise ValueError("Only `xm.Job` is supported for job arrays. ")

            if executable is None:
                executable = job_view.executable
            if id(job_view.executable) != id(executable):
                raise RuntimeError("Found multiple executables in job array.")

            if executor is None:
                executor = job_view.executor
            if id(job_view.executor) != id(executor):
                raise RuntimeError("Found multiple executors in job array")

            if name is None:
                name = job_view.name
            if job_view.name != name:
                raise RuntimeError("Found multiple names in job array")

            resolved_args.append(
                set(xm.SequentialArgs.from_collection(job_view.args).to_dict().items())
            )
            resolved_env_vars.append(set(job_view.env_vars.items()))
            resolved_futures.append(future)
        assert executable is not None, "No executable found?"
        assert executor is not None, "No executor found?"

        common_args: set = functools.reduce(lambda a, b: a & b, resolved_args, set())
        common_env_vars: set = functools.reduce(lambda a, b: a & b, resolved_env_vars, set())

        sweep_args = [
            {
                "args": dict(a.difference(common_args)),
                "env_vars": dict(e.difference(common_env_vars)),
            }
            for a, e in zip(resolved_args, resolved_env_vars)
        ]

        # No support for sweep_env_vars right now.
        # We schedule the job array and then we'll resolve all the work units with
        # the handles Slurm gives back to us.
        try:
            handles = await execution.get_client().launch(
                job=xm.Job(
                    executable=executable,
                    executor=executor,
                    name=name,
                    args=dict(common_args),
                    env_vars=dict(common_env_vars),
                ),
                args=sweep_args,
                experiment_id=self.experiment_id,
                identity=identity,
            )
        except Exception as e:
            for future in resolved_futures:
                future.set_exception(e)
            raise
        else:
            for handle, future in zip(handles, resolved_futures):
                future.set_result(handle)

        wus = await asyncio.gather(*wu_futures)
        _current_job_array_queue.set(None)
        return wus

    def _create_experiment_unit(
        self,
        args: Mapping[str, Any],
        role: xm.ExperimentUnitRole,
        identity: str,
    ) -> Awaitable[SlurmWorkUnit]:
        del identity

        def _create_work_unit(role: xm.WorkUnitRole) -> Awaitable[SlurmWorkUnit]:
            work_unit = SlurmWorkUnit(
                self,
                self._create_task,
                args,
                role,
                self._work_unit_id_predictor,
            )
            self._experiment_units.append(work_unit)
            self._work_unit_count += 1

            future = asyncio.Future()
            future.set_result(work_unit)
            return future

        match role:
            case xm.WorkUnitRole():
                return _create_work_unit(role)
            case _:
                raise ValueError(f"Unsupported role {role}")

    def _get_experiment_unit(
        self,
        experiment_id: int,
        identity: str,
        role: xm.ExperimentUnitRole,
        args: Mapping[str, Any] | None = None,
    ) -> Awaitable[xm.ExperimentUnit]:
        del experiment_id, identity, role, args
        raise NotImplementedError

    def _should_reload_experiment_unit(self, role: xm.ExperimentUnitRole) -> bool:
        del role
        return False

    async def __aenter__(self) -> "SlurmExperiment":
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # If no work units were added, delete this experiment
        # This is to prevent empty experiments from being persisted
        # and cluttering the database.
        if self.work_unit_count == 0:
            console.print(
                f"[red]No work units were added to experiment `{self.experiment_title}`... deleting.[/red]"
            )
            api.client().delete_experiment(self.experiment_id)

        await super().__aexit__(exc_type, exc_value, traceback)

    @property
    def experiment_id(self) -> int:
        return self._id

    @property
    def experiment_title(self) -> str:
        return self.context.annotations.title

    @property
    def context(self) -> SlurmExperimentMetadataContext:
        return self._experiment_context

    @property
    def work_unit_count(self) -> int:
        return self._work_unit_count

    @property
    def work_units(self) -> Mapping[int, SlurmWorkUnit]:
        """Gets work units created via self.add()."""
        return {
            wu.work_unit_id: wu for wu in self._experiment_units if isinstance(wu, SlurmWorkUnit)
        }

    def __repr__(self, /) -> str:
        return f"<SlurmExperiment {self.experiment_id} {self.experiment_title}>"


def create_experiment(experiment_title: str) -> SlurmExperiment:
    """Create Experiment."""
    experiment_id = api.client().insert_experiment(api.ExperimentPatchModel(title=experiment_title))
    return SlurmExperiment(experiment_title=experiment_title, experiment_id=experiment_id)


def get_experiment(experiment_id: int) -> SlurmExperiment:
    """Get Experiment."""
    experiment_model = api.client().get_experiment(experiment_id)
    # TODO(jfarebro): Fill in jobs and work units and annotations
    return SlurmExperiment(experiment_title=experiment_model.title, experiment_id=experiment_id)


@functools.cache
def get_current_experiment() -> SlurmExperiment | None:
    if xid := os.environ.get("XM_SLURM_EXPERIMENT_ID"):
        return get_experiment(int(xid))
    return None


@functools.cache
def get_current_work_unit() -> SlurmWorkUnit | None:
    if (xid := os.environ.get("XM_SLURM_EXPERIMENT_ID")) and (
        wid := os.environ.get("XM_SLURM_WORK_UNIT_ID")
    ):
        experiment = get_experiment(int(xid))
        return experiment.work_units[int(wid)]
    return None
