import pytest as _pytest

import ml.inference.model as _model

@_pytest.mark.requires_models
def test_all_model_packages_exist():
    assert set(_model.MODEL_PATHS) == set(_model.MODEL_NAMES)
    assert all(path.exists() for path in _model.MODEL_PATHS.values())


def test_models_are_cached(monkeypatch):
    sentinels = {
        name: object() for name in _model.MODEL_NAMES
    }
    monkeypatch.setattr(
        _model,
        "_model_loaders",
        lambda: {
            name: (lambda value=value: value)
            for name, value in sentinels.items()
        },
    )
    _model.load_models.cache_clear()

    assert _model.load_models() == sentinels
    assert _model.load_models() is _model.load_models()

    _model.load_models.cache_clear()


def test_one_load_failure_keeps_the_remaining_models(monkeypatch):
    def fail():
        raise FileNotFoundError("checkpoint missing")

    monkeypatch.setattr(
        _model,
        "_model_loaders",
        lambda: {
            "mobilenet": lambda: "mobile",
            "efficientnet": fail,
            "resnet": lambda: "resnet",
            "densenet": lambda: "densenet",
        },
    )
    _model.load_models.cache_clear()

    assert _model.load_models() == {
        "mobilenet": "mobile",
        "resnet": "resnet",
        "densenet": "densenet",
    }

    _model.load_models.cache_clear()


def test_all_load_failures_raise(monkeypatch):
    def fail():
        raise FileNotFoundError("checkpoint missing")

    monkeypatch.setattr(
        _model,
        "_model_loaders",
        lambda: {name: fail for name in _model.MODEL_NAMES},
    )
    _model.load_models.cache_clear()

    with _pytest.raises(_model.ModelLoadError, match="All models failed"):
        _model.load_models()

    _model.load_models.cache_clear()
