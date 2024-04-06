import copy
import datetime
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional, Tuple, Union

from mlflow.entities import Artifact, ArtifactType
from mlflow.entities import ArtifactVersion as _ArtifactVersion
from mlflow.tracking import MlflowClient

from mlfoundry.artifact.truefoundry_artifact_repo import (
    ArtifactIdentifier,
    MlFoundryArtifactsRepository,
)
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.log_types.artifacts.constants import INTERNAL_METADATA_PATH
from mlfoundry.log_types.artifacts.utils import (
    _get_mlflow_client,
    _validate_artifact_metadata,
    _validate_description,
    calculate_local_directory_size,
)
from mlfoundry.logger import logger
from mlfoundry.pydantic_v1 import BaseModel, Extra

# TODO: Add some progress indicators for upload and download
# TODO: Support async download and upload


class ArtifactPath(NamedTuple):
    src: str
    dest: str = None


class ArtifactVersionInternalMetadata(BaseModel):
    class Config:
        extra = Extra.allow

    files_dir: str  # relative to root


class ArtifactVersionDownloadInfo(BaseModel):
    download_dir: str
    content_dir: str


class ArtifactVersion:
    def __init__(self, artifact_version: _ArtifactVersion, artifact: Artifact) -> None:
        self._mlflow_client = _get_mlflow_client()
        self._artifact_version: _ArtifactVersion = artifact_version
        self._artifact: Artifact = artifact
        self._deleted = False
        self._description: str = ""
        self._metadata: Dict[str, Any] = {}
        self._set_mutable_attrs()

    @classmethod
    def from_fqn(cls, fqn: str) -> "ArtifactVersion":
        """
        Get the version of an Artifact to download contents or load them in memory

        Args:
            fqn (str): Fully qualified name of the artifact version.

        Returns:
            ArtifactVersion: An ArtifactVersion instance of the artifact

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_version = mlfoundry.ArtifactVersion.from_fqn(fqn="<artifact-fqn>")
            ```
        """
        mlflow_client = _get_mlflow_client()
        artifact_version = mlflow_client.get_artifact_version_by_fqn(fqn=fqn)
        artifact = mlflow_client.get_artifact_by_id(
            artifact_id=artifact_version.artifact_id
        )
        return cls(artifact_version=artifact_version, artifact=artifact)

    def _ensure_not_deleted(self):
        if self._deleted:
            raise MlFoundryException(
                "Artifact Version was deleted, cannot access a deleted version"
            )

    def _set_mutable_attrs(self, refetch=False):
        if refetch:
            self._artifact_version = self._mlflow_client.get_artifact_version_by_id(
                version_id=self._artifact_version.id
            )
        self._description = self._artifact_version.description or ""
        self._metadata = copy.deepcopy(self._artifact_version.artifact_metadata)

    def __repr__(self):
        return f"{self.__class__.__name__}(fqn={self.fqn!r})"

    def _get_artifacts_repo(self):
        return MlFoundryArtifactsRepository(
            artifact_identifier=ArtifactIdentifier(
                artifact_version_id=self._artifact_version.id
            ),
            mlflow_client=self._mlflow_client,
        )

    @property
    def name(self) -> str:
        """Get the name of the artifact"""
        return self._artifact.name

    @property
    def artifact_fqn(self) -> str:
        """Get fqn of the artifact"""
        return self._artifact.fqn

    @property
    def version(self) -> int:
        """Get version information of the artifact"""
        return self._artifact_version.version

    @property
    def fqn(self) -> str:
        """Get fqn of the current artifact version"""
        return self._artifact_version.fqn

    @property
    def step(self) -> int:
        """Get the step in which artifact was created"""
        return self._artifact_version.step

    @property
    def description(self) -> Optional[str]:
        """Get description of the artifact"""
        return self._description

    @description.setter
    def description(self, value: str):
        """set the description of the artifact"""
        _validate_description(value)
        self._description = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata for the current artifact"""
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """set the metadata for current artifact"""
        _validate_artifact_metadata(value)
        self._metadata = value

    @property
    def created_by(self) -> str:
        """Get the information about who created the artifact"""
        return self._artifact_version.created_by

    @property
    def created_at(self) -> datetime.datetime:
        """Get the time at which artifact was created"""
        return self._artifact_version.created_at

    @property
    def updated_at(self) -> datetime.datetime:
        """Get the information about the when the artifact was updated"""
        return self._artifact_version.updated_at

    def raw_download(
        self,
        path: Optional[Union[str, Path]],
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> str:
        """
        Download an artifact file or directory to a local directory if applicable, and return a
        local path for it.

        Args:
            path (str): Absolute path of the local filesystem destination directory to which to
                        download the specified artifacts. This directory must already exist.
                        If unspecified, the artifacts will either be downloaded to a new
                        uniquely-named directory on the local filesystem.
            overwrite (bool): If True it will overwrite the file if it is already present in the download directory else
                              it will throw an error
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            path:  Absolute path of the local filesystem location containing the desired artifacts.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.raw_download(path="<your-desired-download-path>")
            ```
        """
        logger.info(
            "Downloading artifact version contents, this might take a while ..."
        )
        artifacts_repo = self._get_artifacts_repo()
        return artifacts_repo.download_artifacts(
            artifact_path="", dst_path=path, overwrite=overwrite, progress=progress
        )

    def _download(
        self,
        path: Optional[Union[str, Path]],
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> Tuple[ArtifactVersionInternalMetadata, str]:
        self._ensure_not_deleted()
        download_dir = self.raw_download(
            path=path, overwrite=overwrite, progress=progress
        )
        internal_metadata_path = os.path.join(download_dir, INTERNAL_METADATA_PATH)
        if not os.path.exists(internal_metadata_path):
            raise MlFoundryException(
                f"Artifact version seems to be corrupted or in invalid format due to missing artifact metadata. "
                f"You can still use .raw_download(path='/your/path/here') to download and inspect files."
            )
        with open(internal_metadata_path) as f:
            internal_metadata = ArtifactVersionInternalMetadata.parse_obj(json.load(f))
        download_path = os.path.join(download_dir, internal_metadata.files_dir)
        return internal_metadata, download_path

    def download(
        self,
        path: Optional[Union[str, Path]] = None,
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> str:
        """
        Download an artifact file or directory to a local directory if applicable, and return a
        local path for it.

        Args:
            path (str): Absolute path of the local filesystem destination directory to which to
                        download the specified artifacts. This directory must already exist.
                        If unspecified, the artifacts will either be downloaded to a new
                        uniquely-named directory on the local filesystem or will be returned
                        directly in the case of the Local ArtifactRepository.
            overwrite (bool): If True it will overwrite the file if it is already present in the download directory else
                              it will throw an error
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            path:  Absolute path of the local filesystem location containing the desired artifacts.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.download(path="<your-desired-download-path>")
            ```
        """
        _, download_path = self._download(
            path=path, overwrite=overwrite, progress=progress
        )
        return download_path

    def delete(self) -> bool:
        """
        Deletes the current instance of the ArtifactVersion hence deleting the current version.

        Returns:
            True if artifact was deleted successfully

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.delete()
            ```
        """
        self._ensure_not_deleted()
        self._mlflow_client.delete_artifact_version(
            version_id=self._artifact_version.id
        )
        self._deleted = True
        return True

    def update(self):
        """
        Updates the current instance of the ArtifactVersion hence updating the current version.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.description = 'This is the new description'
            artifact_version.update()
            ```
        """
        self._ensure_not_deleted()

        self._artifact_version = self._mlflow_client.update_artifact_version(
            version_id=self._artifact_version.id,
            description=self.description,
            artifact_metadata=self.metadata,
        )
        self._set_mutable_attrs()


def _log_artifact_version_helper(
    run,
    name: str,
    artifact_type: ArtifactType,
    artifact_dir: tempfile.TemporaryDirectory,
    mlflow_client: Optional[MlflowClient] = None,
    ml_repo_id: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    step: int = 0,
    progress: Optional[bool] = None,
):
    if (run and mlflow_client) or (not run and not mlflow_client):
        raise MlFoundryException("Exactly one of run, mlflow_client should be passed")
    if mlflow_client and not ml_repo_id:
        raise MlFoundryException(
            "If mlflow_client is passed, ml_repo_id must also be passed"
        )
    if run:
        mlflow_client: MlflowClient = run.mlflow_client

    version_id = mlflow_client.create_artifact_version(
        experiment_id=int(run._experiment_id) if run else ml_repo_id,
        artifact_type=artifact_type,
        name=name,
    )
    artifacts_repo = MlFoundryArtifactsRepository(
        artifact_identifier=ArtifactIdentifier(artifact_version_id=version_id),
        mlflow_client=mlflow_client,
    )
    total_size = calculate_local_directory_size(artifact_dir)
    try:
        logger.info(
            "Packaging and uploading files to remote with Artifact Size: %.6f MB",
            total_size / 1000000.0,
        )
        artifacts_repo.log_artifacts(
            local_dir=artifact_dir.name, artifact_path=None, progress=progress
        )
    except Exception as e:
        mlflow_client.notify_failure_for_artifact_version(version_id=version_id)
        raise MlFoundryException("Failed to log Artifact") from e
    finally:
        artifact_dir.cleanup()
    artifact_version = mlflow_client.finalize_artifact_version(
        version_id=version_id,
        run_uuid=run.run_id if run else None,
        description=description,
        artifact_metadata=metadata,
        data_path=INTERNAL_METADATA_PATH,
        step=step,
        artifact_size=total_size,
    )

    return ArtifactVersion.from_fqn(fqn=artifact_version.fqn)
