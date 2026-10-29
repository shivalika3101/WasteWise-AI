import datetime as _datetime
import logging as _logging
import pathlib as _pathlib

import fastapi.testclient as _testclient
import pytest as _pytest
import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import sqlalchemy.pool as _pool

import app.database as _database
import app.dependencies as _dependencies
import app.main as _main
import app.models as _models
import app.predictor as _predictor
import app.routers.predictions as _predictions
import ml.inference.model as _model
import ml.inference.predictor as _ml_predictor

_IMAGE = (_pathlib.Path(__file__).parent / "fixtures" / "plastic_water_bottle.png").read_bytes()
_ENSEMBLE_PREDICTION = _ml_predictor.Prediction(
    label_index=24,
    label="plastic_water_bottles",
    confidence=0.95,
    models_used=_model.MODEL_NAMES,
    failed_models=(),
)
_REAL_PREDICT = _predictor.predict


@_pytest.fixture
def api(monkeypatch):
    monkeypatch.setattr(_predictor, "predict", lambda _: _ENSEMBLE_PREDICTION)
    engine = _sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=_pool.StaticPool,
    )
    _database.Base.metadata.create_all(engine)
    db = _orm.Session(engine)

    user = _models.User(email="zahra@example.com", password_hash="not-used")
    category = _models.Category(
        name="plastic_water_bottles",
        display_name="Plastic water bottle",
        model_label_index=24,
    )
    bin_record = _models.Bin(
        name="Mixed Dry Recycling",
        colour="green",
        description="Plastic bottles and cans",
    )
    db.add_all([user, category, bin_record])
    db.flush()
    db.add_all(
        [
            _models.CategoryBin(
                category_id=category.id,
                bin_id=bin_record.id,
                is_primary=True,
            ),
            _models.DisposalInstruction(
                category_id=category.id,
                instructions="Empty and rinse, then recycle.",
            ),
        ]
    )
    db.commit()

    def get_db():
        yield db

    def get_current_user():
        return user

    _main.app.dependency_overrides[_database.get_db] = get_db
    _main.app.dependency_overrides[_dependencies.get_current_user] = get_current_user
    client = _testclient.TestClient(_main.app)
    yield client, db, user
    _main.app.dependency_overrides.clear()
    db.close()
    engine.dispose()


def upload(client, content=_IMAGE, content_type="image/png"):
    return client.post(
        "/predictions/",
        files={"image": ("waste.png", content, content_type)},
    )


def test_prediction_is_protected(api):
    client, _, _ = api
    override = _main.app.dependency_overrides.pop(_dependencies.get_current_user)
    try:
        response = upload(client)
    finally:
        _main.app.dependency_overrides[_dependencies.get_current_user] = override
    assert response.status_code == 401


def test_valid_image_returns_resolved_guidance(api):
    client, _, _ = api
    response = upload(client)
    assert response.status_code == 201
    assert response.json() == {
        "prediction_id": 1,
        "category": "Plastic water bottle",
        "confidence": 0.95,
        "bin": "Mixed Dry Recycling",
        "guidance": "Empty and rinse, then recycle.",
    }


def test_prediction_is_stored_for_the_current_user(api):
    client, db, user = api
    upload(client)
    stored = db.scalar(_sa.select(_models.Prediction))
    assert stored.user_id == user.id
    assert stored.predicted_category_id == 1
    assert stored.chosen_bin_id == 1
    assert float(stored.confidence) == 0.95
    assert stored.selected_model is None


def test_the_ensemble_result_drives_guidance_lookup(api, monkeypatch):
    client, db, _ = api
    aerosol = _models.Category(
        name="aerosol_cans",
        display_name="Aerosol can",
        model_label_index=0,
    )
    aerosol_bin = _models.Bin(name="Household Waste", colour="black", description="General waste")
    db.add_all([aerosol, aerosol_bin])
    db.flush()
    db.add_all(
        [
            _models.CategoryBin(category_id=aerosol.id, bin_id=aerosol_bin.id, is_primary=True),
            _models.DisposalInstruction(
                category_id=aerosol.id,
                instructions="Do not puncture; take to a recycling point.",
            ),
        ]
    )
    db.commit()

    ensemble = _ml_predictor.Prediction(
        label_index=0,
        label="aerosol_cans",
        confidence=0.8,
        models_used=_model.MODEL_NAMES,
        failed_models=(),
    )
    monkeypatch.setattr(_predictor, "predict", lambda _: ensemble)

    response = upload(client)

    assert response.status_code == 201
    body = response.json()
    assert body["category"] == "Aerosol can"


