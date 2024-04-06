"""Custom _load_pyfunc function for loading model from source code."""
import importlib
import sys
from pathlib import Path

CONFIG_KEY_ARTIFACTS = "artifacts"


class PythonModelContext:
    """
    A collection of artifacts that a :class:`~PythonModel` can use when performing inference.

    :class:`~PythonModelContext` objects are created *implicitly* by the
    :func:`save_model() <mlflow.pyfunc.save_model>` and
    :func:`log_model() <mlflow.pyfunc.log_model>` persistence methods, using the contents specified
    by the ``artifacts`` parameter of these methods.
    """

    def __init__(self, artifacts):
        """:param artifacts: A dictionary of ``<name, artifact_path>``."""
        self._artifacts = artifacts

    @property
    def artifacts(self):
        """A dictionary containing ``<name, artifact_path>``."""
        return self._artifacts


def _load_pyfunc(model_path):
    parts = Path(model_path).parts
    if str(Path(*parts[:2])) not in sys.path:
        sys.path.append(str(Path(*parts[:2])))

    python_model = importlib.import_module(".".join(parts[2:])).get_object()

    artifacts = Path(model_path) / CONFIG_KEY_ARTIFACTS
    if not artifacts.exists():
        artifacts.mkdir()

    context = PythonModelContext(artifacts=str(artifacts))
    python_model.load_context(context=context)
    return _PythonModelPyfuncWrapper(python_model=python_model, context=context, signature=None)


class _PythonModelPyfuncWrapper:
    """Wrapper class."""

    def __init__(self, python_model, context, signature):
        """Init wrapper class.

        :param python_model: An instance of a subclass of :class:`~PythonModel`.
        :param context: A :class:`~PythonModelContext` instance containing artifacts that
                        ``python_model`` may use when performing inference.
        :param signature: :class:`~ModelSignature` instance describing model input and output.
        """
        self.python_model = python_model
        self.context = context
        self.signature = signature

    def predict(self, model_input):
        return self.python_model.predict_function(self.context, model_input)
