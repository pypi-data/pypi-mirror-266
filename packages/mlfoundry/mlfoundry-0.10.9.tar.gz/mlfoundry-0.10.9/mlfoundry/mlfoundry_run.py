import functools
import os
import platform
import re
import time
import warnings
from pathlib import Path
from typing import (
    Any,
    Collection,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)
from urllib.parse import urljoin, urlsplit

import mlflow
from mlflow.entities import (
    ArtifactType,
    CustomMetric,
    Metric,
    ModelSchema,
    Param,
    Run,
    RunData,
    RunInfo,
    RunStatus,
    RunTag,
)
from mlflow.tracking import MlflowClient

from mlfoundry import constants, enums, version
from mlfoundry.exceptions import MlflowException, MlFoundryException
from mlfoundry.internal_namespace import NAMESPACE
from mlfoundry.log_types import Image, Plot
from mlfoundry.log_types.artifacts.artifact import ArtifactPath, ArtifactVersion
from mlfoundry.log_types.artifacts.general_artifact import _log_artifact_version
from mlfoundry.log_types.artifacts.model import ModelVersion, _log_model_version
from mlfoundry.logger import logger
from mlfoundry.metrics.v2 import ComputedMetrics
from mlfoundry.metrics.v2 import get_metrics_calculator as get_metrics_calculator_v2
from mlfoundry.run_utils import (
    ParamsType,
    flatten_dict,
    log_artifact_blob,
    process_params,
)
from mlfoundry.session import ACTIVE_RUNS


def _ensure_not_deleted(method):
    @functools.wraps(method)
    def _check_deleted_or_not(self, *args, **kwargs):
        if self._deleted:
            raise MlFoundryException(f"Run was deleted, cannot access a deleted Run")
        else:
            return method(self, *args, **kwargs)

    return _check_deleted_or_not


