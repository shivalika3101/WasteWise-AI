import pathlib as _pathlib
import sys as _sys

_REPO_ROOT = _pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))

import ml.inference.labels as _labels
import ml.inference.model as _model
import ml.inference.predictor as _ml_predictor
import ml.inference.preprocessing as _preprocessing

InvalidImageError = _preprocessing.InvalidImageError


class PredictorError(Exception):
    pass


def load() -> None:
    models = _model.load_models()

    if not models:
        raise RuntimeError("Failed to load any models.")


def _is_valid_prediction(result: _ml_predictor.Prediction) -> bool:
    if not 0 <= result.label_index < len(_labels.LABELS):
        return False
    if result.label != _labels.LABELS[result.label_index]:
        return False
    return 0.0 <= result.confidence <= 1.0


def predict(image_bytes: bytes) -> _ml_predictor.Prediction:
    """Return the arithmetic-mean ensemble result from all available models."""
    try:
        result = _ml_predictor.predict(image_bytes)
    except InvalidImageError:
        raise
    except Exception as error:
        raise PredictorError("the model ensemble failed to produce a prediction") from error

    if not _is_valid_prediction(result):
        raise PredictorError("the model ensemble produced an invalid prediction")
    return result