def test_low_confidence_ensemble_result_is_still_accepted(api, monkeypatch):
    client, db, _ = api
    low = _ml_predictor.Prediction(
        label_index=24,
        label="plastic_water_bottles",
        confidence=0.04,
        models_used=_model.MODEL_NAMES,
        failed_models=(),
    )
    monkeypatch.setattr(_predictor, "predict", lambda _: low)

    response = upload(client)

    assert response.status_code == 201
    assert response.json()["confidence"] == 0.04
    stored = db.scalar(_sa.select(_models.Prediction))
    assert float(stored.confidence) == 0.04


def test_partial_model_failure_still_returns_the_ensemble_result(api, monkeypatch):
    client, _, _ = api
    partial = _ml_predictor.Prediction(
        label_index=24,
        label="plastic_water_bottles",
        confidence=0.65,
        models_used=("efficientnet", "densenet"),
        failed_models=("mobilenet", "resnet"),
    )
    monkeypatch.setattr(_predictor, "predict", lambda _: partial)

    response = upload(client)

    assert response.status_code == 201
    body = response.json()
    assert body["confidence"] == 0.65
    assert "selected_model" not in body


def test_prediction_upload_never_logs_the_image_bytes(api, caplog):
    client, _, _ = api
    marker = _IMAGE.hex()
    with caplog.at_level(_logging.DEBUG):
        response = upload(client)
    assert response.status_code == 201
    assert marker not in caplog.text
    assert repr(_IMAGE) not in caplog.text


def test_history_returns_the_current_users_newest_predictions_first(api):
    client, db, user = api
    older = _models.Prediction(
        user_id=user.id,
        predicted_category_id=1,
        chosen_bin_id=1,
        confidence=0.5,
        created_at=_datetime.datetime(2026, 7, 20, 10, 0),
    )
    newer = _models.Prediction(
        user_id=user.id,
        predicted_category_id=1,
        chosen_bin_id=1,
        confidence=0.9,
        created_at=_datetime.datetime(2026, 7, 20, 11, 0),
    )
    other_user = _models.User(email="other@example.com", password_hash="not-used")
    db.add_all([older, newer, other_user])
    db.flush()
    db.add(
        _models.Prediction(
            user_id=other_user.id,
            predicted_category_id=1,
            chosen_bin_id=1,
            confidence=0.8,
            created_at=_datetime.datetime(2026, 7, 20, 12, 0),
        )
    )
    db.commit()

    response = client.get("/predictions/history")

    assert response.status_code == 200
    assert [item["prediction_id"] for item in response.json()] == [newer.id, older.id]
    assert response.json()[0] == {
        "prediction_id": newer.id,
        "category": "Plastic water bottle",
        "confidence": 0.9,
        "bin": "Mixed Dry Recycling",
        "guidance": "Empty and rinse, then recycle.",
        "created_at": "2026-07-20T11:00:00",
    }


def test_history_does_not_expose_the_legacy_selected_model_field(api):
    client, db, user = api
    db.add(
        _models.Prediction(
            user_id=user.id,
            predicted_category_id=1,
            chosen_bin_id=1,
            confidence=0.9,
            selected_model="efficientnet",
        )
    )
    db.commit()
    assert "selected_model" not in client.get("/predictions/history").json()[0]


def test_history_is_empty_for_a_user_with_no_predictions(api):
    client, _, _ = api
    assert client.get("/predictions/history").json() == []


def test_history_is_protected(api):
    client, _, _ = api
    override = _main.app.dependency_overrides.pop(_dependencies.get_current_user)
    try:
        response = client.get("/predictions/history")
    finally:
        _main.app.dependency_overrides[_dependencies.get_current_user] = override
    assert response.status_code == 401


