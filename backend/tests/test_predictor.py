import io as _io

import numpy as _np
import PIL.Image as _image
import pytest as _pytest

import ml.inference.labels as _labels
import ml.inference.model as _model
import ml.inference.predictor as _predictor
import ml.inference.preprocessing as _preprocessing


def _image_bytes(colour="white"):
    buffer = _io.BytesIO()
    _image.new("RGB", (120, 90), colour).save(buffer, format="PNG")
    return buffer.getvalue()


def _model_prediction(name, probabilities):
    probabilities = tuple(probabilities)
    index = int(_np.argmax(probabilities))
    return _predictor.ModelPrediction(
        model_name=name,
        label_index=index,
        label=_labels.LABELS[index],
        confidence=float(probabilities[index]),
        probabilities=probabilities,
    )


def _probabilities(index, confidence=1.0):
    values = [0.0] * len(_labels.LABELS)
    values[index] = confidence
    if confidence < 1.0:
        values[(index + 1) % len(values)] = 1.0 - confidence
    return values


def test_average_probability_selects_the_ensemble_label():
    first = _model_prediction("mobilenet", _probabilities(2, 0.8))
    second = _model_prediction("resnet", _probabilities(3, 0.6))

    prediction = _predictor.combine_predictions((first, second))

    assert prediction.label_index == 2
    assert prediction.label == _labels.LABELS[2]
    assert prediction.confidence == _pytest.approx(0.4)
    assert prediction.models_used == ("mobilenet", "resnet")


def test_exact_tie_uses_the_lowest_canonical_index():
    first = _model_prediction("mobilenet", _probabilities(2))
    second = _model_prediction("resnet", _probabilities(3))

    prediction = _predictor.combine_predictions((first, second))

    assert prediction.label_index == 2
    assert prediction.confidence == _pytest.approx(0.5)


def test_low_confidence_is_returned_without_rejection():
    values = [1 / len(_labels.LABELS)] * len(_labels.LABELS)
    result = _model_prediction("mobilenet", values)

    prediction = _predictor.combine_predictions((result,))

    assert prediction.confidence == _pytest.approx(1 / len(_labels.LABELS))


def test_one_forward_failure_uses_remaining_models(monkeypatch):
    working_model = object()
    failed_model = object()
    monkeypatch.setattr(
        _model,
        "load_models",
        lambda: {
            "mobilenet": working_model,
            "resnet": failed_model,
        },
    )

    def fake_torch(current_model, _batch):
        if current_model is working_model:
            return _probabilities(4)
        raise RuntimeError("forward failed")

    monkeypatch.setattr(_predictor, "_predict_torch", fake_torch)

    results, failures = _predictor.predict_models(_image_bytes())

    assert [result.model_name for result in results] == ["mobilenet"]
    assert failures == ("efficientnet", "densenet", "resnet")


def test_invalid_probability_shape_counts_as_model_failure(monkeypatch):
    monkeypatch.setattr(
        _model,
        "load_models",
        lambda: {"mobilenet": object()},
    )
    monkeypatch.setattr(
        _predictor,
        "_predict_torch",
        lambda _model, _batch: [1.0, 0.0],
    )

    with _pytest.raises(RuntimeError, match="All models failed"):
        _predictor.predict_models(_image_bytes())


def test_invalid_image_raises(monkeypatch):
    monkeypatch.setattr(
        _model,
        "load_models",
        lambda: {"mobilenet": object()},
    )

    with _pytest.raises(_preprocessing.InvalidImageError):
        _predictor.predict_models(b"this is not an image")
