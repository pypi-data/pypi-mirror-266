import enum
import itertools
import math
from typing import Mapping

import immutabledict


class ResourceType(enum.IntEnum):
    CPU = 1

    MEMORY = 2
    RAM = 2

    EPHEMERAL_STORAGE = 3
    DISK = 3

    GPU = 1000
    RTX8000 = 1001
    P4 = 1010
    P100 = 1011
    V100 = 1020
    A100 = 1030
    A100_80GIB = 1031
    A6000 = 1032
    H100 = 1040


AcceleratorType = set([
    ResourceType.P4,
    ResourceType.P100,
    ResourceType.V100,
    ResourceType.A100,
    ResourceType.A100_80GIB,
    ResourceType.A6000,
    ResourceType.H100,
    ResourceType.GPU
])


ResourceQuantity = int | float


class JobRequirements:
    replicas: int
    location: str | None
    accelerator: ResourceType | None

    def __init__(
        self,
        *,
        resources: Mapping[ResourceType | str, ResourceQuantity] = immutabledict.immutabledict(),
        replicas: int = 1,
        location: str | None = None,
        **kw_resources: ResourceQuantity,
    ):
        self.replicas = replicas or 1
        self.location = location
        self.accelerator = None

        self.task_requirements: dict[ResourceType | str, ResourceQuantity] = {}
        for resource_name, value in itertools.chain(resources.items(), kw_resources.items()):
            match resource_name:
                case str() if resource_name.upper() in ResourceType.__members__:
                    resource = ResourceType[resource_name.upper()]
                case ResourceType():
                    resource = resource_name
                case str():
                    resource = resource_name

            if resource in AcceleratorType or (isinstance(resource, str) and resource.startswith("gpu")):
                if self.accelerator is not None:
                    raise ValueError("Accelerator already set.")
                self.accelerator = resource

            if resource in self.task_requirements:
                raise ValueError(f"{resource} has been specified twice.")
            self.task_requirements[resource] = value

    def to_directives(self) -> list[str]:
        directives = []

        for resource, value in self.task_requirements.items():
            match resource:
                case ResourceType.EPHEMERAL_STORAGE | ResourceType.DISK:
                    assert isinstance(value, int), "Disk space must be an integer"
                    directives.append(f"--tmp={math.ceil(value / 2**20)}M")
                case ResourceType.MEMORY | ResourceType.RAM:
                    num_cpus = self.task_requirements.get(ResourceType.CPU, 1)
                    assert isinstance(value, (int, float)), "Memory must be an integer or float"
                    assert isinstance(num_cpus, int), "CPU must be an integer"
                    directives.append(f"--mem-per-cpu={math.ceil(value / num_cpus / 2**20)}M")
                case ResourceType.CPU:
                    assert isinstance(value, int), "CPU must be an integer"
                    directives.append(f"--cpus-per-task={value}")
                case ResourceType.GPU:
                    assert isinstance(value, int), "GPU must be an integer"
                    directives.append(f"--gpus-per-task={value}")
                case ResourceType() if resource in AcceleratorType:
                    assert isinstance(value, int), "Accelerator must be an integer"
                    directives.append(f"--gpus-per-task={resource.name.lower()}:{value}")
                case str():
                    directives.append(f"--gres={resource}:{value}")

        directives.append(f"--ntasks={self.replicas}")
        if self.location:
            directives.append(f"--nodelist={self.location}")

        return directives

    def replace(self, **kw_resources: ResourceQuantity) -> "JobRequirements":
        return JobRequirements(
            resources=self.task_requirements | kw_resources,  # type: ignore
            replicas=self.replicas,
        )

    def __repr__(self) -> str:
        args = []

        for resource, value in self.task_requirements.items():
            if isinstance(resource, ResourceType):
                resource = resource.name
            args.append(f"{resource.lower()}={value!r}")

        if self.replicas != 1:
            args.append(f"replicas={self.replicas}")

        return f'xm_slurm.JobRequirements({", ".join(args)})'