def test_history_pagination_bounds_the_page_size(api):
    client, db, user = api
    db.add_all(
        _models.Prediction(
            user_id=user.id,
            predicted_category_id=1,
            chosen_bin_id=1,
            confidence=0.5,
            created_at=_datetime.datetime(2026, 7, 20, 10, minute),
        )
        for minute in range(5)
    )
    db.commit()

    default_page = client.get("/predictions/history")
    assert len(default_page.json()) == 5

    first_page = client.get("/predictions/history", params={"limit": 2})
    assert [item["prediction_id"] for item in first_page.json()] == [5, 4]

    second_page = client.get("/predictions/history", params={"limit": 2, "offset": 2})
    assert [item["prediction_id"] for item in second_page.json()] == [3, 2]


def test_history_pagination_rejects_out_of_range_values(api):
    client, _, _ = api
    assert client.get("/predictions/history", params={"limit": 0}).status_code == 422
    assert client.get("/predictions/history", params={"limit": 101}).status_code == 422
    assert client.get("/predictions/history", params={"offset": -1}).status_code == 422


def test_summary_is_empty_for_a_user_with_no_predictions(api):
    client, _, _ = api
    assert client.get("/predictions/summary").json() == {
        "total_predictions": 0,
        "latest_prediction": None,
        "most_frequent_category": None,
    }


def test_summary_reports_totals_latest_result_and_most_frequent_category(api):
    client, db, user = api
    aerosol = _models.Category(name="aerosol_cans", display_name="Aerosol can", model_label_index=0)
    db.add(aerosol)
    db.flush()
    db.add(_models.DisposalInstruction(category_id=aerosol.id, instructions="Take to a recycling point."))
    db.add_all(
        [
            _models.Prediction(
                user_id=user.id,
                predicted_category_id=1,
                chosen_bin_id=1,
                confidence=0.5,
                created_at=_datetime.datetime(2026, 7, 20, 10, 0),
            ),
            _models.Prediction(
                user_id=user.id,
                predicted_category_id=1,
                chosen_bin_id=1,
                confidence=0.6,
                created_at=_datetime.datetime(2026, 7, 20, 11, 0),
            ),
            _models.Prediction(
                user_id=user.id,
                predicted_category_id=aerosol.id,
                chosen_bin_id=1,
                confidence=0.7,
                selected_model="resnet",
                created_at=_datetime.datetime(2026, 7, 20, 12, 0),
            ),
        ]
    )
    db.commit()

    response = client.get("/predictions/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_predictions"] == 3
    assert body["most_frequent_category"] == "Plastic water bottle"
    assert body["latest_prediction"]["category"] == "Aerosol can"
    assert "selected_model" not in body["latest_prediction"]


def test_summary_is_protected(api):
    client, _, _ = api
    override = _main.app.dependency_overrides.pop(_dependencies.get_current_user)
    try:
        response = client.get("/predictions/summary")
    finally:
        _main.app.dependency_overrides[_dependencies.get_current_user] = override
    assert response.status_code == 401


def test_summary_is_isolated_per_user(api):
    client, db, user = api
    other_user = _models.User(email="other@example.com", password_hash="not-used")
    db.add(other_user)
    db.flush()
    db.add_all(
        [
            _models.Prediction(user_id=user.id, predicted_category_id=1, chosen_bin_id=1, confidence=0.5),
            _models.Prediction(user_id=other_user.id, predicted_category_id=1, chosen_bin_id=1, confidence=0.9),
            _models.Prediction(user_id=other_user.id, predicted_category_id=1, chosen_bin_id=1, confidence=0.8),
        ]
    )
    db.commit()

    assert client.get("/predictions/summary").json()["total_predictions"] == 1

    override = _main.app.dependency_overrides[_dependencies.get_current_user]
    _main.app.dependency_overrides[_dependencies.get_current_user] = lambda: other_user
    try:
        assert client.get("/predictions/summary").json()["total_predictions"] == 2
    finally:
        _main.app.dependency_overrides[_dependencies.get_current_user] = override


def test_history_pagination_never_leaks_another_users_predictions(api):
    client, db, user = api
    other_user = _models.User(email="other@example.com", password_hash="not-used")
    db.add(other_user)
    db.flush()
    db.add_all(
        _models.Prediction(user_id=user.id, predicted_category_id=1, chosen_bin_id=1, confidence=0.5)
        for _ in range(3)
    )
    db.add_all(
        _models.Prediction(user_id=other_user.id, predicted_category_id=1, chosen_bin_id=1, confidence=0.9)
        for _ in range(3)
    )
    db.commit()

    response = client.get("/predictions/history", params={"limit": 100})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert all(item["confidence"] == 0.5 for item in body)


