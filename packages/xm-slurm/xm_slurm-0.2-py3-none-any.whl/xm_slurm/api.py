import dataclasses
import functools
import logging
import os
import time
import typing
from typing import Any

logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True, frozen=True)
class ExperimentPatchModel:
    title: str | None = None
    description: str | None = None
    note: str | None = None
    tags: list[str] | None = None


@dataclasses.dataclass(kw_only=True, frozen=True)
class SlurmJobModel:
    name: str
    slurm_job_id: int
    slurm_cluster: str


@dataclasses.dataclass(kw_only=True, frozen=True)
class ArtifactModel:
    name: str
    uri: str


@dataclasses.dataclass(kw_only=True, frozen=True)
class WorkUnitPatchModel:
    wid: int
    identity: str | None
    args: str | None = None


@dataclasses.dataclass(kw_only=True, frozen=True)
class WorkUnitModel(WorkUnitPatchModel):
    jobs: list[SlurmJobModel] = dataclasses.field(default_factory=list)
    artifacts: list[ArtifactModel] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(kw_only=True, frozen=True)
class ExperimentModel:
    title: str
    description: str | None
    note: str | None
    tags: list[str] | None

    work_units: list[WorkUnitModel]
    artifacts: list[ArtifactModel]


class XManagerAPI:
    def get_experiment(self, xid: int) -> ExperimentModel:
        del xid
        raise NotImplementedError("`get_experiment` is not implemented without a storage backend.")

    def delete_experiment(self, experiment_id: int) -> None:
        del experiment_id
        logger.debug("`delete_experiment` is not implemented without a storage backend.")

    def insert_experiment(self, experiment: ExperimentPatchModel) -> int:
        del experiment
        logger.debug("`insert_experiment` is not implemented without a storage backend.")
        return int(time.time() * 10**3)

    def update_experiment(self, experiment_id: int, experiment_patch: ExperimentPatchModel) -> None:
        del experiment_id, experiment_patch
        logger.debug("`update_experiment` is not implemented without a storage backend.")

    def insert_job(self, experiment_id: int, work_unit_id: int, job: SlurmJobModel) -> None:
        del experiment_id, work_unit_id, job
        logger.debug("`insert_job` is not implemented without a storage backend.")

    def insert_work_unit(self, experiment_id: int, work_unit: WorkUnitPatchModel) -> None:
        del experiment_id, work_unit
        logger.debug("`insert_work_unit` is not implemented without a storage backend.")

    def delete_work_unit_artifact(self, experiment_id: int, work_unit_id: int, name: str) -> None:
        del experiment_id, work_unit_id, name
        logger.debug("`delete_work_unit_artifact` is not implemented without a storage backend.")

    def insert_work_unit_artifact(
        self, experiment_id: int, work_unit_id: int, artifact: ArtifactModel
    ) -> None:
        del experiment_id, work_unit_id, artifact
        logger.debug("`insert_work_unit_artifact` is not implemented without a storage backend.")

    def delete_experiment_artifact(self, experiment_id: int, name: str) -> None:
        del experiment_id, name
        logger.debug("`delete_experiment_artifact` is not implemented without a storage backend.")

    def insert_experiment_artifact(self, experiment_id: int, artifact: ArtifactModel) -> None:
        del experiment_id, artifact
        logger.debug("`insert_experiment_artifact` is not implemented without a storage backend.")


