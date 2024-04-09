import base64
import dataclasses
import enum
import json
import logging
import os
import pathlib
import shlex
import shutil
import subprocess
import tempfile
import typing
from typing import Sequence

from xmanager import xm

from xm_slurm.executables import (
    Dockerfile,
    ImageURI,
    RemoteImage,
    RemoteRepositoryCredentials,
)
from xm_slurm.executors import SlurmSpec
from xm_slurm.packaging import utils as packaging_utils
from xm_slurm.packaging.docker.abc import (
    DockerBakeCommand,
    DockerClient,
    DockerVersionCommand,
)
from xm_slurm.packaging.registry import IndexedContainer


class LocalDockerClient(DockerClient):
    """Build Docker images locally."""

    class Builder(enum.Enum):
        BUILDKIT = enum.auto()
        BUILDAH = enum.auto()

    def __init__(self):
        if "XM_DOCKER_CLIENT" in os.environ:
            client_call = shlex.split(os.environ["XM_DOCKER_CLIENT"])
        elif shutil.which("docker"):
            client_call = ["docker"]
        elif shutil.which("podman"):
            client_call = ["podman"]
        else:
            raise RuntimeError("No Docker client found.")
        self._client_call = client_call

        version_command = DockerVersionCommand()
        backend_version = packaging_utils.run_command(
            xm.merge_args(self._client_call, version_command.to_args()), return_stdout=True
        )
        if backend_version.stdout.startswith("github.com/docker/buildx"):
            self._builder = LocalDockerClient.Builder.BUILDKIT
        else:
            raise NotImplementedError(f"Unsupported Docker build backend: {backend_version}")

        self._credentials_cache: dict[str, RemoteRepositoryCredentials] = {}

    def credentials(self, hostname: str) -> RemoteRepositoryCredentials | None:
        """Fetch credentials from the local Docker configuration."""
        if hostname in self._credentials_cache:
            return self._credentials_cache[hostname]

        def _parse_docker_credentials(helper: str) -> RemoteRepositoryCredentials | None:
            """Parse credentials from a Docker credential helper."""
            if not shutil.which(f"docker-credential-{helper}"):
                return None
            returncode, output = subprocess.getstatusoutput(
                f"echo {hostname} | docker-credential-{helper} get",
            )

            if returncode == 0:
                credentials = json.loads(output)
                return RemoteRepositoryCredentials(
                    username=credentials["Username"], password=credentials["Secret"]
                )
            return None

        def _parse_credentials_from_config(
            config_path: pathlib.Path
        ) -> RemoteRepositoryCredentials | None:
            """Parse credentials from the Docker configuration file."""
            if not config_path.exists():
                return None
            config = json.loads(config_path.read_text())

            # Attempt to parse from the global credential store
            if (creds_store := config.get("credsStore", None)) and (
                credentials := _parse_docker_credentials(creds_store)
            ):
                self._credentials_cache[hostname] = credentials
                return credentials
            # Attempt to parse from the credential helper for this registry
            if creds_helper := config.get("credHelpers", {}):
                for registry, helper in creds_helper.items():
                    registry = ImageURI(registry)
                    if registry.domain == hostname and (
                        credentials := _parse_docker_credentials(helper)
                    ):
                        self._credentials_cache[hostname] = credentials
                        return credentials
            # Last resort: attempt to parse raw auth
            if auths := config.get("auths", None):
                for registry, metadata in auths.items():
                    registry = ImageURI(registry)
                    if registry.domain == hostname:
                        auth = base64.b64decode(metadata["auth"]).decode("utf-8")
                        username, password = auth.split(":")
                        credentials = RemoteRepositoryCredentials(username, password)
                        self._credentials_cache[hostname] = credentials
                        return credentials
            return None

        # Attempt to parse credentials from the Docker or Podman configuration
        match self._builder:
            case LocalDockerClient.Builder.BUILDKIT:
                docker_config_path = (
                    pathlib.Path(os.environ.get("DOCKER_CONFIG", "~/.docker")).expanduser()
                    / "config.json"
                )
                return _parse_credentials_from_config(docker_config_path)
            case LocalDockerClient.Builder.BUILDAH:
                podman_config_path = (
                    pathlib.Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
                    / "containers"
                    / "auth.json"
                )
                return _parse_credentials_from_config(podman_config_path)
            case _:
                return None

    def bake(
        self,
        *,
        targets: Sequence[IndexedContainer[xm.Packageable]],
    ) -> list[IndexedContainer[RemoteImage]]:
        executors_by_executables = packaging_utils.collect_executors_by_executable(targets)
        executors_by_executables = typing.cast(
            dict[Dockerfile, list[SlurmSpec]], executors_by_executables
        )

        with tempfile.TemporaryDirectory() as tempdir:
            hcl_file = pathlib.Path(tempdir) / "docker-bake.hcl"
            metadata_file = pathlib.Path(tempdir) / "metadata.json"

            # Write HCL and bake it
            hcl = self._bake_template.render(
                executables=executors_by_executables,
                hash=packaging_utils.hash_digest,
            )
            hcl_file.write_text(hcl)
            logging.debug(hcl)

            try:
                command = DockerBakeCommand(
                    targets=list(
                        set(
                            [
                                packaging_utils.hash_digest(target.value.executable_spec)
                                for target in targets
                            ]
                        )
                    ),
                    files=[hcl_file],
                    metadata_file=metadata_file,
                    pull=True,
                    push=True,
                )

                bake_command = xm.merge_args(self._client_call, command.to_args())
                packaging_utils.run_command(bake_command.to_list(), tty=True, check=True)
            except Exception as ex:
                raise RuntimeError(f"Failed to build Dockerfiles: {ex}") from ex
            else:
                metadata = json.loads(metadata_file.read_text())

        images = []
        for target in targets:
            assert isinstance(target.value.executable_spec, Dockerfile)
            assert isinstance(target.value.executor_spec, SlurmSpec)
            assert target.value.executor_spec.tag

            executable_metadata = metadata[
                packaging_utils.hash_digest(target.value.executable_spec)
            ]
            uri = ImageURI(target.value.executor_spec.tag).with_digest(
                executable_metadata["containerimage.digest"]
            )

            images.append(
                dataclasses.replace(
                    target,
                    value=RemoteImage(  # type: ignore
                        image=str(uri),
                        workdir=target.value.executable_spec.workdir,
                        args=target.value.args,
                        env_vars=target.value.env_vars,
                        credentials=self.credentials(uri.domain),
                    ),
                )
            )

        return images
