import fastapi.testclient as _testclient
import pytest as _pytest

import app.bootstrap as _bootstrap
import app.main as _main
import app.predictor as _predictor
import ml.inference.model as _model


@_pytest.fixture
def without_database(monkeypatch):
    monkeypatch.setattr(_bootstrap, "run", lambda: None)


def test_models_are_not_loaded_at_startup(without_database, monkeypatch):
    calls = []
    monkeypatch.setattr(_predictor, "load", lambda: calls.append("load"))

    with _testclient.TestClient(_main.app):
        pass

    assert calls == []


def test_load_rejects_an_empty_model_set(monkeypatch):
    monkeypatch.setattr(_model, "load_models", lambda: {})

    with _pytest.raises(RuntimeError, match="Failed to load any models"):
        _predictor.load()


def test_startup_does_not_fail_when_model_loading_would_raise(
    without_database,
    monkeypatch,
):
    def fail():
        raise RuntimeError("all model packages failed")

    monkeypatch.setattr(_predictor, "load", fail)

    with _testclient.TestClient(_main.app):
        pass