@_pytest.mark.parametrize(
    ("content", "content_type", "status_code"),
    [
        (b"", "image/png", 400),
        (b"not an image", "image/png", 400),
        (_IMAGE, "image/gif", 415),
        (_IMAGE, "image/jpeg", 415),
        (b"x" * (_predictions.MAX_IMAGE_BYTES + 1), "image/png", 413),
    ],
    ids=["empty", "unreadable", "unsupported", "mime-mismatch", "oversized"],
)
def test_invalid_uploads_are_rejected(api, content, content_type, status_code):
    client, db, _ = api
    assert upload(client, content, content_type).status_code == status_code
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Prediction)) == 0


def test_missing_guidance_returns_no_false_success(api):
    client, db, _ = api
    db.execute(_sa.delete(_models.DisposalInstruction))
    db.commit()
    response = upload(client)
    assert response.status_code == 500
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Prediction)) == 0


def test_failed_write_is_rolled_back(api, monkeypatch):
    client, db, _ = api

    def fail_commit():
        raise _sa.exc.OperationalError("COMMIT", {}, RuntimeError("write failed"))

    monkeypatch.setattr(db, "commit", fail_commit)
    response = upload(client)
    assert response.status_code == 500
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Prediction)) == 0


@_pytest.fixture
def real_model(api, monkeypatch):
    monkeypatch.setattr(_predictor, "predict", _REAL_PREDICT)
    return api


def _models_return(monkeypatch, results):
    monkeypatch.setattr(_ml_predictor, "predict_models", lambda _: (results, ()))


def _models_raise(monkeypatch, error):
    def fail(_):
        raise error

    monkeypatch.setattr(_ml_predictor, "predict_models", fail)


def test_known_image_is_classified_and_stored(real_model):
    client, db, user = real_model
    expected = _REAL_PREDICT(_IMAGE)
    response = upload(client)
    assert response.status_code == 201

    body = response.json()
    assert body["category"] == "Plastic water bottle"
    assert body["bin"] == "Mixed Dry Recycling"
    assert body["guidance"] == "Empty and rinse, then recycle."
    assert body["confidence"] == _pytest.approx(expected.confidence, abs=1e-4)
    assert body["confidence"] > 0.8
    assert "selected_model" not in body

    stored = db.scalar(_sa.select(_models.Prediction))
    assert stored.user_id == user.id
    assert float(stored.confidence) == _pytest.approx(expected.confidence, abs=1e-4)
    assert stored.selected_model is None


def test_unreadable_image_is_rejected(real_model, monkeypatch):
    client, db, _ = real_model
    _models_raise(monkeypatch, _predictor.InvalidImageError())
    assert upload(client).status_code == 400
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Prediction)) == 0


def test_model_failure_is_reported_as_unavailable(real_model, monkeypatch):
    client, db, _ = real_model
    _models_raise(monkeypatch, RuntimeError("forward pass failed"))
    assert upload(client).status_code == 503
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Prediction)) == 0


def test_out_of_contract_prediction_never_reaches_the_database(real_model, monkeypatch):
    client, db, _ = real_model
    bad_results = tuple(
        _ml_predictor.ModelPrediction(
            model_name=name,
            label_index=24,
            label="plastic_water_bottles",
            confidence=95.0,
            probabilities=(),
        )
        for name in _model.MODEL_NAMES
    )
    _models_return(monkeypatch, bad_results)
    assert upload(client).status_code == 503
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Prediction)) == 0


def test_unmapped_label_never_reaches_the_database(real_model, monkeypatch):
    client, db, _ = real_model
    bad_results = tuple(
        _ml_predictor.ModelPrediction(
            model_name=name,
            label_index=999,
            label="plastic_water_bottles",
            confidence=0.9,
            probabilities=(),
        )
        for name in _model.MODEL_NAMES
    )
    _models_return(monkeypatch, bad_results)
    assert upload(client).status_code == 503
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Prediction)) == 0
