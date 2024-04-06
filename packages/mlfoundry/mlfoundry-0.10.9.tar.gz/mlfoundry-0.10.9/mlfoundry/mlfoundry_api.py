"""
# TO independently test this module, you can run the example in the path
python examples/sklearn/iris_train.py

Besides running pytest
"""

from __future__ import annotations

import os
import uuid
import warnings
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union

import coolname
import mlflow
import pandas as pd
from mlflow.entities import Artifact, ArtifactType, CustomMetric, Model, ModelSchema
from mlflow.store.tracking import _SEARCH_MAX_RESULTS_DEFAULT
from mlflow.tracking import MlflowClient

from mlfoundry import constants, env_vars
from mlfoundry.enums import ModelFramework, ViewType
from mlfoundry.env_vars import TRACKING_HOST_GLOBAL
from mlfoundry.exceptions import MlflowException, MlFoundryException
from mlfoundry.internal_namespace import NAMESPACE
from mlfoundry.log_types.artifacts.artifact import ArtifactPath, ArtifactVersion
from mlfoundry.log_types.artifacts.dataset import DataDirectory
from mlfoundry.log_types.artifacts.general_artifact import _log_artifact_version
from mlfoundry.log_types.artifacts.model import ModelVersion, _log_model_version
from mlfoundry.logger import logger
from mlfoundry.mlfoundry_run import MlFoundryRun
from mlfoundry.monitoring.store import MonitoringClient
from mlfoundry.session import Session, get_active_session, init_session
from mlfoundry.tracking.servicefoundry_service import ServicefoundryService


def _get_internal_env_vars_values() -> Dict[str, str]:
    env = {}
    for env_var_name in env_vars.INTERNAL_ENV_VARS:
        value = os.getenv(env_var_name)
        if value:
            env[env_var_name] = value

    return env


def get_client() -> MlFoundry:
    """Initializes and returns the mlfoundry client.


    Returns:
        MlFoundry: Instance of `MlFoundry` class which represents a `run`.

    Examples:

        ### Get client
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        ```
    """
    session = None

    # NOTE: hack to run tests
    if os.getenv(TRACKING_HOST_GLOBAL, "").startswith("file:"):
        tracking_uri = os.getenv(TRACKING_HOST_GLOBAL)
        tracking_uri = os.path.join(tracking_uri, constants.MLRUNS_FOLDER_NAME)
        mlflow.set_tracking_uri(tracking_uri)
    else:
        session = init_session()

    return MlFoundry(session=session)


def _validate_ml_repo_name(
    ml_repo: str,
) -> str:
    if ml_repo == "" or (not isinstance(ml_repo, str)):
        raise MlFoundryException(
            f"ml_repo must be string type and not empty. "
            f"Got {type(ml_repo)} type with value {ml_repo!r}"
        )
    return ml_repo


def _resolve_version(version: Union[int, str]) -> int:
    if not isinstance(version, int) and not (
        isinstance(version, str) and version.isnumeric()
    ):
        raise MlFoundryException(
            f"version must be an integer or string containing numbers only. Got {version!r}"
        )
    final_version = int(version)
    if final_version <= 0:
        raise ValueError("version must be greater than 0")
    return final_version