class XManagerWebAPI(XManagerAPI):
    def __init__(self, base_url: str, token: str):
        from xm_slurm_api_client import AuthenticatedClient
        from xm_slurm_api_client import models as _models

        self.models = _models
        self.client = AuthenticatedClient(
            base_url,
            token=token,
            raise_on_unexpected_status=True,
            verify_ssl=False,
        )

    def get_experiment(self, xid: int) -> ExperimentModel:
        from xm_slurm_api_client.api.experiment import get_experiment as _get_experiment

        experiment: Any = _get_experiment.sync(xid, client=self.client)  # type: ignore
        wus = []
        for wu in experiment.work_units:
            jobs = []
            for job in wu.jobs:
                jobs.append(SlurmJobModel(**job.dict()))
            artifacts = []
            for artifact in wu.artifacts:
                artifacts.append(ArtifactModel(**artifact.dict()))
            wus.append(
                WorkUnitModel(
                    wid=wu.wid,
                    identity=wu.identity,
                    args=wu.args,
                    jobs=jobs,
                    artifacts=artifacts,
                )
            )

        artifacts = []
        for artifact in experiment.artifacts:
            artifacts.append(ArtifactModel(**artifact.dict()))

        return ExperimentModel(
            title=experiment.title,
            description=experiment.description,
            note=experiment.note,
            tags=experiment.tags,
            work_units=wus,
            artifacts=artifacts,
        )

    def delete_experiment(self, experiment_id: int) -> None:
        from xm_slurm_api_client.api.experiment import delete_experiment as _delete_experiment

        _delete_experiment.sync(experiment_id, client=self.client)

    def insert_experiment(self, experiment: ExperimentPatchModel) -> int:
        from xm_slurm_api_client.api.experiment import insert_experiment as _insert_experiment

        assert experiment.title is not None, "Title must be set in the experiment model."
        assert (
            experiment.description is None and experiment.note is None and experiment.tags is None
        ), "Only title should be set in the experiment model."
        experiment_response = _insert_experiment.sync(
            client=self.client,
            body=self.models.Experiment(title=experiment.title),
        )
        return typing.cast(int, experiment_response["xid"])  # type: ignore

    def update_experiment(self, experiment_id: int, experiment_patch: ExperimentPatchModel) -> None:
        from xm_slurm_api_client.api.experiment import update_experiment as _update_experiment

        m = self.models.ExperimentPatch(**dataclasses.asdict(experiment_patch))

        _update_experiment.sync(
            experiment_id,
            client=self.client,
            body=self.models.ExperimentPatch(**dataclasses.asdict(experiment_patch)),
        )

    def insert_job(self, experiment_id: int, work_unit_id: int, job: SlurmJobModel) -> None:
        from xm_slurm_api_client.api.job import insert_job as _insert_job

        _insert_job.sync(
            experiment_id,
            work_unit_id,
            client=self.client,
            body=self.models.SlurmJob(**dataclasses.asdict(job)),
        )

    def insert_work_unit(self, experiment_id: int, work_unit: WorkUnitPatchModel) -> None:
        from xm_slurm_api_client.api.work_unit import insert_work_unit as _insert_work_unit

        _insert_work_unit.sync(
            experiment_id,
            client=self.client,
            body=self.models.WorkUnit(**dataclasses.asdict(work_unit)),
        )

    def delete_work_unit_artifact(self, experiment_id: int, work_unit_id: int, name: str) -> None:
        from xm_slurm_api_client.api.artifact import (
            delete_work_unit_artifact as _delete_work_unit_artifact,
        )

        _delete_work_unit_artifact.sync(experiment_id, work_unit_id, name, client=self.client)

    def insert_work_unit_artifact(
        self, experiment_id: int, work_unit_id: int, artifact: ArtifactModel
    ) -> None:
        from xm_slurm_api_client.api.artifact import (
            insert_work_unit_artifact as _insert_work_unit_artifact,
        )

        _insert_work_unit_artifact.sync(
            experiment_id,
            work_unit_id,
            client=self.client,
            body=self.models.Artifact(**dataclasses.asdict(artifact)),
        )

    def delete_experiment_artifact(self, experiment_id: int, name: str) -> None: ...

    def insert_experiment_artifact(self, experiment_id: int, artifact: ArtifactModel) -> None:
        from xm_slurm_api_client.api.artifact import (
            insert_experiment_artifact as _insert_experiment_artifact,
        )

        _insert_experiment_artifact.sync(
            experiment_id,
            client=self.client,
            body=self.models.Artifact(**dataclasses.asdict(artifact)),
        )


@functools.cache
def client() -> XManagerAPI:
    try:
        import xm_slurm_api_client  # noqa: F401
    except ImportError:
        logger.debug("xm_slurm_api_client not found... skipping logging to the API.")
    else:
        if (base_url := os.environ.get("XM_SLURM_API_BASE_URL")) is not None and (
            token := os.environ.get("XM_SLURM_API_TOKEN")
        ) is not None:
            return XManagerWebAPI(base_url=base_url, token=token)
        else:
            logger.warn(
                "XM_SLURM_API_BASE_URL and XM_SLURM_API_TOKEN not set. "
                "Disabling XManager API client."
            )

    return XManagerAPI()
