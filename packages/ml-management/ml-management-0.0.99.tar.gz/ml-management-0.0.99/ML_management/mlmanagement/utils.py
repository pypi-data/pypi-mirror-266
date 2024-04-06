"""Functions for internal usage."""
import inspect
from typing import Optional

import mlflow
from ML_management.mlmanagement import mlmanagement
from ML_management.mlmanagement.mlmanager import request_for_function


def _load_model_type(run_id, unwrap: bool = True, dst_path: Optional[str] = None):
    """Load model from local path."""
    local_path = mlmanagement.MlflowClient().download_artifacts(run_id=run_id, path="", dst_path=dst_path)
    loaded_model = mlflow.pyfunc.load_model(local_path)
    if unwrap:
        artifacts_path = loaded_model._model_impl.context._artifacts
        loaded_model = loaded_model.unwrap_python_model()
        loaded_model.artifacts = artifacts_path
    return loaded_model


def _add_eval_run(run_id: str):  # noqa: ARG001
    """Set the active run as the eval run for the model with 'run_id'."""
    return request_for_function(inspect.currentframe())
