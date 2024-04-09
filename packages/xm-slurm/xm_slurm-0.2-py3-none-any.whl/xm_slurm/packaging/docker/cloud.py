import dataclasses
import functools
import hashlib
import io
import os
import pathlib
import tarfile
import tempfile
import threading
import time
from typing import Mapping, Sequence

try:
    import google.api_core.exceptions
    import google.protobuf.duration_pb2
    import google_crc32c as crc32c
    import pathspec
    from google.cloud import iam_credentials, kms, storage
    from google.cloud import logging as cloud_logging
    from google.cloud.devtools import cloudbuild
    from google.cloud.logging_v2.services import logging_service_v2
    from google.logging.type import log_severity_pb2
except ImportError as ex:
    raise ImportError(
        "The `gcp` extra is required for the Google Cloud Builder. " "Install with `xm-slurm[gcp]`."
    ) from ex

import humanize
from xmanager import xm
from xmanager.cloud import auth

from xm_slurm import utils
from xm_slurm.console import console
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
    DockerLoginCommand,
    DockerPullCommand,
)
from xm_slurm.packaging.registry import IndexedContainer

_CLOUD_DOCKER_REGISTRY = "XM_SLURM_CLOUD_DOCKER_REGISTRY"
_CLOUD_DOCKER_USERNAME = "XM_SLURM_CLOUD_DOCKER_USERNAME"
_CLOUD_DOCKER_PASSWORD = "XM_SLURM_CLOUD_DOCKER_PASSWORD"

_GCP_BUILD_MACHINE = "XM_SLURM_GCP_BUILD_MACHINE"
_GCP_BUILD_TIMEOUT = "XM_SLURM_GCP_BUILD_TIMEOUT"


def _tar_writestr(tar: tarfile.TarFile, name: str, data: str):
    """Writes a string to a tar file."""
    info = tarfile.TarInfo(name)
    encoded = data.encode()
    info.size = len(encoded)
    tar.addfile(info, fileobj=io.BytesIO(encoded))


