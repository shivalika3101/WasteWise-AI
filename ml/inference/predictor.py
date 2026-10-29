import dataclasses as _dataclasses
import io as _io

import numpy as _np
import PIL.Image as _image
import torch as _torch

import ml.inference.labels as _labels
import ml.inference.model as _model
import ml.inference.preprocessing as _preprocessing


@_dataclasses.dataclass(frozen=True)
class ModelPrediction:
    model_name: str
    label_index: int
    label: str
    confidence: float
    probabilities: tuple[float, ...]


@_dataclasses.dataclass(frozen=True)
class Prediction:
    label_index: int
    label: str
    confidence: float
    models_used: tuple[str, ...] = ()
    failed_models: tuple[str, ...] = ()


def _predict_torch(model, batch):
    with _torch.no_grad():
        logits = model(batch)
    probabilities = _torch.nn.functional.softmax(logits, dim=1)
    return probabilities.squeeze(0).detach().cpu().numpy()


def _predict_densenet(model, image_bytes):
    image = (
        _image.open(_io.BytesIO(image_bytes))
        .convert("RGB")
        .resize((224, 224))
    )
    image = _np.array(image, dtype=_np.float32)
    image = _np.expand_dims(image, axis=0)
    return _np.asarray(model.predict(image, verbose=0))[0]


def _validated_probabilities(values) -> _np.ndarray:
    probabilities = _np.asarray(values, dtype=_np.float64)

    if probabilities.shape != (len(_labels.LABELS),):
        raise ValueError(
            "model output has shape "
            f"{probabilities.shape}; expected ({len(_labels.LABELS)},)"
        )
    if not _np.all(_np.isfinite(probabilities)):
        raise ValueError("model output contains non-finite values")
    if _np.any(probabilities < 0):
        raise ValueError("model output contains negative probabilities")

    total = float(probabilities.sum())
    if total <= 0:
        raise ValueError("model probabilities have no positive mass")

    return probabilities / total


def predict_models(
    image_bytes: bytes,
) -> tuple[tuple[ModelPrediction, ...], tuple[str, ...]]:
    """Return every successful model result and the failed model names."""
    models = _model.load_models()
    batch = _preprocessing.preprocess(image_bytes)

    results = []
    failed_models = [
        name for name in _model.MODEL_NAMES if name not in models
    ]

    for name in _model.MODEL_NAMES:
        current_model = models.get(name)
        if current_model is None:
            continue

        try:
            if name == "densenet":
                raw_probabilities = _predict_densenet(
                    current_model,
                    image_bytes,
                )
            else:
                raw_probabilities = _predict_torch(
                    current_model,
                    batch,
                )

            probabilities = _validated_probabilities(raw_probabilities)
            label_index = int(_np.argmax(probabilities))
            results.append(
                ModelPrediction(
                    model_name=name,
                    label_index=label_index,
                    label=_labels.LABELS[label_index],
                    confidence=float(probabilities[label_index]),
                    probabilities=tuple(
                        float(value) for value in probabilities
                    ),
                )
            )
        except Exception:
            failed_models.append(name)

    if not results:
        raise RuntimeError("All models failed.")

    return tuple(results), tuple(failed_models)


def combine_predictions(
    model_predictions: tuple[ModelPrediction, ...],
    failed_models: tuple[str, ...] = (),
) -> Prediction:
    if not model_predictions:
        raise RuntimeError("All models failed.")

    average_probabilities = _np.mean(
        [result.probabilities for result in model_predictions],
        axis=0,
    )

    # np.argmax resolves an exact tie to the lowest canonical label index.
    label_index = int(_np.argmax(average_probabilities))

    return Prediction(
        label_index=label_index,
        label=_labels.LABELS[label_index],
        confidence=float(average_probabilities[label_index]),
        models_used=tuple(
            result.model_name for result in model_predictions
        ),
        failed_models=failed_models,
    )


def predict(image_bytes: bytes) -> Prediction:
    model_predictions, failed_models = predict_models(image_bytes)
    return combine_predictions(model_predictions, failed_models)