class MlFoundryRun:
    """MlFoundryRun."""

    VALID_PARAM_AND_METRIC_NAMES = re.compile(r"^[A-Za-z0-9_\-\. /]+$")

    def __init__(
        self,
        experiment_id: str,
        run_id: str,
        auto_end: bool = False,
        **kwargs,
    ):
        """__init__.

        Args:
            experiment_id (str): experiment_id
            run_id (str): run_id
            auto_end (bool): If to end the run at garbage collection or process end (atexit)
        """
        self._experiment_id = str(experiment_id)
        self._run_id = run_id
        self._auto_end = auto_end
        # TODO (chiragjn): mlflow_client be a protected/private member
        self.mlflow_client = MlflowClient()
        self._run_info: Optional[RunInfo] = None
        self._run_data: Optional[RunData] = None
        self._deleted = False
        self._terminate_called = False
        if self._auto_end:
            ACTIVE_RUNS.add_run(self)

    @classmethod
    def _get_run_from_mlflow_run(cls, mlflow_run: Run):
        """classmethod to get MLfoundry run from mlfow_run instance"""
        run = cls(mlflow_run.info.experiment_id, mlflow_run.info.run_id)
        run._run_info = mlflow_run.info
        run._run_data = mlflow_run.data
        return run

    def _get_run_info(self) -> RunInfo:
        if self._run_info is not None:
            return self._run_info

        self._run_info = self.mlflow_client.get_run(self.run_id).info
        return self._run_info

    @property
    @_ensure_not_deleted
    def run_id(self) -> str:
        """Get run_id for the current `run`"""
        return self._run_id

    @property
    @_ensure_not_deleted
    def run_name(self) -> str:
        """Get run_name for the current `run`"""
        return self._get_run_info().name

    @property
    @_ensure_not_deleted
    def fqn(self) -> str:
        """Get fqn for the current `run`"""
        return self._get_run_info().fqn

    @property
    @_ensure_not_deleted
    def status(self) -> str:
        """Get status for the current `run`"""
        return self.mlflow_client.get_run(self.run_id).info.status

    @property
    @_ensure_not_deleted
    def ml_repo(self) -> str:
        """Get ml_repo name of which the current `run` is part of"""
        return self.mlflow_client.get_experiment(self._experiment_id).name

    @property
    @_ensure_not_deleted
    def auto_end(self) -> bool:
        """Tells whether automatic end for `run` is True or False"""
        return self._auto_end

    @_ensure_not_deleted
    def __repr__(self) -> str:
        return f"<{type(self).__name__} at 0x{id(self):x}: run={self.fqn!r}>"

    @_ensure_not_deleted
    def __enter__(self):
        return self

    def _terminate_run_if_running(self, termination_status: RunStatus):
        """_terminate_run_if_running.

        Args:
            termination_status (RunStatus): termination_status
        """
        if self._terminate_called:
            return

        # Prevent double execution for termination
        self._terminate_called = True
        ACTIVE_RUNS.remove_run(self)

        current_status = self.status
        termination_status = RunStatus.to_string(termination_status)
        try:
            # we do not need to set any termination status unless the run was in RUNNING state
            if current_status != RunStatus.to_string(RunStatus.RUNNING):
                return
            logger.info("Setting run status of %r to %r", self.fqn, termination_status)
            self.mlflow_client.set_terminated(self.run_id, termination_status)
        except Exception as e:
            logger.warning(
                f"failed to set termination status {termination_status} due to {e}"
            )
        print(f"Finished run: {self.fqn!r}, Dashboard: {self.dashboard_link}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = RunStatus.FINISHED if exc_type is None else RunStatus.FAILED
        self._terminate_run_if_running(status)

    def __del__(self):
        if self._auto_end:
            self._terminate_run_if_running(RunStatus.FINISHED)

    @property
    @_ensure_not_deleted
    def dashboard_link(self) -> str:
        """Get Mlfoundry dashboard link for a `run`"""

        base_url = "{uri.scheme}://{uri.netloc}/".format(
            uri=urlsplit(mlflow.get_tracking_uri())
        )

        return urljoin(base_url, f"mlfoundry/{self._experiment_id}/run/{self.run_id}/")

    @_ensure_not_deleted
    def end(self, status: RunStatus = RunStatus.FINISHED):
        """End a `run`.

        This function marks the run as `FINISHED`.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )
            # ...
            # Model training code
            # ...
            run.end()
            ```

            In case the run was created using the context manager approach,
            We do not need to call this function.

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            with client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            ) as run:
                # ...
                # Model training code
                ...
            # `run` will be automatically marked as `FINISHED` or `FAILED`.
            ```
        """
        self._terminate_run_if_running(status)

    @_ensure_not_deleted
    def delete(self) -> None:
        """
        This function permanently delete the run

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            client.create_ml_repo('iris-learning')
            run = client.create_run(ml_repo="iris-learning", run_name="svm-model1")
            run.log_params({"learning_rate": 0.001})
            run.log_metrics({"accuracy": 0.7, "loss": 0.6})

            run.delete()
            ```

            In case we try to call or access any other function of that run after deleting
            then it will through MlfoundryException

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            client.create_ml_repo('iris-learning')
            run = client.create_run(ml_repo="iris-learning", run_name="svm-model1")
            run.log_params({"learning_rate": 0.001})
            run.log_metrics({"accuracy": 0.7, "loss": 0.6})

            run.delete()
            run.log_params({"learning_rate": 0.001})  # raises MlfoundryException
            ```
        """
        name = self.run_name
        try:
            self.mlflow_client.hard_delete_run(self.run_id)
            logger.info(f"Run {name} was deleted successfully")
            ACTIVE_RUNS.remove_run(self)
            self._deleted = True
            self._auto_end = False
        except Exception as ex:
            logger.warning(f"Failed to delete the run {name} because of {ex}")
            raise

    @_ensure_not_deleted
    def list_artifact_versions(
        self,
        artifact_type: Optional[List[ArtifactType]] = None,
    ) -> Iterator[ArtifactVersion]:
        """
        Get all the version of an artifact from a particular run to download contents or load them in memory

        Args:
            artifact_type: Type of the artifact you want

        Returns:
            Iterator[ArtifactVersion]: An iterator that yields non deleted artifact-versions
                of an artifact under a given run  sorted reverse by the version number

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(ml_repo="iris-learning", run_name="svm-model1")
            artifact_versions = run.list_artifact_versions()

            for artifact_version in artifact_versions:
                print(artifact_version)

            run.end()
            ```
        """
        page_token, done = None, False
        while not done:
            artifact_versions = self.mlflow_client.list_artifact_versions(
                run_ids=[self.run_id],
                artifact_types=artifact_type,
                page_token=page_token,
            )
            for artifact_version in artifact_versions:
                yield ArtifactVersion.from_fqn(artifact_version.fqn)
            done = page_token is None

    @_ensure_not_deleted
    def list_model_versions(
        self,
    ) -> Iterator[ModelVersion]:
        """
        Get all the version of a models from a particular run to download contents or load them in memory

        Returns:
            Iterator[ModelVersion]: An iterator that yields non deleted model-versions
                under a given run  sorted reverse by the version number

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.get_run(run_id="<your-run-id>")
            model_versions = run.list_model_versions()

            for model_version in model_versions:
                print(model_version)

            run.end()
            ```
        """
        page_token, done = None, False
        while not done:
            model_versions = self.mlflow_client.list_model_versions(
                page_token=page_token,
                run_ids=[self.run_id],
            )
            for model_version in model_versions:
                yield ModelVersion.from_fqn(fqn=model_version.model_fqn)
            done = page_token is None

    def _add_git_info(self, root_path: Optional[str] = None):
        """_add_git_info.

        Args:
            root_path (Optional[str]): root_path
        """
        root_path = root_path or os.getcwd()
        try:
            from mlfoundry.git_info import GitInfo

            git_info = GitInfo(root_path)
            tags = [
                RunTag(
                    key=constants.GIT_COMMIT_TAG_NAME,
                    value=git_info.current_commit_sha,
                ),
                RunTag(
                    key=constants.GIT_BRANCH_TAG_NAME,
                    value=git_info.current_branch_name,
                ),
                RunTag(key=constants.GIT_DIRTY_TAG_NAME, value=str(git_info.is_dirty)),
            ]
            remote_url = git_info.remote_url
            if remote_url is not None:
                tags.append(RunTag(key=constants.GIT_REMOTE_URL_NAME, value=remote_url))
            self.mlflow_client.log_batch(run_id=self.run_id, tags=tags)
            log_artifact_blob(
                mlflow_client=self.mlflow_client,
                run_id=self.run_id,
                blob=git_info.diff_patch,
                file_name=constants.PATCH_FILE_NAME,
                artifact_path=constants.PATCH_FILE_ARTIFACT_DIR,
            )
        except Exception as ex:
            # no-blocking
            logger.warning(f"failed to log git info because {ex}")

    def _add_python_mlf_version(self):
        python_version = platform.python_version()
        mlfoundry_version = version.__version__

        tags = [
            RunTag(
                key=constants.PYTHON_VERSION_TAG_NAME,
                value=python_version,
            ),
        ]

        if mlfoundry_version:
            tags.append(
                RunTag(
                    key=constants.MLFOUNDRY_VERSION_TAG_NAME,
                    value=mlfoundry_version,
                )
            )
        else:
            logger.warning("Failed to get MLFoundry version.")

        self.mlflow_client.log_batch(run_id=self.run_id, tags=tags)

    @_ensure_not_deleted
    def _download_artifact_deprecated(
        self, path: str, dest_path: Optional[str] = None
    ) -> str:
        """Downloads a logged `artifact` associated with the current `run`.

        Args:
            path (str): Source artifact path.
            dest_path (Optional[str], optional): Absolute path of the local destination
                directory. If a directory path is passed, the directory must already exist.
                If not passed, the artifact will be downloaded to a newly created directory
                in the local filesystem.

        Returns:
            str: Path of the directory where the artifact is downloaded.

        Examples:

            ```python
            import os
            import mlfoundry

            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )

            run.log_artifact(local_path="artifact.txt", artifact_path="my-artifacts")

            local_path = run.download_artifact(path="my-artifacts")
            print(f"Artifacts: {os.listdir(local_path)}")

            run.end()
            ```
        """
        if dest_path is None:
            return self.mlflow_client.download_artifacts(self.run_id, path=path)
        elif os.path.isdir(dest_path):
            return self.mlflow_client.download_artifacts(
                self.run_id, path=path, dst_path=dest_path
            )
        else:
            raise MlFoundryException(
                f"Destination path {dest_path} should be an existing directory."
            )

    @_ensure_not_deleted
    def _log_artifact_deprecated(
        self, local_path: str, artifact_path: Optional[str] = None
    ):
        """Logs an artifact for the current `run`.

        An `artifact` is a local file or directory. This function stores the `artifact`
        at the remote artifact storage.

        Args:
            local_path (str): Local path of the file or directory.
            artifact_path (Optional[str], optional): Relative destination path where
                the `artifact` will be stored. If not passed, the `artifact` is stored
                at the root path of the `run`'s artifact storage. The passed
                `artifact_path` should not start with `mlf/`, as `mlf/` directory is
                reserved for `mlfoundry`.

        Examples:

            ```python
            import os
            import mlfoundry

            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )

            run.log_artifact(local_path="artifact.txt", artifact_path="my-artifacts")

            run.end()
            ```
        """
        # TODO (chiragjn): this api is a little bit confusing, artifact_path is always considered to be a directory
        # which means passing local_path="a/b/c/d.txt", artifact_path="x/y/z.txt" will result in x/y/z.txt/d.txt

        if artifact_path is not None:
            NAMESPACE.validate_namespace_not_used(path=artifact_path)
        if os.path.isfile(local_path):
            _to = os.path.join(artifact_path or "", os.path.basename(local_path))
            logger.info(
                f"Logging {local_path!r} file as artifact to {_to!r}, this might take a while ..."
            )
            self.mlflow_client.log_artifact(
                self.run_id, local_path=local_path, artifact_path=artifact_path
            )
        elif os.path.isdir(local_path):
            _to = artifact_path or "/"
            logger.info(
                f"Logging contents of the {local_path!r} directory as artifacts to {_to!r}, this might take a while ..."
            )
            self.mlflow_client.log_artifacts(
                self.run_id, local_dir=local_path, artifact_path=artifact_path
            )
        else:
            raise MlFoundryException(
                f"local path {local_path} should be an existing file or directory"
            )

    @_ensure_not_deleted
    def log_artifact(
        self,
        name: str,
        artifact_paths: List[
            Union[Tuple[str], Tuple[str, Optional[str]], ArtifactPath]
        ],
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        step: Optional[int] = 0,
        progress: Optional[bool] = None,
    ) -> ArtifactVersion:
        """Logs an artifact for the current ML Repo.

        An `artifact` is a list of local files and directories.
        This function packs the mentioned files and directories in `artifact_paths`
        and uploads them to remote storage linked to the experiment

        Args:
            name (str): Name of the Artifact. If an artifact with this name already exists under the current ML Repo,
                the logged artifact will be added as a new version under that `name`.
                If no artifact exist with the given `name`, the given artifact will be logged as version 1.
            artifact_paths (List[mlfoundry.ArtifactPath], optional): A list of pairs
                of (source path, destination path) to add files and folders
                to the artifact version contents. The first member of the pair should be a file or directory path
                and the second member should be the path inside the artifact contents to upload to.

                ```
                E.g. >>> run.log_artifact(
                     ...     name="xyz",
                     ...     artifact_paths=[
                                mlfoundry.ArtifactPath("foo.txt", "foo/bar/foo.txt"),
                                mlfoundry.ArtifactPath("tokenizer/", "foo/tokenizer/"),
                                mlfoundry.ArtifactPath('bar.text'),
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
            description (Optional[str], optional): arbitrary text upto 1024 characters to store as description.
                This field can be updated at any time after logging. Defaults to `None`
            metadata (Optional[Dict[str, Any]], optional): arbitrary json serializable dictionary to store metadata.
                For example, you can use this to store metrics, params, notes.
                This field can be updated at any time after logging. Defaults to `None`
            step (int): step/iteration at which the vesion is being logged, defaults to 0.
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            mlfoundry.ArtifactVersion: an instance of `ArtifactVersion` that can be used to download the files,
            or update attributes like description, metadata.

        Examples:

            ```python
            import os
            import mlfoundry

            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )

            run.log_artifact(
                name="hello-world-file",
                artifact_paths=[mlfoundry.ArtifactPath('artifact.txt', 'a/b/')]
            )

            run.end()
            ```
        """
        if not artifact_paths:
            raise MlFoundryException(
                "artifact_paths cannot be empty, atleast one artifact_path must be passed"
            )

        return _log_artifact_version(
            self,
            name=name,
            artifact_paths=artifact_paths,
            description=description,
            metadata=metadata,
            step=step,
            progress=progress,
        )

    @_ensure_not_deleted
    def log_metrics(self, metric_dict: Dict[str, Union[int, float]], step: int = 0):
        """Log metrics for the current `run`.

        A metric is defined by a metric name (such as "training-loss") and a
        floating point or integral value (such as `1.2`). A metric is associated
        with a `step` which is the training iteration at which the metric was
        calculated.

        Args:
            metric_dict (Dict[str, Union[int, float]]): A metric name to metric value map.
                metric value should be either `float` or `int`. This should be
                a non-empty dictionary.
            step (int, optional): Training step/iteration at which the metrics
                present in `metric_dict` were calculated. If not passed, `0` is
                set as the `step`.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_metrics(metric_dict={"accuracy": 0.7, "loss": 0.6}, step=0)
            run.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4}, step=1)

            run.end()
            ```
        """
        try:
            # mlfow_client doesn't have log_metrics api, so we have to use log_batch,
            # This is what internally used by mlflow.log_metrics
            timestamp = int(time.time() * 1000)
            metrics_arr = []
            for key in metric_dict.keys():
                if isinstance(metric_dict[key], str):
                    logger.warning(
                        f"Cannot log metric with string value. Discarding metric {key}={metric_dict[key]}"
                    )
                    continue
                if not self.VALID_PARAM_AND_METRIC_NAMES.match(key):
                    logger.warning(
                        f"Invalid metric name: {key}. Names may only contain alphanumerics, "
                        f"underscores (_), dashes (-), periods (.), spaces ( ), and slashes (/). "
                        f"Discarding metric {key}={metric_dict[key]}"
                    )
                    continue
                metrics_arr.append(Metric(key, metric_dict[key], timestamp, step=step))

            if len(metrics_arr) == 0:
                logger.warning("Cannot log empty metrics dictionary")
                return

            self.mlflow_client.log_batch(
                run_id=self.run_id, metrics=metrics_arr, params=[], tags=[]
            )
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None

        logger.info("Metrics logged successfully")

    @_ensure_not_deleted
    def log_params(self, param_dict: ParamsType, flatten_params: bool = False):
        """Logs parameters for the run.

        Parameters or Hyperparameters can be thought of as configurations for a run.
        For example, the type of kernel used in a SVM model is a parameter.
        A Parameter is defined by a name and a string value. Parameters are
        also immutable, we cannot overwrite parameter value for a parameter
        name.

        Args:
            param_dict (ParamsType): A parameter name to parameter value map.
                Parameter values are converted to `str`.
            flatten_params (bool): Flatten hierarchical dict, e.g. `{'a': {'b': 'c'}} -> {'a.b': 'c'}`.
                All the keys will be converted to `str`. Defaults to False

        Examples:

            ### Logging parameters using a `dict`.

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_params({"learning_rate": 0.01, "epochs": 10})

            run.end()
            ```

            ### Logging parameters using `argparse` Namespace object

            ```python
            import argparse
            import mlfoundry

            parser = argparse.ArgumentParser()
            parser.add_argument("-batch_size", type=int, required=True)
            args = parser.parse_args()

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_params(args)
            ```
        """
        try:
            # mlfow client doesn't have log_params api, so we have to use log_batch,
            # This is what internally used by mlflow.log_params
            param_dict = process_params(param_dict)
            param_dict = flatten_dict(param_dict) if flatten_params else param_dict

            params_arr = []
            for param_key in param_dict.keys():
                if len(str(param_key)) > 250 or len(str(param_dict[param_key])) > 250:
                    logger.warning(
                        f"MlFoundry can't log parmeters with length greater than 250 characters. "
                        f"Discarding {param_key}:{param_dict[param_key]}."
                    )
                    continue
                if not self.VALID_PARAM_AND_METRIC_NAMES.match(param_key):
                    logger.warning(
                        f"Invalid param name: {param_key}. Names may only contain alphanumerics, "
                        f"underscores (_), dashes (-), periods (.), spaces ( ), and slashes (/). "
                        f"Discarding param {param_key}={param_dict[param_key]}"
                    )
                    continue
                params_arr.append(Param(param_key, str(param_dict[param_key])))

            if len(params_arr) == 0:
                logger.warning("Cannot log empty params dictionary")

            self.mlflow_client.log_batch(
                run_id=self.run_id, metrics=[], params=params_arr, tags=[]
            )
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None
        logger.info("Parameters logged successfully")

    @_ensure_not_deleted
    def set_tags(self, tags: Dict[str, str]):
        """Set tags for the current `run`.

        Tags are "labels" for a run. A tag is represented by a tag name and value.

        Args:
            tags (Dict[str, str]): A tag name to value map.
                Tag name cannot start with `mlf.`, `mlf.` prefix
                is reserved for mlfoundry. Tag values will be converted
                to `str`.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.set_tags({"nlp.framework": "Spark NLP"})

            run.end()
            ```
        """
        try:
            NAMESPACE.validate_namespace_not_used(names=tags.keys())
            tags_arr = [RunTag(key, str(value)) for key, value in tags.items()]
            self.mlflow_client.log_batch(
                run_id=self.run_id, metrics=[], params=[], tags=tags_arr
            )
        except MlflowException as e:
            raise MlFoundryException(e.message) from e
        logger.info("Tags set successfully")

    @_ensure_not_deleted
    def get_tags(self, no_cache=False) -> Dict[str, str]:
        """Returns all the tags set for the current `run`.

        Returns:
            Dict[str, str]: A dictionary containing tags. The keys in the dictionary
                are tag names and the values are corresponding tag values.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.set_tags({"nlp.framework": "Spark NLP"})
            print(run.get_tags())

            run.end()
            ```
        """
        if not no_cache and self._run_data:
            return self._run_data.tags

        run = self.mlflow_client.get_run(self.run_id)
        self._run_data = run.data
        return self._run_data.tags

    @_ensure_not_deleted
    def auto_log_metrics(
        self,
        model_type: enums.ModelType,
        data_slice: enums.DataSlice,
        predictions: Collection[Any],
        actuals: Optional[Collection[Any]] = None,
        class_names: Optional[List[str]] = None,
        prediction_probabilities=None,
    ) -> ComputedMetrics:
        """auto_log_metrics.

        Args:
            model_type (enums.ModelType): model_type
            data_slice (enums.DataSlice): data_slice
            predictions (Collection[Any]): predictions
            actuals (Optional[Collection[Any]]): actuals
            class_names (Optional[List[str]]): class_names
            prediction_probabilities:

        Returns:
            ComputedMetrics:
        """
        metrics_calculator = get_metrics_calculator_v2(model_type)
        metrics = metrics_calculator.compute_metrics(
            predictions=predictions,
            actuals=actuals,
            prediction_probabilities=prediction_probabilities,
            class_names=class_names,
        )
        metric_path = os.path.join(constants.ALM_ARTIFACT_PATH, data_slice.value)
        log_artifact_blob(
            mlflow_client=self.mlflow_client,
            run_id=self.run_id,
            blob=metrics.json(),
            file_name=constants.ALM_METRICS_FILE_NAME,
            artifact_path=metric_path,
        )
        return metrics

    @_ensure_not_deleted
    def get_metrics(
        self, metric_names: Optional[Iterable[str]] = None
    ) -> Dict[str, List[Metric]]:
        """Get metrics logged for the current `run` grouped by metric name.

        Args:
            metric_names (Optional[Iterable[str]], optional): A list of metric names
                For which the logged metrics will be fetched. If not passed, then all
                metrics logged under the `run` is returned.

        Returns:
            Dict[str, List[Metric]]: A dictionary containing metric name to list of metrics
                map.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )
            run.log_metrics(metric_dict={"accuracy": 0.7, "loss": 0.6}, step=0)
            run.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4}, step=1)

            metrics = run.get_metrics()
            for metric_name, metric_history in metrics.items():
                print(f"logged metrics for metric {metric_name}:")
                for metric in metric_history:
                    print(f"value: {metric.value}")
                    print(f"step: {metric.step}")
                    print(f"timestamp_ms: {metric.timestamp}")
                    print("--")

            run.end()
            ```
        """
        run = self.mlflow_client.get_run(self.run_id)
        run_metrics = run.data.metrics

        metric_names = (
            set(metric_names) if metric_names is not None else run_metrics.keys()
        )

        unknown_metrics = metric_names - run_metrics.keys()
        if len(unknown_metrics) > 0:
            logger.warning(f"{unknown_metrics} metrics not present in the run")
        metrics_dict = {metric_name: [] for metric_name in unknown_metrics}
        valid_metrics = metric_names - unknown_metrics
        for metric_name in valid_metrics:
            metrics_dict[metric_name] = self.mlflow_client.get_metric_history(
                self.run_id, metric_name
            )
        return metrics_dict

    @_ensure_not_deleted
    def get_params(self, no_cache=False) -> Dict[str, str]:
        """Get all the params logged for the current `run`.

        Returns:
            Dict[str, str]: A dictionary containing the parameters. The keys in the dictionary
                are parameter names and the values are corresponding parameter values.

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_params({"learning_rate": 0.01, "epochs": 10})
            print(run.get_params())

            run.end()
            ```
        """
        if not no_cache and self._run_data:
            return self._run_data.params

        run = self.mlflow_client.get_run(self.run_id)
        self._run_data = run.data
        return self._run_data.params

    @_ensure_not_deleted
    def log_model(
        self,
        *,
        name: str,
        model_file_or_folder: Optional[str] = None,
        framework: Optional[Union[enums.ModelFramework, str]],
        additional_files: Sequence[Tuple[Union[str, Path], Optional[str]]] = (),
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        model_schema: Optional[Union[Dict[str, Any], ModelSchema]] = None,
        custom_metrics: Optional[List[Union[Dict[str, Any], CustomMetric]]] = None,
        step: int = 0,
        progress: Optional[bool] = None,
        # Deprecated
        model: Optional[Any] = None,
        model_save_kwargs: Optional[Dict[str, Any]] = None,
    ) -> ModelVersion:
        # TODO (chiragjn): Document mapping of framework to list of valid model save kwargs
        # TODO (chiragjn): Add more examples
        """
        Serialize and log a versioned model under the current ML Repo. Each logged model generates a new version
            associated with the given `name` and linked to the current run. Multiple versions of the model can be
            logged as separate versions under the same `name`.

        Args:
            name (str): Name of the model. If a model with this name already exists under the current ML Repo,
                the logged model will be added as a new version under that `name`. If no models exist with the given
                `name`, the given model will be logged as version 1.
            model_file_or_folder (str): Path to either a single file or a folder containing model files. This folder
                is usually created using serialization methods of libraries or frameworks e.g. `joblib.dump`,
                `model.save_pretrained(...)`, `torch.save(...)`, `model.save(...)`
            framework (Union[enums.ModelFramework, str]): Model Framework. Ex:- pytorch, sklearn, tensorflow etc.
                The full list of supported frameworks can be found in `mlfoundry.enums.ModelFramework`.
                Can also be `None` when `model` is `None`.
            additional_files (Sequence[Tuple[Union[str, Path], Optional[str]]], optional): A list of pairs
                of (source path, destination path) to add additional files and folders
                to the model version contents. The first member of the pair should be a file or directory path
                and the second member should be the path inside the model versions contents to upload to.
                The model version contents are arranged like follows
                .
                └── model/
                    └── # model files are serialized here
                └── # any additional files and folders can be added here.

                You can also add additional files to model/ subdirectory by specifying the destination path as model/

                ```
                E.g. >>> run.log_model(
                     ...     name="xyz", model_file_or_folder="clf.joblib", framework="sklearn",
                     ...     additional_files=[("foo.txt", "foo/bar/foo.txt"), ("tokenizer/", "foo/tokenizer/")]
                     ... )
                would result in
                .
                ├── model/
                │   └── clf.joblib  # if `model_file_or_folder` is a folder, contents will be added here
                └── foo/
                    ├── bar/
                    │   └── foo.txt
                    └── tokenizer/
                        └── # contents of tokenizer/ directory will be uploaded here
                ```
            description (Optional[str], optional): arbitrary text upto 1024 characters to store as description.
                This field can be updated at any time after logging. Defaults to `None`
            metadata (Optional[Dict[str, Any]], optional): arbitrary json serializable dictionary to store metadata.
                For example, you can use this to store metrics, params, notes.
                This field can be updated at any time after logging. Defaults to `None`
            model_schema (Optional[Union[Dict[str, Any], ModelSchema]], optional): instance of `mlfoundry.ModelSchema`.
                This schema needs to be consistent with older versions of the model under the given `name` i.e.
                a feature's value type and model's prediction type cannot be changed in the schema of new version.
                Features can be removed or added between versions.
                ```
                E.g. if there exists a v1 with
                    schema = {"features": {"name": "feat1": "int"}, "prediction": "categorical"}, then

                    schema = {"features": {"name": "feat1": "string"}, "prediction": "categorical"} or
                    schema = {"features": {"name": "feat1": "int"}, "prediction": "numerical"}
                    are invalid because they change the types of existing features and prediction

                    while
                    schema = {"features": {"name": "feat1": "int", "feat2": "string"}, "prediction": "categorical"} or
                    schema = {"features": {"feat2": "string"}, "prediction": "categorical"}
                    are valid

                    This field can be updated at any time after logging. Defaults to None
                ```
            custom_metrics: (Optional[Union[List[Dict[str, Any]], CustomMetric]], optional): list of instances of
                `mlfoundry.CustomMetric`
                The custom metrics must be added according to the prediction type of schema.
                custom_metrics = [{
                    "name": "mean_square_error",
                    "type": "metric",
                    "value_type": "float"
                }]
            step (int): step/iteration at which the model is being logged, defaults to 0.
            progress (bool): value to show progress bar, defaults to None.
            model (Any): Deprecated. model instance of any one of the supported frameworks
                under `mlfoundry.enums.ModelFramework`. Can also be `None` which can be useful to
                create a reference entry without uploading any model files.
            model_save_kwargs (Optional[Dict[str, Any]], optional): Deprecated. keyword arguments to pass
                to model serializer.Defaults to `None`

        Returns:
            mlfoundry.ModelVersion: an instance of `ModelVersion` that can be used to download the files,
                load the model, or update attributes like description, metadata, schema.

        Examples:

            ### Sklearn

            ```python
            import mlfoundry
            from mlfoundry.enums import ModelFramework

            import joblib
            import numpy as np
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import StandardScaler
            from sklearn.svm import SVC

            X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
            y = np.array([1, 1, 2, 2])
            clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
            clf.fit(X, y)
            joblib.dump(clf, "sklearn-pipeline.joblib")

            client = mlfoundry.get_client()
            client.create_ml_repo(  # This is only required once
                ml_repo="my-classification-project",
                # This controls which bucket is used.
                # You can get this from Integrations > Blob Storage. `None` picks the default
                storage_integration_fqn=None
            )
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            model_version = run.log_model(
                name="my-sklearn-model",
                model_file_or_folder="sklearn-pipeline.joblib",
                framework=ModelFramework.SKLEARN,
                metadata={"accuracy": 0.99, "f1": 0.80},
                step=1,  # step number, useful when using iterative algorithms like SGD
            )
            print(model_version.fqn)
            ```

            ### Huggingface Transformers

            ```python
            import mlfoundry
            from mlfoundry.enums import ModelFramework

            import torch
            from transformers import AutoTokenizer, AutoConfig, pipeline, AutoModelForCausalLM
            pln = pipeline(
                "text-generation",
                model_file_or_folder="EleutherAI/pythia-70m",
                tokenizer="EleutherAI/pythia-70m",
                torch_dtype=torch.float16
            )
            pln.model.save_pretrained("my-transformers-model")
            pln.tokenizer.save_pretrained("my-transformers-model")

            client = mlfoundry.get_client()
            client.create_ml_repo(  # This is only required once
                ml_repo="my-llm-project",
                # This controls which bucket is used.
                # You can get this from Integrations > Blob Storage. `None` picks the default
                storage_integration_fqn=None
            )
            run = client.create_run(
                ml_repo="my-llm-project"
            )
            model_version = run.log_model(
                name="my-transformers-model",
                model_file_or_folder="my-transformers-model/",
                framework=ModelFramework.TRANSFORMERS
            )
            print(model_version.fqn)
            ```

        """
        if model or model_save_kwargs:
            deprecation_message = (
                "`model` and `model_save_kwargs` are deprecated and will be removed in a future release. "
                "Please use `model_file_or_folder` argument instead to pass an already serialized model"
            )
            warnings.warn(
                message=deprecation_message, category=DeprecationWarning, stacklevel=2
            )
            logger.warning(deprecation_message)
        model_version = _log_model_version(
            run=self,
            name=name,
            model_file_or_folder=model_file_or_folder,
            framework=framework,
            additional_files=additional_files,
            description=description,
            metadata=metadata,
            model_schema=model_schema,
            custom_metrics=custom_metrics,
            step=step,
            progress=progress,
            # Deprecated:
            model=model,
            model_save_kwargs=model_save_kwargs,
        )
        logger.info(f"Logged model successfully with fqn {model_version.fqn!r}")
        return model_version

    @_ensure_not_deleted
    def log_images(self, images: Dict[str, Image], step: int = 0):
        """Log images under the current `run` at the given `step`.

        Use this function to log images for a `run`. `PIL` package is needed to log images.
        To install the `PIL` package, run `pip install pillow`.

        Args:
            images (Dict[str, "mlfoundry.Image"]): A map of string image key to instance of
                `mlfoundry.Image` class. The image key should only contain alphanumeric,
                hyphens(-) or underscores(_). For a single key and step pair, we can log only
                one image.
            step (int, optional): Training step/iteration for which the `images` should be
                logged. Default is `0`.

        Examples:

            ### Logging images from different sources

            ```python
            import mlfoundry
            import numpy as np
            import PIL.Image

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project",
            )

            imarray = np.random.randint(low=0, high=256, size=(100, 100, 3))
            im = PIL.Image.fromarray(imarray.astype("uint8")).convert("RGB")
            im.save("result_image.jpeg")

            images_to_log = {
                "logged-image-array": mlfoundry.Image(data_or_path=imarray),
                "logged-pil-image": mlfoundry.Image(data_or_path=im),
                "logged-image-from-path": mlfoundry.Image(data_or_path="result_image.jpeg"),
            }

            run.log_images(images_to_log, step=1)
            run.end()
            ```
        """
        for key, image in images.items():
            if not isinstance(image, Image):
                raise MlFoundryException("image should be of type `mlfoundry.Image`")
            image.save(run=self, key=key, step=step)

    @_ensure_not_deleted
    def log_plots(
        self,
        plots: Dict[
            str,
            Union[
                "matplotlib.pyplot",
                "matplotlib.figure.Figure",
                "plotly.graph_objects.Figure",
                Plot,
            ],
        ],
        step: int = 0,
    ):
        """Log custom plots under the current `run` at the given `step`.

        Use this function to log custom matplotlib, plotly plots.

        Args:
            plots (Dict[str, "matplotlib.pyplot", "matplotlib.figure.Figure", "plotly.graph_objects.Figure", Plot]):
                A map of string plot key to the plot or figure object.
                The plot key should only contain alphanumeric, hyphens(-) or
                underscores(_). For a single key and step pair, we can log only
                one image.
            step (int, optional): Training step/iteration for which the `plots` should be
                logged. Default is `0`.


        Examples:

            ### Logging a plotly figure

            ```python
            import mlfoundry
            import plotly.express as px

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project",
            )

            df = px.data.tips()
            fig = px.histogram(
                df,
                x="total_bill",
                y="tip",
                color="sex",
                marginal="rug",
                hover_data=df.columns,
            )

            plots_to_log = {
                "distribution-plot": fig,
            }

            run.log_plots(plots_to_log, step=1)
            run.end()
            ```


            ### Logging a matplotlib plt or figure

            ```python
            import mlfoundry
            from matplotlib import pyplot as plt
            import numpy as np

            client = mlfoundry.get_client()
            run = client.create_run(
                ml_repo="my-classification-project",
            )

            t = np.arange(0.0, 5.0, 0.01)
            s = np.cos(2 * np.pi * t)
            (line,) = plt.plot(t, s, lw=2)

            plt.annotate(
                "local max",
                xy=(2, 1),
                xytext=(3, 1.5),
                arrowprops=dict(facecolor="black", shrink=0.05),
            )

            plt.ylim(-2, 2)

            plots_to_log = {"cos-plot": plt, "cos-plot-using-figure": plt.gcf()}

            run.log_plots(plots_to_log, step=1)
            run.end()
            ```
        """
        for key, plot in plots.items():
            plot = Plot(plot) if not isinstance(plot, Plot) else plot
            plot.save(run=self, key=key, step=step)
