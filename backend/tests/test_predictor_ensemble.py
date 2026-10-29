import pytest as _pytest

import app.predictor as _predictor
import ml.inference.labels as _labels
import ml.inference.model as _model
import ml.inference.predictor as _ml_predictor


def _prediction(label_index=0, confidence=0.9, label=None):
    return _ml_predictor.Prediction(
        label_index=label_index,
        label=label if label is not None else _labels.LABELS[label_index],
        confidence=confidence,
        models_used=_model.MODEL_NAMES,
        failed_models=(),
    )


def _returns(monkeypatch, result):
    monkeypatch.setattr(_ml_predictor, "predict", lambda _: result)


def _raises(monkeypatch, error):
    def fail(_):
        raise error

    monkeypatch.setattr(_ml_predictor, "predict", fail)


def test_returns_the_ml_ensembles_prediction(monkeypatch):
    expected = _prediction(label_index=24, confidence=0.76)
    _returns(monkeypatch, expected)

    result = _predictor.predict(b"image")

    assert result is expected
    assert result.models_used == _model.MODEL_NAMES


def test_partial_model_failure_metadata_is_preserved(monkeypatch):
    expected = _ml_predictor.Prediction(
        label_index=24,
        label="plastic_water_bottles",
        confidence=0.7,
        models_used=_model.MODEL_NAMES[1:],
        failed_models=(_model.MODEL_NAMES[0],),
    )
    _returns(monkeypatch, expected)

    result = _predictor.predict(b"image")

    assert result.models_used == _model.MODEL_NAMES[1:]
    assert result.failed_models == (_model.MODEL_NAMES[0],)


def test_all_models_failing_becomes_a_predictor_error(monkeypatch):
    _raises(monkeypatch, RuntimeError("All models failed."))

    with _pytest.raises(_predictor.PredictorError):
        _predictor.predict(b"image")


def test_label_disagreeing_with_index_is_rejected(monkeypatch):
    _returns(monkeypatch, _prediction(label_index=0, label=_labels.LABELS[1]))

    with _pytest.raises(_predictor.PredictorError):
        _predictor.predict(b"image")


def test_out_of_range_confidence_is_rejected(monkeypatch):
    _returns(monkeypatch, _prediction(confidence=1.5))

    with _pytest.raises(_predictor.PredictorError):
        _predictor.predict(b"image")


def test_negative_index_is_rejected(monkeypatch):
    _returns(
        monkeypatch,
        _ml_predictor.Prediction(
            label_index=-1,
            label=_labels.LABELS[0],
            confidence=0.9,
        ),
    )

    with _pytest.raises(_predictor.PredictorError):
        _predictor.predict(b"image")


def test_invalid_image_is_not_disguised(monkeypatch):
    _raises(monkeypatch, _predictor.InvalidImageError())

    with _pytest.raises(_predictor.InvalidImageError):
        _predictor.predict(b"image")
