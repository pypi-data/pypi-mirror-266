import dataclasses
import functools
from typing import Sequence

from absl import flags
from xmanager import xm

from xm_slurm.executables import Dockerfile, DockerImage, ImageURI, RemoteImage
from xm_slurm.executors import SlurmSpec
from xm_slurm.packaging import registry
from xm_slurm.packaging.docker.abc import DockerClient

FLAGS = flags.FLAGS
REMOTE_BUILD = flags.DEFINE_enum(
    "xm_builder", "local", ["local", "gcp", "azure"], "Remote build provider."
)

IndexedContainer = registry.IndexedContainer


@functools.cache
def docker_client() -> DockerClient:
    match REMOTE_BUILD.value:
        case "local":
            from xm_slurm.packaging.docker.local import LocalDockerClient

            return LocalDockerClient()
        case "gcp":
            from xm_slurm.packaging.docker.cloud import GoogleCloudRemoteDockerClient

            return GoogleCloudRemoteDockerClient()
        case "azure":
            raise NotImplementedError("Azure remote build is not yet supported.")
        case _:
            raise ValueError(f"Unknown remote build provider: {REMOTE_BUILD.value}")


@registry.register(Dockerfile)
def _(
    targets: Sequence[IndexedContainer[xm.Packageable]],
) -> list[IndexedContainer[RemoteImage]]:
    return docker_client().bake(targets=targets)


@registry.register(DockerImage)
def _(
    targets: Sequence[IndexedContainer[xm.Packageable]],
) -> list[IndexedContainer[RemoteImage]]:
    """Build Docker images, this is essentially a passthrough."""
    images = []
    client = docker_client()
    for target in targets:
        assert isinstance(target.value.executable_spec, DockerImage)
        assert isinstance(target.value.executor_spec, SlurmSpec)
        if target.value.executor_spec.tag is not None:
            raise ValueError(
                "Executable `DockerImage` should not be tagged via `SlurmSpec`. "
                "The image URI is provided by the `DockerImage` itself."
            )

        uri = ImageURI(target.value.executable_spec.image)
        images.append(
            dataclasses.replace(
                target,
                value=RemoteImage(  # type: ignore
                    image=str(uri),
                    workdir=target.value.executable_spec.workdir,
                    args=target.value.args,
                    env_vars=target.value.env_vars,
                    credentials=client.credentials(hostname=uri.domain),
                ),
            )
        )

    return images