class GoogleCloudRemoteDockerClient(DockerClient):
    """A Docker client that uses Google Cloud Build to build and push images."""

    def __init__(self):
        self.cloud_credentials = auth.get_creds()
        self.cloud_project = auth.get_project_name()
        self.cloud_bucket = auth.get_bucket()
        self.cloud_service_account = auth.get_service_account()

        self.cloud_storage_client = storage.Client(
            project=self.cloud_project, credentials=self.cloud_credentials
        )
        self.cloud_build_client = cloudbuild.CloudBuildClient(credentials=self.cloud_credentials)
        self.cloud_logging_client = logging_service_v2.LoggingServiceV2Client(
            credentials=self.cloud_credentials
        )
        self.cloud_credentials_client = iam_credentials.IAMCredentialsClient(
            credentials=self.cloud_credentials
        )
        self.cloud_kms_client = kms.KeyManagementServiceClient(credentials=self.cloud_credentials)
        self._credentials_cache: dict[str, RemoteRepositoryCredentials] = {}

    def credentials(self, hostname: str) -> RemoteRepositoryCredentials | None:
        """Fetch access token for images in the Google Cloud Artifact Registry."""
        if (
            (username := os.environ.get(_CLOUD_DOCKER_USERNAME, None))
            and (password := os.environ.get(_CLOUD_DOCKER_PASSWORD, None))
            and (registry := os.environ.get(_CLOUD_DOCKER_REGISTRY, None))
            and hostname.endswith(registry)
        ):
            return RemoteRepositoryCredentials(username=username, password=password)
        elif not hostname.endswith("gcr.io"):
            return None
        elif hostname in self._credentials_cache:
            return self._credentials_cache[hostname]

        key = self.cloud_credentials_client.generate_access_token(
            iam_credentials.GenerateAccessTokenRequest(
                name=f"projects/-/serviceAccounts/{self.cloud_service_account}",
                lifetime=google.protobuf.duration_pb2.Duration(seconds=3600),
                scope=[
                    "https://www.googleapis.com/auth/devstorage.read_only",
                ],
            )
        )
        credentials = RemoteRepositoryCredentials(
            username="oauth2accesstoken", password=key.access_token
        )
        self._credentials_cache[hostname] = credentials

        return credentials

    def _upload_context_to_storage(
        self, archive_path: str | os.PathLike[str], destination_name: str | os.PathLike[str]
    ):
        """Uploads context archive to GCS."""
        bucket = self.cloud_storage_client.bucket(self.cloud_bucket)
        blob = bucket.blob(destination_name)
        blob.upload_from_filename(archive_path)

    def _encrypt_secret_env(
        self, secret_env: Mapping[str, str], *, key_id: str
    ) -> cloudbuild.Secret:
        """Encrypts the given secret environment using Cloud KMS."""

        key_location = f"projects/{self.cloud_project}/locations/global"
        key_ring_id = "xmanager"
        key_ring = f"{key_location}/keyRings/{key_ring_id}"
        key_name = f"{key_ring}/cryptoKeys/{key_id}"

        # Create the key ring and key if they don't exist
        try:
            self.cloud_kms_client.get_key_ring(kms.GetKeyRingRequest(name=key_ring))
        except google.api_core.exceptions.NotFound:
            self.cloud_kms_client.create_key_ring(
                kms.CreateKeyRingRequest(
                    parent=key_location,
                    key_ring_id=key_ring_id,
                    key_ring=kms.KeyRing(name=key_ring),
                )
            )

        try:
            self.cloud_kms_client.get_crypto_key(kms.GetCryptoKeyRequest(name=key_name))
        except google.api_core.exceptions.NotFound:
            self.cloud_kms_client.create_crypto_key(
                kms.CreateCryptoKeyRequest(
                    parent=key_ring,
                    crypto_key_id=key_id,
                    crypto_key=kms.CryptoKey(
                        purpose=kms.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT,
                    ),
                )
            )

        def _crc32c_digest(value: bytes) -> int:
            return int.from_bytes(crc32c.Checksum(value).digest(), "big")

        ciphers: dict[str, bytes] = {}
        for secret_name, secret in secret_env.items():
            secret_bytes = secret.encode("utf-8")
            response = self.cloud_kms_client.encrypt(
                kms.EncryptRequest(
                    name=key_name,
                    plaintext=secret_bytes,
                    plaintext_crc32c=_crc32c_digest(secret_bytes),
                )
            )

            if not response.verified_plaintext_crc32c:
                raise RuntimeError(
                    "The encryption request sent to the server was corrupted in-transit."
                )
            if not response.ciphertext_crc32c == _crc32c_digest(response.ciphertext):
                raise Exception(
                    "The encryption response received from the server was corrupted in-transit."
                )
            ciphers[secret_name] = response.ciphertext

        return cloudbuild.Secret(kms_key_name=key_name, secret_env=ciphers)

    def _make_build_request(
        self,
        targets: Sequence[IndexedContainer],
        context_path: str | os.PathLike[str],
    ) -> cloudbuild.CreateBuildRequest:
        """Creates a Cloud Build request to build the given targets."""
        bake_command = DockerBakeCommand(
            targets=[
                packaging_utils.hash_digest(target.value.executable_spec) for target in targets
            ],
            pull=False,
            push=False,
            load=True,
        )
        steps = [
            *[
                cloudbuild.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    args=DockerPullCommand(image=target.value.executor_spec.tag)
                    .to_args()
                    .to_list(),
                )
                for target in targets
            ],
            cloudbuild.BuildStep(
                name="gcr.io/cloud-builders/docker",
                args=bake_command.to_args().to_list(),
            ),
            # Delete the context archive on success
            cloudbuild.BuildStep(
                name="gcr.io/cloud-builders/gsutil",
                args=["rm", "-a", "-f", f"gs://{self.cloud_bucket}/{context_path}"],
                allow_failure=True,
            ),
        ]
        secrets: list[cloudbuild.Secret] = []

        if (
            (username := os.environ.get(_CLOUD_DOCKER_USERNAME, None))
            and (password := os.environ.get(_CLOUD_DOCKER_PASSWORD, None))
            and (registry := os.environ.get(_CLOUD_DOCKER_REGISTRY, None))
        ):
            login_command = DockerLoginCommand(
                server=registry, username="$$DOCKER_USERNAME", password="$$DOCKER_PASSWORD"
            )
            steps.insert(
                0,
                cloudbuild.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    args=["-c", f"docker {' '.join(login_command.to_args().to_list(escaper=str))}"],
                    entrypoint="bash",
                    secret_env=["DOCKER_USERNAME", "DOCKER_PASSWORD"],
                    allow_failure=False,
                ),
            )
            secrets += [
                self._encrypt_secret_env(
                    {"DOCKER_USERNAME": username}, key_id="dockerRegistryUsername"
                ),
                self._encrypt_secret_env(
                    {"DOCKER_PASSWORD": password}, key_id="dockerRegistryPassword"
                ),
            ]

        return cloudbuild.CreateBuildRequest(
            project_id=self.cloud_project,
            build=cloudbuild.Build(
                source=cloudbuild.Source(
                    storage_source=cloudbuild.StorageSource(
                        bucket=self.cloud_bucket,
                        object_=context_path,
                    )
                ),
                timeout=google.protobuf.duration_pb2.Duration(
                    seconds=int(os.environ.get(_GCP_BUILD_TIMEOUT, 1200))
                ),
                steps=steps,
                options=cloudbuild.BuildOptions(
                    machine_type=os.environ.get(
                        _GCP_BUILD_MACHINE, cloudbuild.BuildOptions.MachineType.UNSPECIFIED
                    ),
                ),
                images=list(
                    functools.reduce(
                        lambda tags, executor_spec: tags | {executor_spec.tag},
                        [target.value.executor_spec for target in targets],
                        set(),
                    )
                ),
                secrets=secrets,
            ),
        )

    def _tail_logs(self, build_id: str, stop_event: threading.Event):
        def request_generator():
            yield cloud_logging.types.TailLogEntriesRequest(
                resource_names=[f"projects/{self.cloud_project}"],
                filter=(
                    f'logName="projects/{self.cloud_project}/logs/cloudbuild" AND '
                    'resource.type="build" AND '
                    f'resource.labels.build_id="{build_id}"'
                ),
            )
            while not stop_event.is_set():
                time.sleep(0.1)

        stream = self.cloud_logging_client.tail_log_entries(request_generator())
        style_by_severity = {
            log_severity_pb2.DEFAULT: "",
            log_severity_pb2.DEBUG: "dim",
            log_severity_pb2.INFO: "bright_cyan",
            log_severity_pb2.NOTICE: "cyan",
            log_severity_pb2.WARNING: "yellow",
            log_severity_pb2.ERROR: "red",
            log_severity_pb2.CRITICAL: "bold red",
            log_severity_pb2.ALERT: "bold red",
            log_severity_pb2.EMERGENCY: "bold red",
        }

        for response in stream:
            for entry in response.entries:
                console.print(
                    f"[magenta][BUILD][/magenta] {entry.text_payload}",
                    style=style_by_severity.get(entry.severity, ""),  # type: ignore
                )

    def _wait_for_build(self, build_id: str, *, backoff: int = 5) -> dict[str, str]:
        """Waits for the given build to complete."""
        stop_logging_event = threading.Event()
        log_thread = threading.Thread(target=self._tail_logs, args=(build_id, stop_logging_event))
        log_thread.start()

        while True:
            time.sleep(backoff)
            result: cloudbuild.Build = self.cloud_build_client.get_build(
                request=cloudbuild.GetBuildRequest(id=build_id, project_id=self.cloud_project)
            )

            # Stop logging if the build is no longer running
            if result.status not in (
                cloudbuild.Build.Status.QUEUED,
                cloudbuild.Build.Status.WORKING,
            ):
                stop_logging_event.set()

            match result.status:
                case cloudbuild.Build.Status.SUCCESS:
                    return {image.name: image.digest for image in result.results.images}
                case cloudbuild.Build.Status.FAILURE:
                    console.log(
                        "Build FAILED. See logs for more information",
                        style="bold red",
                    )
                    raise RuntimeError("Build failed.")
                case cloudbuild.Build.Status.QUEUED | cloudbuild.Build.Status.WORKING:
                    continue
                case cloudbuild.Build.Status.CANCELLED:
                    console.log(
                        f"Cloud build tool internal error: {result.status}", style="bold red"
                    )
                    raise RuntimeError("Build cancelled.")
                case cloudbuild.Build.Status.INTERNAL_ERROR:
                    console.log(
                        f"Cloud build tool internal error: {result.status}", style="bold red"
                    )
                    raise RuntimeError("Build internal error.")
                case cloudbuild.Build.Status.TIMEOUT:
                    console.log("Build timed out after 1200 seconds.", style="bold red")
                    raise RuntimeError("Build timed out.")

    def _resolve_ignore_pathspec(
        self, path: pathlib.Path, *, ignore_files: Sequence[str] = [".gitignore", ".dockerignore"]
    ) -> pathspec.PathSpec:
        """Resolves the ignore list for the given context path."""

        def _maybe_add_ignore_file(patterns: list[str], ignore_file: str) -> list[str]:
            if (file := path / ignore_file).exists():
                patterns.extend(file.read_text().splitlines())
            return patterns

        ignore_patterns = functools.reduce(_maybe_add_ignore_file, ignore_files, [])
        return pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern,  # type: ignore
            ignore_patterns,
        )

    def _reroot_targets(
        self, targets: Sequence[IndexedContainer], source_path: pathlib.Path
    ) -> Sequence[IndexedContainer]:
        """Reroots the given targets to be relative to the given source path."""
        # We must re-root the targets as when we upload to GCS everything is relative to /
        rerooted_targets = []
        for target in targets:
            executable_spec: Dockerfile = target.value.executable_spec
            assert isinstance(executable_spec, Dockerfile)
            context_path = executable_spec.context.relative_to(source_path)
            executable_spec = dataclasses.replace(
                executable_spec,
                context=context_path,
                # dockerfile=context_path
                # / f"Dockerfile-{packaging_utils.hash_digest(executable_spec)}",
            )
            rerooted_targets.append(
                dataclasses.replace(
                    target,
                    value=xm.Packageable(
                        executable_spec=executable_spec,
                        executor_spec=target.value.executor_spec,
                        args=target.value.args,
                        env_vars=target.value.env_vars,
                    ),
                )
            )
        return rerooted_targets

    def bake(self, *, targets: Sequence[IndexedContainer]) -> list[IndexedContainer[RemoteImage]]:
        """Builds the given targets and returns the digest for each image."""
        # Step 1: Upload to GCS
        source_path = utils.find_project_root()
        # dockerfiles: dict[str, str] = {
        #     packaging_utils.hash_digest(
        #         target.value.executable_spec
        #     ): target.value.executable_spec.dockerfile.read_text()
        #     for target in targets
        # }
        targets = self._reroot_targets(targets, source_path)

        with tempfile.NamedTemporaryFile(suffix=".tar.gx") as tmpfile:
            console.print("Packaging context for upload...", style="blue")

            ignore_pathspec = self._resolve_ignore_pathspec(source_path)
            executors_by_executables = packaging_utils.collect_executors_by_executable(targets)
            with tarfile.open(tmpfile.name, "w:gz") as tar:
                for file in sorted(ignore_pathspec.match_tree_files(source_path, negate=True)):
                    file = pathlib.Path(file).resolve()
                    tar.add(file, file.relative_to(source_path))
                hcl = self._bake_template.render(
                    executables=executors_by_executables,
                    hash=packaging_utils.hash_digest,
                )
                _tar_writestr(tar, "docker-bake.hcl", hcl)
                # for executable_hash, dockerfile in dockerfiles.items():
                #     _tar_writestr(tar, f"Dockerfile-{executable_hash}", dockerfile)
            # with zipfile.ZipFile(tmpfile.name, "w", compression=zipfile.ZIP_DEFLATED) as zip:
            #     for file in sorted(ignore_pathspec.match_tree_files(source_path, negate=True)):
            #         file = pathlib.Path(file).resolve()
            #         zip.write(file, file.relative_to(source_path))
            #     hcl = self._bake_template.render(
            #         executables=executors_by_executables,
            #         hash=packaging_utils.hash_digest,
            #     )
            #     zip.writestr("docker-bake.hcl", hcl)
            #     for executable_hash, dockerfile in dockerfiles.items():
            #         zip.writestr(f"Dockerfile-{executable_hash}", dockerfile)

            archive_file_size = os.path.getsize(tmpfile.name)
            # Check file size of archive and warn if it's too large
            if archive_file_size > 1 * xm.GB:
                console.log(
                    "WARNING: Context archive is larger than 1GB. "
                    "This may cause slow builds. "
                    "Try to avoid storing datasets or large files in the source directory. "
                    "You may also ignore files by adding them to `.gitignore` or `.dockerignore`.",
                    style="bold yellow",
                )

            hasher = hashlib.blake2s()
            tmpfile.seek(0)
            for chunk in iter(lambda: tmpfile.read(4096), b""):
                hasher.update(chunk)
            destination_path = pathlib.Path(f"blake2s:{hasher.hexdigest()}").with_suffix(".tar.gz")

            console.print(
                f"Sending build context ({humanize.naturalsize(archive_file_size)}) to GCS...",
                style="blue",
            )
            self._upload_context_to_storage(tmpfile.name, destination_path.as_posix())

        # Step 2: Schedule build
        create_build_op = self.cloud_build_client.create_build(
            self._make_build_request(targets, destination_path.as_posix())
        )
        build_metadata: cloudbuild.BuildOperationMetadata = create_build_op.metadata  # type: ignore
        build_id = build_metadata.build.id
        build_url = create_build_op.metadata.build.log_url  # type: ignore
        console.print(f"Queued build with ID {build_id}...", style="blue")
        console.print(f"URL: [{build_url}]{build_url}", markup=True, style="blue")

        # Step 3: Wait for build completion for digests & collect credentials
        console.print("Waiting for build agent...", style="blue")
        digest_by_image_names = self._wait_for_build(build_id)

        # Step 4: Construct new remote images
        images = []
        for target in targets:
            assert isinstance(target.value.executable_spec, Dockerfile)
            assert isinstance(target.value.executor_spec, SlurmSpec)
            assert target.value.executor_spec.tag

            uri = ImageURI(target.value.executor_spec.tag).with_digest(
                digest_by_image_names[target.value.executor_spec.tag]
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