class MlFoundry:
    """MlFoundry."""

    def __init__(self, session: Optional[Session] = None):
        """__init__.

        Args:
            session (Optional[Session], optional): Session instance to get auth credentials from
        """
        self.mlflow_client = MlflowClient()
        if session:
            self.monitoring_client = MonitoringClient(session=session)

    def _get_ml_repo_id(self, ml_repo: str) -> str:
        """_get_ml_repo_id.

        Args:
            ml_repo (str): The name of the ML Repo.

        Returns:
            str: The id of the ML Repo.
        """
        try:
            ml_repo_obj = self.mlflow_client.get_experiment_by_name(name=ml_repo)
        except MlflowException as e:
            err_msg = (
                f"Error happened in getting ML Repo based on name: "
                f"{ml_repo}. Error details: {e.message}"
            )
            raise MlFoundryException(err_msg) from e
        if not ml_repo_obj:
            err_msg = (
                f"ML Repo Does Not Exist for name: {ml_repo}. You may either "
                "create it from the dashboard or using client.create_ml_repo('<ml_repo_name>')"
            )
            raise MlFoundryException(err_msg)
        return ml_repo_obj.experiment_id

    def list_ml_repos(self) -> List[str]:
        """Returns a list of names of ML Repos accessible by the current user.

        Returns:
            List[str]: A list of names of ML Repos
        """
        try:
            ml_repos = self.mlflow_client.list_experiments(view_type=ViewType.ALL)
        except MlflowException as e:
            err_msg = f"Error happened in fetching ML Repos. Error details: {e.message}"
            raise MlFoundryException(err_msg) from e

        ml_repos_names = []
        for ml_repo in ml_repos:
            # ML Repo with experiment_id 0 represents default ML Repo which we are removing.
            if ml_repo.experiment_id != "0":
                ml_repos_names.append(ml_repo.name)

        return ml_repos_names

    def create_ml_repo(
        self,
        ml_repo: Optional[str] = None,
        storage_integration_fqn: Optional[str] = None,
    ):
        """Creates an ML Repository.

        Args:
            ml_repo (str, optional): The name of the Repository you want to create.
                if not given, it creates a name by itself.
            storage_integration_fqn(str, optional): The storage integration FQN to use for the experiment
                for saving artifacts.

        Examples:

            ### Create Repository
            ```python
            import mlfoundry

            client = mlfoundry.get_client()

            ml_repo = client.create_ml_repo(ml_repo="my-repo")
            ```
        """
        existing_ml_repo = self.mlflow_client.get_experiment_by_name(name=ml_repo)
        if not existing_ml_repo:  # ml_repo does not exist
            self.mlflow_client.get_experiment(
                experiment_id=self.mlflow_client.create_experiment(
                    name=ml_repo, storage_integration_fqn=storage_integration_fqn
                )
            )

        if storage_integration_fqn:
            session = get_active_session()
            servicefoundry_service = ServicefoundryService(
                tracking_uri=self.get_tracking_uri(),
                token=session.token.access_token,
            )

            try:
                existing_storage_integration = (
                    servicefoundry_service.get_integration_from_id(
                        existing_ml_repo.storage_integration_id
                    )
                )
            except Exception as e:
                raise MlFoundryException(
                    "Error in getting storage integration for ML Repo"
                ) from e

            if existing_storage_integration["fqn"] != storage_integration_fqn:
                raise MlFoundryException(
                    f"ML Repo with same name already exists with storage integration:"
                    f"{existing_storage_integration['fqn']}. Cannot update the storage integration to: "
                    f"{storage_integration_fqn}"
                )

    def create_run(
        self,
        ml_repo: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> MlFoundryRun:
        """Initialize a `run`.

        In a machine learning experiment `run` represents a single experiment
        conducted under a project.
        Args:
            ml_repo (str): The name of the project under which the run will be created.
                ml_repo should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
                The user must have `ADMIN` or `WRITE` access to this project.
            run_name (Optional[str], optional): The name of the run. If not passed, a randomly
                generated name is assigned to the run. Under a project, all runs should have
                a unique name. If the passed `run_name` is already used under a project, the
                `run_name` will be de-duplicated by adding a suffix.
                run name should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
            tags (Optional[Dict[str, Any]], optional): Optional tags to attach with
                this run. Tags are key-value pairs.
            kwargs:

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### Create a run under current user.
            ```python
            import mlfoundry

            client = mlfoundry.get_client()

            tags = {"model_type": "svm"}
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel", tags=tags
            )

            run.end()
            ```

            ### Creating a run using context manager.
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

            ### Create a run in a project owned by a different user.
            ```python
            import mlfoundry

            client = mlfoundry.get_client()

            tags = {"model_type": "svm"}
            run = client.create_run(
                ml_repo="my-classification-project",
                run_name="svm-with-rbf-kernel",
                tags=tags,
            )
            run.end()
            ```
        """
        if not run_name:
            run_name = coolname.generate_slug(2)
            logger.info(
                f"No run_name given. Using a randomly generated name {run_name}."
                " You can pass your own using the `run_name` argument"
            )
        ml_repo = _validate_ml_repo_name(ml_repo=ml_repo)

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)

        if tags is not None:
            NAMESPACE.validate_namespace_not_used(tags.keys())
        else:
            tags = {}

        tags.update(_get_internal_env_vars_values())
        run = self.mlflow_client.create_run(ml_repo_id, name=run_name, tags=tags)
        mlf_run_id = run.info.run_id

        kwargs.setdefault("auto_end", True)
        mlf_run = MlFoundryRun(experiment_id=ml_repo_id, run_id=mlf_run_id, **kwargs)
        # TODO(Rizwan): Revisit this once run lifecycle is formalised
        mlf_run._add_git_info()
        mlf_run._add_python_mlf_version()
        logger.info(f"Run {run.info.fqn!r} has started.")
        print(f"Link to the dashboard for the run: {mlf_run.dashboard_link}")
        return mlf_run

    def get_run_by_id(self, run_id: str) -> MlFoundryRun:
        """Get an existing `run` by the `run_id`.

        Args:
            run_id (str): run_id or fqn of an existing `run`.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### Get run by the run id
            ```python
            import mlfoundry

            client = mlfoundry.get_client()

            run = client.get_run_by_id(run_id='a8f6dafd70aa4baf9437a33c52d7ee90')
            ```
        """
        if run_id == "" or (not isinstance(run_id, str)):
            raise MlFoundryException(
                f"run_id must be string type and not empty. "
                f"Got {type(run_id)} type with value {run_id}"
            )
        if "/" in run_id:
            return self.get_run_by_fqn(run_id)

        run = self.mlflow_client.get_run(run_id)
        mlfoundry_run = MlFoundryRun._get_run_from_mlflow_run(run)
        print(f"Link to the dashboard for the run: {mlfoundry_run.dashboard_link}")
        return mlfoundry_run

    def get_run_by_fqn(self, run_fqn: str) -> MlFoundryRun:
        """Get an existing `run` by `fqn`.

        `fqn` stands for Fully Qualified Name. A run `fqn` has the following pattern:
        tenant_name/ml_repo/run_name

        If  a run `svm` under the project `cat-classifier` in `truefoundry` tenant,
        the `fqn` will be `truefoundry/cat-classifier/svm`.

        Args:
            run_fqn (str): `fqn` of an existing run.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### get run by run fqn
            ```python
            import mlfoundry

            client = mlfoundry.get_client()

            run = client.get_run_by_fqn(run_fqn='truefoundry/my-repo/svm')
            ```
        """
        run = self.mlflow_client.get_run_by_fqn(run_fqn)
        mlfoundry_run = MlFoundryRun._get_run_from_mlflow_run(run)
        print(f"Link to the dashboard for the run: {mlfoundry_run.dashboard_link}")
        return mlfoundry_run

    def get_run_by_name(
        self,
        ml_repo: str,
        run_name: str,
    ) -> MlFoundryRun:
        """Get an existing `run` by `run_name`.

        Args:
            ml_repo (str): name of the ml_repo of which the run is part of.
            run_name (str): the name of the run required

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### get run by name
            ```python
            import mlfoundry

            client = mlfoundry.get_client()

            run = client.get_run_by_name(run_name='svm', ml_repo='my-repo')
            ```
        """
        run = self.mlflow_client.get_run_by_name(
            experiment_id=None,
            run_name=run_name,
            experiment_name=ml_repo,
        )
        mlfoundry_run = MlFoundryRun._get_run_from_mlflow_run(run)
        print(f"Link to the dashboard for the run: {mlfoundry_run.dashboard_link}")
        return mlfoundry_run

    def get_all_runs(
        self,
        ml_repo: Optional[str] = None,
    ) -> pd.DataFrame:
        """Returns all the run name and id present under a project.

        The user must have `READ` access to the project.

        Args:
            ml_repo (str): Name of the project.
        Returns:
            pd.DataFrame: dataframe with two columns- run_id and run_name

        Examples:

            ### get all the runs from a ml_repo
            ```python
            import mlfoundry

            client = mlfoundry.get_client()

            run = client.get_all_runs(ml_repo='my-repo')
            ```
        """
        runs = []
        for run in self.search_runs(ml_repo=ml_repo):
            runs.append((run.run_id, run.run_name))

        if len(runs) == 0:
            return pd.DataFrame(
                columns=[constants.RUN_ID_COL_NAME, constants.RUN_NAME_COL_NAME]
            )

        return pd.DataFrame(
            runs, columns=[constants.RUN_ID_COL_NAME, constants.RUN_NAME_COL_NAME]
        )

    def search_runs(
        self,
        ml_repo: Optional[str] = None,
        filter_string: str = "",
        run_view_type: str = "ACTIVE_ONLY",
        order_by: Sequence[str] = ("attribute.start_time DESC",),
        job_run_name: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Iterator[MlFoundryRun]:
        """
        The user must have `READ` access to the project.
        Returns an iterator that returns a MLFoundryRun on each next call.
        All the runs under a project which matches the filter string and the run_view_type are returned.

        Args:
            ml_repo (str): Name of the project.
            filter_string (str, optional):
                Filter query string, defaults to searching all runs.
                Identifier required in the LHS of a search expression.
                Signifies an entity to compare against. An identifier has two parts separated by a period: the
                type of the entity and the name of the entity.
                The type of the entity is metrics, params, attributes, or tags.
                The entity name can contain alphanumeric characters and special characters.
                You can search using two run attributes : status and artifact_uri. Both attributes have string values.
                When a metric, parameter, or tag name contains a special character like hyphen, space, period,
                and so on, enclose the entity name in double quotes or backticks,
                params."model-type" or params.`model-type`

            run_view_type (str, optional): one of the following values "ACTIVE_ONLY", "DELETED_ONLY", or "ALL" runs.
            order_by (List[str], optional):
                List of columns to order by (e.g., "metrics.rmse"). Currently supported values
                are metric.key, parameter.key, tag.key, attribute.key. The ``order_by`` column
                can contain an optional ``DESC`` or ``ASC`` value. The default is ``ASC``.
                The default ordering is to sort by ``start_time DESC``.

            job_run_name (str): Name of the job which are associated with the runs to get that runs
            max_results (int): max_results on the total numbers of run yielded through filter

        Returns:
            Iterator[MlFoundryRun]: MLFoundryRuns matching the search query.

        Examples:

            ```python
            import mlfoundry as mlf

            client = mlf.get_client()
            with client.create_run(ml_repo="my-project", run_name="run-1") as run1:
                run1.log_metrics(metric_dict={"accuracy": 0.74, "loss": 0.6})
                run1.log_params({"model": "LogisticRegression", "lambda": "0.001"})

            with client.create_run(ml_repo="my-project", run_name="run-2") as run2:
                run2.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4})
                run2.log_params({"model": "SVM"})

            # Search for the subset of runs with logged accuracy metric greater than 0.75
            filter_string = "metrics.accuracy > 0.75"
            runs = client.search_runs(ml_repo="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7
            filter_string = "metrics.accuracy > 0.7"
            runs = client.search_runs(ml_repo="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7 and model="LogisticRegression"
            filter_string = "metrics.accuracy > 0.7 and params.model = 'LogisticRegression'"
            runs = client.search_runs(ml_repo="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7 and
            # order by accuracy in Descending order
            filter_string = "metrics.accuracy > 0.7"
            order_by = ["metric.accuracy DESC"]
            runs = client.search_runs(
                ml_repo="my-project", filter_string=filter_string, order_by=order_by
            )

            filter_string = "metrics.accuracy > 0.7"
            runs = client.search_runs(
                ml_repo="transformers", order_by=order_by ,job_run_name='job_run_name', filter_string=filter_string
            )

            order_by = ["metric.accuracy DESC"]
            runs = client.search_runs(
                ml_repo="my-project", filter_string=filter_string, order_by=order_by, max_results=10
            )
            ```
        """
        ml_repo = _validate_ml_repo_name(ml_repo=ml_repo)
        try:
            run_view_type = ViewType.from_string(run_view_type.lower())
        except Exception as e:
            raise MlFoundryException(e) from e

        try:
            ml_repo_obj = self.mlflow_client.get_experiment_by_name(ml_repo)
        except MlflowException as e:
            raise MlFoundryException(e) from e  # user doesnot have READ permission

        if ml_repo_obj is None:
            logger.warning(f"ML Repo with name {ml_repo} does not exist")
            return

        ml_repo_id = ml_repo_obj.experiment_id

        page_token = None
        done = False
        if job_run_name:
            if filter_string == "":
                filter_string = f"tags.TFY_INTERNAL_JOB_RUN_NAME = '{job_run_name}'"
            else:
                filter_string += (
                    f" and tags.TFY_INTERNAL_JOB_RUN_NAME = '{job_run_name}'"
                )
        while not done:
            all_runs = self.mlflow_client.search_runs(
                experiment_ids=[ml_repo_id],
                filter_string=filter_string,
                run_view_type=run_view_type,
                max_results=(
                    min(_SEARCH_MAX_RESULTS_DEFAULT, max_results)
                    if max_results
                    else _SEARCH_MAX_RESULTS_DEFAULT
                ),
                order_by=order_by,
                page_token=page_token,
            )
            page_token = all_runs.token
            for run in all_runs:
                if max_results is not None:
                    max_results -= 1
                yield MlFoundryRun._get_run_from_mlflow_run(run)
            done = page_token is None or max_results == 0

    @staticmethod
    def get_tracking_uri():
        """
        Get the current tracking URI.

        Returns:
            The tracking URI.

        Examples:

            ```python
            import tempfile
            import mlfoundry

            client = mlfoundry.get_client()
            tracking_uri = client.get_tracking_uri()
            print("Current tracking uri: {}".format(tracking_uri))
            ```
        """
        return mlflow.tracking.get_tracking_uri()

    def get_model_version(
        self,
        ml_repo: str,
        name: str,
        version: Union[str, int] = constants.LATEST_ARTIFACT_OR_MODEL_VERSION,
    ) -> Optional[ModelVersion]:
        """
        Get the model version to download contents or load it in memory

        Args:
            ml_repo (str): ML Repo to which model is logged
            name (str): Model Name
            version (str | int): Model Version to fetch (default is the latest version)

        Returns:
           ModelVersion: The ModelVersion instance of the model.

        Examples:

            ### Sklearn

            ```python
            # See `mlfoundry.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import tempfile
            import joblib
            import mlfoundry

            client = mlfoundry.get_client()
            model_version = client.get_model_version(
                ml_repo="my-classification-project",
                name="my-sklearn-model",
                version=1
            )

            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir, download_info.model_filename)

            # Deserialize and Load
            model = joblib.load(
                os.path.join(download_info.model_dir, download_info.model_filename)
            )
            ```

            ### Huggingface Transformers

            ```python
            # See `mlfoundry.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import torch
            from transformers import pipeline

            import mlfoundry

            client = mlfoundry.get_client()
            model_version = client.get_model_version(
                ml_repo="my-llm-project",
                name="my-transformers-model",
                version=1
            )

            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir)

            # Deserialize and Load
            pln = pipeline("text-generation", model=download_info.model_dir, torch_dtype=torch.float16)
            ```
        """
        resolved_version = None
        if version != constants.LATEST_ARTIFACT_OR_MODEL_VERSION:
            resolved_version = _resolve_version(version=version)

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        model_version = self.mlflow_client.get_model_version(
            experiment_id=int(ml_repo_id),
            model_name=name,
            version=resolved_version,
        )
        model = self.mlflow_client.get_model_by_id(model_id=model_version.model_id)
        return ModelVersion(
            model_version=model_version,
            model=model,
        )

    def get_model_version_by_fqn(self, fqn: str) -> ModelVersion:
        """
        Get the model version to download contents or load it in memory

        Args:
            fqn (str): Fully qualified name of the model version.

        Returns:
            ModelVersion: The ModelVersion instance of the model.

        Examples:

            ### Sklearn

            ```python
            # See `mlfoundry.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import tempfile
            import joblib
            import mlfoundry

            client = mlfoundry.get_client()
            model_version = client.get_model_version_by_fqn(
                fqn="model:truefoundry/my-classification-project/my-sklearn-model:1"
            )

            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir, download_info.model_filename)

            # Deserialize and Load
            model = joblib.load(
                os.path.join(download_info.model_dir, download_info.model_filename)
            )
            ```

            ### Huggingface Transformers

            ```python
            # See `mlfoundry.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import torch
            from transformers import pipeline

            import mlfoundry

            client = mlfoundry.get_client()
            model_version = client.get_model_version_by_fqn(
                fqn="model:truefoundry/my-llm-project/my-transformers-model:1"
            )
            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir)

            # Deserialize and Load
            pln = pipeline("text-generation", model=download_info.model_dir, torch_dtype=torch.float16)
            ```

        """
        return ModelVersion.from_fqn(fqn=fqn)

    def list_model_versions(self, ml_repo: str, name: str) -> Iterator[ModelVersion]:
        """
        Get all the version of a model to download contents or load them in memory

        Args:
            ml_repo (str): Repository in which the model is stored.
            name (str): Name of the model whose version is required

        Returns:
            Iterator[ModelVersion]: An iterator that yields non deleted model versions
                of a model under a given ml_repo  sorted reverse by the version number

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            model_versions = client.list_model_version(ml_repo="my-repo", name="svm")

            for model_version in model_versions:
                print(model_version)
            ```
        """
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        models = self.mlflow_client.list_models(ml_repo_id=ml_repo_id, name=name)
        if not models or len(models) == 0:
            err_msg = f"Model Does Not Exist for ml_repo={ml_repo}, name={name}"
            raise MlFoundryException(err_msg)
        return self._list_model_versions_by_id(model=models[0])

    def list_model_versions_by_fqn(self, model_fqn: str) -> Iterator[ModelVersion]:
        """
        List versions for a given model

        Args:
            model_fqn: FQN of the Model to list versions for.
                A model_fqn looks like `model:{org}/{user}/{project}/{artifact_name}`
                or `model:{user}/{project}/{artifact_name}`

        Returns:
            Iterator[ModelVersion]: An iterator that yields non deleted model versions
                under the given model_fqn sorted reverse by the version number

        Yields:
            ModelVersion: An instance of `mlfoundry.ModelVersion`

        Examples:

            ```python
            import mlfoundry

            mlfoundry.login(tracking_uri="https://your.truefoundry.site.com")
            client = mlfoundry.get_client()
            model_fqn = "model:org/my-project/my-model"
            for mv in client.list_model_versions(model_fqn=model_fqn):
                print(mv.name, mv.version, mv.description)
            ```
        """
        model = self.mlflow_client.get_model_by_fqn(fqn=model_fqn)
        return self._list_model_versions_by_id(model=model)

    def _list_model_versions_by_id(
        self, model_id: Optional[uuid.UUID] = None, model: Model = None
    ) -> Iterator[ModelVersion]:
        if model and not model_id:
            model_id = model.id
        elif not model and model_id:
            model = self.mlflow_client.get_model_by_id(model_id=model_id)
        else:
            raise MlFoundryException(
                "Exactly one of model_id or model should be passed"
            )

        max_results, page_token, done = 10, None, False
        while not done:
            model_versions = self.mlflow_client.list_model_versions(
                model_id=model_id, max_results=max_results, page_token=page_token
            )
            page_token = model_versions.token
            for model_version in model_versions:
                yield ModelVersion(model_version=model_version, model=model)
            if not model_versions or not page_token:
                done = True

    def get_artifact_version(
        self,
        ml_repo: str,
        artifact_name: str,
        artifact_type: Optional[ArtifactType] = ArtifactType.ARTIFACT,
        version: Union[str, int] = constants.LATEST_ARTIFACT_OR_MODEL_VERSION,
    ) -> Optional[ArtifactVersion]:
        """
        Get the model version to download contents or load it in memory

        Args:
            ml_repo (str): ML Repo to which artifact is logged
            artifact_name (str): Artifact Name
            artifact_type (str): The type of artifact to fetch (acceptable values: "artifact", "model", "plot", "image")
            version (str | int): Artifact Version to fetch (default is the latest version)

        Returns:
            ArtifactVersion : An ArtifactVersion instance of the artifact

        Examples:

            ```python
            import tempfile
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_version = client.get_artifact_version(ml_repo="ml-repo-name", name="artifact-name", version=1)

            # download the artifact to disk
            temp = tempfile.TemporaryDirectory()
            download_path = artifact_version.download(path=temp.name)
            print(download_path)
            ```
        """
        resolved_version = None
        if version != constants.LATEST_ARTIFACT_OR_MODEL_VERSION:
            resolved_version = _resolve_version(version=version)

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)

        artifact_version = self.mlflow_client.get_artifact_version(
            experiment_id=int(ml_repo_id),
            artifact_name=artifact_name,
            artifact_type=artifact_type,
            version=resolved_version,
        )
        artifact = self.mlflow_client.get_artifact_by_id(
            artifact_id=artifact_version.artifact_id,
        )
        return ArtifactVersion(
            artifact_version=artifact_version,
            artifact=artifact,
        )

    def get_artifact_version_by_fqn(self, fqn: str) -> ArtifactVersion:
        """
        Get the artifact version to download contents

        Args:
            fqn (str): Fully qualified name of the artifact version.

        Returns:
            ArtifactVersion : An ArtifactVersion instance of the artifact

        Examples:

            ```python
            import tempfile
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_version = client.get_artifact_version_by_fqn(
                fqn="artifact:truefoundry/my-classification-project/sklearn-artifact:1"
            )

            # download the artifact to disk
            temp = tempfile.TemporaryDirectory()
            download_path = artifact_version.download(path=temp.name)
            print(download_path)
            ```
        """
        return ArtifactVersion.from_fqn(fqn=fqn)

    def list_artifact_versions(
        self,
        ml_repo: str,
        name: str,
        artifact_type: Optional[ArtifactType] = ArtifactType.ARTIFACT,
    ) -> Iterator[ArtifactVersion]:
        """
        Get all the version of na artifact to download contents or load them in memory

        Args:
            ml_repo (str): Repository in which the model is stored.
            name (str): Name of the artifact whose version is required
            artifact_type (ArtifactType): Type of artifact you want for example model, image, etc.

        Returns:
            Iterator[ArtifactVersion]: An iterator that yields non deleted artifact-versions
                of an artifact under a given ml_repo  sorted reverse by the version number

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            artifact_versions = client.list_artifact_versions(ml_repo="my-repo", name="artifact-name")

            for artifact_version in artifact_versions:
                print(artifact_version)
            ```
        """
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        artifacts = self.mlflow_client.list_artifacts_mlf(
            ml_repo_id=ml_repo_id, name=name, artifact_type=artifact_type
        )
        if not artifacts or len(artifacts) == 0:
            err_msg = f"Artifact Does Not Exist for ml_repo={ml_repo}, name={name}, type={artifact_type}"
            raise MlFoundryException(err_msg)
        return self._list_artifact_versions_by_id(artifact=artifacts[0])

    def list_artifact_versions_by_fqn(
        self, artifact_fqn: str
    ) -> Iterator[ArtifactVersion]:
        """
        List versions for a given artifact

        Args:
            artifact_fqn: FQN of the Artifact to list versions for.
                An artifact_fqn looks like `{artifact_type}:{org}/{user}/{project}/{artifact_name}`
                or `{artifact_type}:{user}/{project}/{artifact_name}`

                where artifact_type can be on of ("model", "image", "plot")

        Returns:
            Iterator[ArtifactVersion]: An iterator that yields non deleted artifact versions
                under the given artifact_fqn sorted reverse by the version number

        Yields:
            ArtifactVersion: An instance of `mlfoundry.ArtifactVersion`

        Examples:

            ```python
            import mlfoundry

            mlfoundry.login(tracking_uri=https://your.truefoundry.site.com")
            client = mlfoundry.get_client()
            artifact_fqn = "artifact:org/my-project/my-artifact"
            for av in client.list_artifact_versions(artifact_fqn=artifact_fqn):
                print(av.name, av.version, av.description)
            ```
        """
        artifact = self.mlflow_client.get_artifact_by_fqn(fqn=artifact_fqn)
        return self._list_artifact_versions_by_id(artifact=artifact)

    def _list_artifact_versions_by_id(
        self, artifact_id: Optional[uuid.UUID] = None, artifact: Artifact = None
    ) -> Iterator[ArtifactVersion]:
        if artifact and not artifact_id:
            artifact_id = artifact.id
        elif not artifact and artifact_id:
            artifact = self.mlflow_client.get_artifact_by_id(artifact_id=artifact_id)
        else:
            raise MlFoundryException(
                "Exactly one of artifact_id or artifact should be passed"
            )

        max_results, page_token, done = 10, None, False
        while not done:
            artifact_versions = self.mlflow_client.list_artifact_versions(
                artifact_id=artifact_id, max_results=max_results, page_token=page_token
            )
            page_token = artifact_versions.token
            for artifact_version in artifact_versions:
                yield ArtifactVersion(
                    artifact_version=artifact_version, artifact=artifact
                )
            if not artifact_versions or not page_token:
                done = True

    def log_artifact(
        self,
        ml_repo: str,
        name: str,
        artifact_paths: List[
            Union[Tuple[str], Tuple[str, Optional[str]], ArtifactPath]
        ],
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        progress: Optional[bool] = None,
    ) -> ArtifactVersion | None:
        """Logs an artifact for the current `ml_repo`.

        An `artifact` is a list of local files and directories.
        This function packs the mentioned files and directories in `artifact_paths`
        and uploads them to remote storage linked to the ml_repo

        Args:
            ml_repo (str): Name of the ML Repo to which an artifact is to be logged.
            name (str): Name of the Artifact. If an artifact with this name already exists under the current ml_repo,
                the logged artifact will be added as a new version under that `name`. If no artifact exist with
                the given `name`, the given artifact will be logged as version 1.
            artifact_paths (List[mlfoundry.ArtifactPath], optional): A list of pairs
                of (source path, destination path) to add files and folders
                to the artifact version contents. The first member of the pair should be a file or directory path
                and the second member should be the path inside the artifact contents to upload to.
            progress (bool): value to show progress bar, defaults to None.
                ```
                E.g. >>> client.log_artifact(
                     ...     ml_repo="sample-repo",
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
            ml_repo = "sample-repo"

            client.create_ml_repo(ml_repo=ml_repo)
            client.log_artifact(
                ml_repo=ml_repo,
                name="hello-world-file",
                artifact_paths=[mlfoundry.ArtifactPath('artifact.txt', 'a/b/')]
            )
            ```
        """
        if not artifact_paths:
            raise MlFoundryException(
                "artifact_paths cannot be empty, atleast one artifact_path must be passed"
            )

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        artifact_version = _log_artifact_version(
            run=None,
            mlflow_client=self.mlflow_client,
            ml_repo_id=ml_repo_id,
            name=name,
            artifact_paths=artifact_paths,
            description=description,
            metadata=metadata,
            step=None,
            progress=progress,
        )
        logger.info(f"Logged artifact successfully with fqn {artifact_version.fqn!r}")
        return artifact_version

    def log_model(
        self,
        *,
        ml_repo: str,
        name: str,
        model_file_or_folder: Optional[str] = None,
        framework: Optional[Union[ModelFramework, str]],
        additional_files: Sequence[Tuple[Union[str, Path], Optional[str]]] = (),
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        model_schema: Optional[Union[Dict[str, Any], ModelSchema]] = None,
        custom_metrics: Optional[List[Union[Dict[str, Any], CustomMetric]]] = None,
        # Deprecated:
        model: Optional[Any] = None,
        model_save_kwargs: Optional[Dict[str, Any]] = None,
    ) -> ModelVersion:
        """
        Serialize and log a versioned model under the current ml_repo. Each logged model generates a new version
        associated with the given `name` and linked to the current run. Multiple versions of the model can be
        logged as separate versions under the same `name`.

        Args:
            ml_repo (str): Name of the ML Repo to which an artifact is to be logged.
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
                │   └── clf.joblib # if `model_file_or_folder` is a folder, contents will be added here
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
            model_version = client.log_model(
                ml_repo="my-classification-project",
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
            model_version = client.log_model(
                ml_repo="my-llm-project",
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
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)

        model_version = _log_model_version(
            run=None,
            mlflow_client=self.mlflow_client,
            ml_repo_id=ml_repo_id,
            name=name,
            model_file_or_folder=model_file_or_folder,
            framework=framework,
            additional_files=additional_files,
            description=description,
            metadata=metadata,
            model_schema=model_schema,
            custom_metrics=custom_metrics,
            step=None,
            # Deprecated:
            model=model,
            model_save_kwargs=model_save_kwargs,
        )
        logger.info(f"Logged model successfully with fqn {model_version.fqn!r}")
        return model_version

    # Datasets API
    def create_data_directory(
        self,
        ml_repo: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DataDirectory:
        """
        Create DataDirectory to Upload the files

        Args:
            ml_repo (str): Name of the ML Repo in which you want to create data_directory
            name (str): Name of the DataDirectory to be created.
            description (str): Description of the Datset
            metadata (Dict <str>: Any): Metadata about the data_directory in Dictionary form.

        Returns:
            DataDirectory : An instance of class DataDirectory

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directory = client.create_data_directory(name="<data_directory-name>", ml_repo="<repo-name>")
            print(data_directory.fqn)
            ```
        """
        if name == "" or not isinstance(name, str):
            raise MlFoundryException(
                f"DataDirectory name must be string type and not empty. "
                f"Got {type(name)} type with value {name}"
            )

        if ml_repo == "" or not isinstance(ml_repo, str):
            raise MlFoundryException(
                f"ML repo must be string type and not empty. "
                f"Got {type(ml_repo)} type with value {ml_repo}"
            )

        data_directory = self.get_data_directory(ml_repo=ml_repo, name=name)
        if data_directory:
            logger.warning(
                f"Data Directory with the name {name} already exists in ML Repo {ml_repo}, returning the orignal instance of DataDirectory instead"
            )
            return data_directory

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)

        dataset = self.mlflow_client.create_dataset(
            name=name,
            experiment_id=int(ml_repo_id),
            description=description,
            dataset_metadata=metadata,
        )

        return DataDirectory(dataset=dataset)

    def get_data_directory_by_id(self, id: uuid.UUID) -> DataDirectory:
        """
        Get the DataDirectory From the DataDirectory ID

        Args:
            id (uuid.UUID): Id of the data_directory.

        Returns:
            DataDirectory : An instance of class DataDirectory

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directory = client.get_data_directory_by_id(id="<data_directory-id>")
            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            data_directory.add_files(
                artifact_paths=[mlfoundry.DataDirectoryPath('artifact.txt', 'a/b/')]
            )
            # print the path of files and folder in the data_directory
            for file in data_directory.list_files():
                print(file.path)
            ```
        """
        dataset = self.mlflow_client.get_dataset(id=id)
        return DataDirectory(dataset)

    def get_data_directory_by_fqn(
        self,
        fqn: str,
    ) -> DataDirectory:
        """
        Get the DataDirectory by DataDirectory FQN

        Args:
            fqn (str): Fully qualified name of the artifact version.

        Returns:
            DataDirectory : An instance of class DataDirectory

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<data-dir-fqn>")
            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            data_directory.add_files(
                artifact_paths=[mlfoundry.DataDirectoryPath('artifact.txt', 'a/b/')]
            )
            # print the path of files and folder in the data_directory
            for file in data_directory.list_files():
                print(file.path)
            ```
        """
        dataset = self.mlflow_client.get_dataset_by_fqn(fqn=fqn)
        return DataDirectory(dataset)

    def get_data_directory(
        self,
        ml_repo: str,
        name: str,
    ) -> DataDirectory:
        """Get an existing `data_directory` by `name`.
        Args:
            ml_repo (str): name of an the project of which the data-directory is part of.
            name (str): the name of the data-directory
        Returns:
            DataDirectory: An instance of class DataDirectory
        Examples:
            ```python
            import mlfoundry
            client = mlfoundry.get_client()
            data_directory = client.get_data_directory(ml_repo='my-repo', name="<data-directory-name>")
            with open("artifact.txt", "w") as f:
                f.write("hello-world")
            data_directory.add_files(
                artifact_paths=[mlfoundry.DataDirectoryPath('artifact.txt', 'a/b/')]
            )
            # print the path of files and folder in the data_directory
            for file in data_directory.list_files():
                print(file.path)
            ```
        """
        if ml_repo == "" or not isinstance(ml_repo, str):
            raise MlFoundryException(
                f"ML repo must be string type and not empty. "
                f"Got {type(ml_repo)} type with value {ml_repo}"
            )
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        data_directory = self.mlflow_client.list_datasets(
            experiment_id=ml_repo_id,
            name=name,
            max_results=1,
        )
        if len(data_directory) == 0:
            return

        return DataDirectory(data_directory[0])

    def list_data_directories(
        self,
        ml_repo: str,
        max_results: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Iterator[DataDirectory]:
        """
        Get the list of DataDirectory in a ml_repo

        Args:
            ml_repo (str): Name of the ML Repository
            max_results (int): Maximum number of Data Directory to list
            offset (int): Skip these number of instance of DataDirectory and then give the result from these number onwards

        Returns:
            DataDirectory : An instance of class DataDirectory

        Examples:

            ```python
            import mlfoundry

            client = mlfoundry.get_client()
            data_directories = client.list_data_directories(ml_repo="<ml-repo-nam>")

            for data_directory in data_directories:
                print(data_directory.name)
            ```
        """
        if ml_repo == "" or not isinstance(ml_repo, str):
            raise MlFoundryException(
                f"ML repo must be string type and not empty. "
                f"Got {type(ml_repo)} type with value {ml_repo}"
            )
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        done = False
        while not done:
            datasets = self.mlflow_client.list_datasets(
                experiment_id=ml_repo_id,
                max_results=max_results,
                offset=offset,
            )
            page_token = datasets.token
            for dataset in datasets:
                yield DataDirectory(dataset=dataset)
            if not datasets or not page_token:
                done = True
