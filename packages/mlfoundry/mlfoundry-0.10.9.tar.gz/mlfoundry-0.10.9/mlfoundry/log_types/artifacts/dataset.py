import collections
import copy
import datetime
import tempfile
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

from mlflow.entities import Dataset as _Dataset

from mlfoundry.artifact.truefoundry_artifact_repo import (
    ArtifactIdentifier,
    MlFoundryArtifactsRepository,
)
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.log_types.artifacts.utils import (
    _copy_additional_files,
    _get_mlflow_client,
    _validate_artifact_metadata,
    _validate_description,
    calculate_local_directory_size,
)
from mlfoundry.logger import logger


class DataDirectoryPath(NamedTuple):
    src: str
    dest: str = None


class DataDirectory:
    def __init__(self, dataset: _Dataset) -> None:
        self._mlflow_client = _get_mlflow_client()
        self._dataset: _Dataset = dataset
        self._description: str = ""
        self._metadata: Dict[str, Any] = {}
        self._set_mutable_attrs()

    @classmethod
    def from_fqn(cls, fqn: str):
        """
        Get the DataDirectory to download contents or load them in memory

        Args:
            fqn (str): Fully qualified name of the data directory.

        Returns:
            DataDirectory: An DataDirectory instance of the artifact

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directory = mlfoundry.DataDirectory.from_fqn(fqn="<data_directory-fqn>")
            ```
        """
        mlflow_client = _get_mlflow_client()
        dataset = mlflow_client.get_dataset_by_fqn(fqn=fqn)
        return cls(dataset)

    def __repr__(self):
        return f"{self.__class__.__name__}(fqn={self.fqn!r})"

    def _set_mutable_attrs(self, refetch=False):
        if refetch:
            self._dataset = self._mlflow_client.get_dataset_by_fqn(
                fqn=self._dataset.fqn
            )
        self._description = self._dataset.description or ""
        self._metadata = copy.deepcopy(self._dataset.dataset_metadata)

    def _get_artifacts_repo(self):
        return MlFoundryArtifactsRepository(
            artifact_identifier=ArtifactIdentifier(dataset_fqn=self._dataset.fqn),
            mlflow_client=self._mlflow_client,
        )

    @property
    def name(self) -> str:
        """Get the name of the DataDirectory"""
        return self._dataset.name

    @property
    def fqn(self) -> str:
        """Get fqn of the DataDirectory"""
        return self._dataset.fqn

    @property
    def storage_root(self) -> str:
        """Get storage_root of the DataDirectory"""
        return self._dataset.storage_root

    @property
    def description(self) -> Optional[str]:
        """Get description of the DataDirectory"""
        return self._description

    @description.setter
    def description(self, value: str):
        """set the description of the DataDirectory"""
        _validate_description(value)
        self._description = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata for the current DataDirectory"""
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """set the metadata for current DataDirectory"""
        _validate_artifact_metadata(value)
        self._metadata = value

    @property
    def created_by(self) -> str:
        """Get the information about who created the DataDirectory"""
        return self._dataset.created_by

    @property
    def created_at(self) -> datetime.datetime:
        """Get the time at which DataDirectory was created"""
        return self._dataset.created_at

    @property
    def updated_at(self) -> datetime.datetime:
        """Get the information about the when the DataDirectory was updated"""
        return self._dataset.updated_at

    def add_files(
        self,
        file_paths: List[
            Union[Tuple[str], Tuple[str, Optional[str]], DataDirectoryPath]
        ],
    ) -> None:
        """Logs File in the `DataDirectory`.

        Args:
            file_paths (List[mlfoundry.DataDirectoryPath], optional): A list of pairs of (source path, destination path) to add files and folders to the DataDirectory contents. The first member of the pair should be a file or directory path and the second member should be the path inside the artifact contents to upload to.

                ```
                E.g. >>> data_directory.add_files(
                     ...     file_paths=[
                                mlfoundry.DataDirectoryPath("foo.txt", "foo/bar/foo.txt"),
                                mlfoundry.DataDirectoryPath("tokenizer/", "foo/tokenizer/"),
                                mlfoundry.DataDirectoryPath('bar.text'),
                                ('bar.txt', ),
                                ('foo.txt', 'a/foo.txt')
                             ]
                     ... )
                would result in
                .
                └── foo/
                    ├── bar/
                    │   └── foo.txt
                    └── tokenizer/
                        └── # contents of tokenizer/ directory will be uploaded here
                ```

        Examples:
            ```python
            import os
            import mlfoundry

            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            client = mlfoundry.get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<data_directory-fqn>")

            data_directory.add_files(
                file_paths=[mlfoundry.DataDirectoryPath('artifact.txt', 'a/b/')]
            )
            ```
        """
        for i, file_path in enumerate(file_paths):
            if isinstance(file_path, DataDirectoryPath):
                continue
            elif isinstance(file_path, collections.abc.Sequence) and (
                0 < len(file_path) <= 2
            ):
                file_paths[i] = DataDirectoryPath(*file_path)
            else:
                raise ValueError(
                    "`file_paths` should be an instance of `mlfoundry.DataDirectoryPath` or a tuple of (src, dest) path strings"
                )

        logger.info("Adding the files to data_directory, this might take a while ...")
        temp_dir = tempfile.TemporaryDirectory(prefix="truefoundry-")

        try:
            logger.info("Copying the files to add")
            _copy_additional_files(
                root_dir=temp_dir.name,
                files_dir="",
                model_dir=None,
                additional_files=file_paths,
            )

        except Exception as e:
            temp_dir.cleanup()
            raise MlFoundryException("Failed to Add Files to DataDirectory") from e

        artifacts_repo = self._get_artifacts_repo()
        total_size = calculate_local_directory_size(temp_dir)
        try:
            logger.info(
                "Packaging and uploading files to remote with Size: %.6f MB",
                total_size / 1000000.0,
            )
            artifacts_repo.log_artifacts(local_dir=temp_dir.name, artifact_path=None)
        except Exception as e:
            raise MlFoundryException("Failed to Add Files to DataDirectory") from e
        finally:
            temp_dir.cleanup()

    def list_files(
        self,
        path: Optional[str] = None,
    ):
        """
        List all the files and folders in the data_directory.

        Args:
            path: The path of directory in data_directory, from which the files are to be listed.

        Returns:
            str: Absolute path of the local filesystem location containing the desired files or folder.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<your-artifact-fqn>")
            files = data_directory.list_files()
            for file in files:
                print(file.path)
            ```
        """
        artifacts_repo = self._get_artifacts_repo()
        return artifacts_repo.list_artifacts(path=path)

    def download(
        self,
        download_path: Optional[str] = "",
        path: Optional[str] = None,
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ):
        """
        Download an file or directory to a local directory if applicable, and return a
        local path for it.

        Args:
            download_path: Relative source path to the desired files.
            path: Absolute path of the local filesystem destination directory to which to
                download the specified files. This directory must already exist.
                If unspecified, the files will either be downloaded to a new
                uniquely-named directory.
            overwrite: if to overwrite the files at/inside `dst_path` if they exist
            progress: value to show progress bar, defaults to None.

        Returns:
            str: Absolute path of the local filesystem location containing the desired files or folder.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<your-data_directory-fqn>")
            data_directory.download(download_path="<your-desired-download-path>")
            ```
        """
        artifacts_repo = self._get_artifacts_repo()
        return artifacts_repo.download_artifacts(
            artifact_path=download_path,
            dst_path=path,
            overwrite=overwrite,
            progress=progress,
        )

    def update(self):
        """
        Updates the current instance of the DataDirectory.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<your-artifact-fqn>")
            data_directory.description = 'This is the new description'
            data_directory.update()
            ```
        """

        self._dataset = self._mlflow_client.update_dataset(
            fqn=self._dataset.fqn,
            description=self.description,
            dataset_metadata=self.metadata,
        )
        self._set_mutable_attrs()
