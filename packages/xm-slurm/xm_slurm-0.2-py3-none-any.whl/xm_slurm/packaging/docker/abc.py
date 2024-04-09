import abc
import collections.abc
import dataclasses
import functools
import os
from typing import Literal, Mapping, Protocol, Sequence

import jinja2 as j2
from xmanager import xm

from xm_slurm.executables import RemoteImage, RemoteRepositoryCredentials
from xm_slurm.packaging.registry import IndexedContainer


class DockerCommandProtocol(Protocol):
    def to_args(self) -> xm.SequentialArgs: ...


@dataclasses.dataclass(frozen=True, kw_only=True)
class DockerBakeCommand(DockerCommandProtocol):
    targets: str | Sequence[str] | None = None
    builder: str | None = None
    files: str | os.PathLike[str] | Sequence[os.PathLike[str] | str] | None = None
    load: bool = False
    cache: bool = True
    print: bool = False
    pull: bool = False
    push: bool = False
    metadata_file: str | os.PathLike[str] | None = None
    progress: Literal["auto", "plain", "tty"] = "auto"
    set: Mapping[str, str] | None = None

    def to_args(self) -> xm.SequentialArgs:
        files = self.files
        if files is None:
            files = []
        if not isinstance(files, collections.abc.Sequence):
            files = [files]

        targets = self.targets
        if targets is None:
            targets = []
        elif not isinstance(targets, collections.abc.Sequence):
            targets = [targets]

        return xm.merge_args(
            ["buildx", "bake"],
            [f"--progress={self.progress}"],
            [f"--builder={self.builder}"] if self.builder else [],
            [f"--metadata-file={self.metadata_file}"] if self.metadata_file else [],
            ["--print"] if self.print else [],
            ["--push"] if self.push else [],
            ["--pull"] if self.pull else [],
            ["--load"] if self.load else [],
            ["--no-cache"] if not self.cache else [],
            [f"--file={file}" for file in files],
            [f"--set={key}={value}" for key, value in self.set.items()] if self.set else [],
            targets,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DockerPullCommand(DockerCommandProtocol):
    image: str

    def to_args(self) -> xm.SequentialArgs:
        return xm.merge_args(["pull", self.image])


@dataclasses.dataclass(frozen=True, kw_only=True)
class DockerLoginCommand(DockerCommandProtocol):
    server: str
    username: str
    password: str | None = None
    password_stdin: bool = False

    def __post_init__(self):
        if self.password is None and not self.password_stdin:
            raise ValueError("Either password or password_stdin must be set")
        if self.password is not None and self.password_stdin:
            raise ValueError("Only one of password or password_stdin must be set")

    def to_args(self) -> xm.SequentialArgs:
        return xm.merge_args(
            ["login", "--username", self.username],
            ["--password", self.password] if self.password else [],
            ["--password-stdin"] if self.password_stdin else [],
            [self.server],
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DockerVersionCommand(DockerCommandProtocol):
    def to_args(self) -> xm.SequentialArgs:
        return xm.merge_args(["buildx", "version"])


class DockerClient(abc.ABC):
    @functools.cached_property
    def _bake_template(self) -> j2.Template:
        template_loader = j2.PackageLoader("xm_slurm", "templates/docker")
        template_env = j2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=False)

        return template_env.get_template("docker-bake.hcl.j2")

    @abc.abstractmethod
    def credentials(self, *, hostname: str) -> RemoteRepositoryCredentials | None: ...

    @abc.abstractmethod
    def bake(
        self, *, targets: Sequence[IndexedContainer[xm.Packageable]]
    ) -> list[IndexedContainer[RemoteImage]]: ...
