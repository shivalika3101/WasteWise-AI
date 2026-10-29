import fastapi.testclient as _testclient
import pytest as _pytest
import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import sqlalchemy.pool as _pool

import app.database as _database
import app.dependencies as _dependencies
import app.main as _main
import app.models as _models


@_pytest.fixture
def api():
    engine = _sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=_pool.StaticPool,
    )
    _database.Base.metadata.create_all(engine)
    db = _orm.Session(engine)

    user = _models.User(email="zahra@example.com", password_hash="not-used")
    other_user = _models.User(email="other@example.com", password_hash="not-used")
    category = _models.Category(name="plastic_water_bottles", display_name="Plastic water bottle", model_label_index=24)
    correct_bin = _models.Bin(name="Mixed Dry Recycling", colour="green", description="Plastic bottles and cans")
    wrong_bin = _models.Bin(name="General Waste", colour="black", description="Non-recyclables")
    db.add_all([user, other_user, category, correct_bin, wrong_bin])
    db.flush()
    db.add_all(
        [
            _models.CategoryBin(category_id=category.id, bin_id=correct_bin.id, is_primary=True),
            _models.DisposalInstruction(category_id=category.id, instructions="Empty and rinse, then recycle."),
        ]
    )
    prediction = _models.Prediction(
        predicted_category_id=category.id,
        confidence=0.95,
        chosen_bin_id=correct_bin.id,
        user_id=user.id,
    )
    db.add(prediction)
    db.commit()

    def get_db():
        yield db

    def get_current_user():
        return user

    _main.app.dependency_overrides[_database.get_db] = get_db
    _main.app.dependency_overrides[_dependencies.get_current_user] = get_current_user
    client = _testclient.TestClient(_main.app)
    yield client, db, user, other_user, prediction, correct_bin, wrong_bin
    _main.app.dependency_overrides.clear()
    db.close()
    engine.dispose()


def examine(client, prediction_id, bin_id):
    return client.post(f"/predictions/{prediction_id}/bin-examinations", json={"selected_bin_id": bin_id})


def test_available_bins_return_stable_ids(api):
    client, _, _, _, _, correct_bin, wrong_bin = api

    response = client.get("/predictions/bins")

    assert response.status_code == 200
    assert response.json() == [
        {"id": wrong_bin.id, "name": "General Waste", "description": "Non-recyclables"},
        {"id": correct_bin.id, "name": "Mixed Dry Recycling", "description": "Plastic bottles and cans"},
    ]


def test_available_bins_excludes_inactive_bins(api):
    client, db, _, _, _, correct_bin, wrong_bin = api
    wrong_bin.is_active = False
    db.commit()

    response = client.get("/predictions/bins")

    assert response.status_code == 200
    assert response.json() == [
        {"id": correct_bin.id, "name": "Mixed Dry Recycling", "description": "Plastic bottles and cans"},
    ]


def test_correct_bin_is_recorded(api):
    client, db, _, _, prediction, correct_bin, _ = api

    response = examine(client, prediction.id, correct_bin.id)

    assert response.status_code == 201
    assert response.json() == {
        "selected_bin": "Mixed Dry Recycling",
        "is_correct": True,
        "recommended_bin": "Mixed Dry Recycling",
        "guidance": "Empty and rinse, then recycle.",
    }
    stored = db.scalar(_sa.select(_models.BinExamination))
    assert stored.prediction_id == prediction.id
    assert stored.selected_bin_id == correct_bin.id
    assert stored.is_correct is True


def test_incorrect_bin_identifies_the_recommended_bin(api):
    client, _, _, _, prediction, _, wrong_bin = api

    response = examine(client, prediction.id, wrong_bin.id)

    assert response.status_code == 201
    body = response.json()
    assert body["is_correct"] is False
    assert body["recommended_bin"] == "Mixed Dry Recycling"


def test_equivalent_red_sack_bin_is_correct(api):
    client, db, _, _, prediction, _, _ = api
    alternate_red_sack_bin = _models.Bin(name="Plastic & Cans")
    db.add(alternate_red_sack_bin)
    db.commit()

    response = examine(client, prediction.id, alternate_red_sack_bin.id)

    assert response.status_code == 201
    assert response.json()["is_correct"] is True


def test_examination_requires_authentication(api):
    client, _, _, _, prediction, correct_bin, _ = api
    override = _main.app.dependency_overrides.pop(_dependencies.get_current_user)
    try:
        response = examine(client, prediction.id, correct_bin.id)
    finally:
        _main.app.dependency_overrides[_dependencies.get_current_user] = override
    assert response.status_code == 401


def test_nonexistent_prediction_is_rejected(api):
    client, _, _, _, _, correct_bin, _ = api
    assert examine(client, 999, correct_bin.id).status_code == 404


def test_another_users_prediction_is_rejected(api):
    client, db, _, other_user, prediction, correct_bin, _ = api
    other_prediction = _models.Prediction(
        predicted_category_id=prediction.predicted_category_id,
        confidence=0.9,
        chosen_bin_id=correct_bin.id,
        user_id=other_user.id,
    )
    db.add(other_prediction)
    db.commit()

    assert examine(client, other_prediction.id, correct_bin.id).status_code == 404


def test_invalid_bin_is_rejected(api):
    client, _, _, _, prediction, _, _ = api
    assert examine(client, prediction.id, 999).status_code == 400


def test_missing_mapping_is_rejected(api):
    client, db, user, _, _, correct_bin, _ = api
    orphan_category = _models.Category(name="unmapped_category", model_label_index=5)
    db.add(orphan_category)
    db.flush()
    orphan_prediction = _models.Prediction(
        predicted_category_id=orphan_category.id,
        confidence=0.9,
        chosen_bin_id=correct_bin.id,
        user_id=user.id,
    )
    db.add(orphan_prediction)
    db.commit()

    assert examine(client, orphan_prediction.id, correct_bin.id).status_code == 500


def test_missing_selected_bin_id_is_rejected(api):
    client, _, _, _, prediction, _, _ = api
    response = client.post(f"/predictions/{prediction.id}/bin-examinations", json={})
    assert response.status_code == 422


def test_multiple_attempts_are_all_stored(api):
    client, db, _, _, prediction, correct_bin, wrong_bin = api
    examine(client, prediction.id, wrong_bin.id)
    examine(client, prediction.id, correct_bin.id)

    count = db.scalar(_sa.select(_sa.func.count()).select_from(_models.BinExamination))
    assert count == 2
