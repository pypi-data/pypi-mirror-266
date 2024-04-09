import dataclasses
import enum
import functools
import json
import pathlib
from typing import Literal, Mapping

import toml


class ContainerRuntime(enum.Enum):
    """The container engine to use."""

    SINGULARITY = enum.auto()
    APPTAINER = enum.auto()
    DOCKER = enum.auto()
    PODMAN = enum.auto()

    @classmethod
    def from_string(
        cls, runtime: Literal["singularity", "apptainer", "docker", "podman"]
    ) -> "ContainerRuntime":
        return {
            "singularity": cls.SINGULARITY,
            "apptainer": cls.APPTAINER,
            "docker": cls.DOCKER,
            "podman": cls.PODMAN,
        }[runtime]

    def __str__(self):
        if self is self.SINGULARITY:
            return "singularity"
        elif self is self.APPTAINER:
            return "apptainer"
        elif self is self.DOCKER:
            return "docker"
        elif self is self.PODMAN:
            return "podman"
        else:
            raise NotImplementedError


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is ContainerRuntime:
            return {"__type__": "ContainerRuntime", "value": str(obj)}
        return json.JSONEncoder.default(self, obj)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmClusterConfig:
    host: str
    user: str | None = None
    port: int | None = None

    # Job submission directory
    cwd: str | None = None

    # Additional scripting
    prolog: str | None = None
    epilog: str | None = None

    # Job scheduling
    account: str | None = None
    partition: str | None = None
    qos: str | None = None

    # If true, a reverse proxy is initiated via the submission host.
    proxy: Literal["submission-host"] | str | None = None

    runtime: ContainerRuntime

    # Environment variables
    environment: Mapping[str, str] = dataclasses.field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), cls=JSONEncoder)

    @classmethod
    def from_json(cls, json_str: str) -> "SlurmClusterConfig":
        def object_hook(tree):
            if "__type__" in tree and tree["__type__"] == "ContainerRuntime":
                return ContainerRuntime.from_string(tree["value"])
            return tree

        return cls(**json.loads(json_str, object_hook=object_hook))

    def __hash__(self):
        return hash((
            self.host,
            self.user,
            self.port,
            self.cwd,
            self.prolog,
            self.epilog,
            self.account,
            self.partition,
            self.qos,
            self.proxy,
            self.runtime,
            frozenset(self.environment.items()),
        ))


@functools.cache
def clusters(pyproject_path: pathlib.Path) -> list[SlurmClusterConfig]:
    if not pyproject_path.exists():
        raise RuntimeError(f"{pyproject_path} does not exist")

    with pyproject_path.open("r") as fp:
        config = functools.reduce(
            lambda d, key: d.get(key, {}),
            ["tool", "xmanager", "slurm"],
            toml.load(fp),
        )
        if not config:
            return []

        clusters = []
        for cluster in config.pop("clusters", []):
            cluster["runtime"] = ContainerRuntime.from_string(cluster["runtime"])
            clusters.append(SlurmClusterConfig(**config, **cluster))

        return clusters
