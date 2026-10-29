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

    admin = _models.User(email="admin@example.com", password_hash="not-used", role="admin")
    member = _models.User(email="member@example.com", password_hash="not-used")
    category = _models.Category(name="plastic_water_bottles", display_name="Plastic water bottle", model_label_index=24)
    bin_record = _models.Bin(name="Mixed Dry Recycling", colour="green", description="Plastic bottles and cans")
    db.add_all([admin, member, category, bin_record])
    db.flush()
    db.add_all(
        [
            _models.CategoryBin(category_id=category.id, bin_id=bin_record.id, is_primary=True),
            _models.DisposalInstruction(category_id=category.id, instructions="Empty and rinse, then recycle."),
        ]
    )
    prediction = _models.Prediction(
        predicted_category_id=category.id,
        confidence=0.9,
        chosen_bin_id=bin_record.id,
        user_id=member.id,
    )
    db.add(prediction)
    db.commit()

    def get_db():
        yield db

    def get_current_user():
        return admin

    _main.app.dependency_overrides[_database.get_db] = get_db
    _main.app.dependency_overrides[_dependencies.get_current_user] = get_current_user
    client = _testclient.TestClient(_main.app)
    yield client, db, admin, member, prediction
    _main.app.dependency_overrides.clear()
    db.close()
    engine.dispose()


def as_user(user):
    def get_current_user():
        return user

    _main.app.dependency_overrides[_dependencies.get_current_user] = get_current_user


def test_admin_can_list_users(api):
    client, _, admin, member, _ = api
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert {row["email"] for row in response.json()} == {admin.email, member.email}


def test_admin_user_list_never_exposes_password_hashes(api):
    client, *_ = api
    assert "password_hash" not in client.get("/admin/users").text


def test_admin_can_view_a_single_user(api):
    client, _, _, member, _ = api
    response = client.get(f"/admin/users/{member.id}")
    assert response.status_code == 200
    assert response.json()["email"] == member.email
    assert response.json()["is_active"] is True


def test_viewing_a_missing_user_is_rejected(api):
    client, *_ = api
    assert client.get("/admin/users/999").status_code == 404


def test_admin_can_view_a_users_predictions(api):
    client, _, _, member, prediction = api
    response = client.get(f"/admin/users/{member.id}/predictions")
    assert response.status_code == 200
    assert [row["prediction_id"] for row in response.json()] == [prediction.id]


def test_predictions_for_a_missing_user_are_rejected(api):
    client, *_ = api
    assert client.get("/admin/users/999/predictions").status_code == 404


def test_admin_can_deactivate_a_user(api):
    client, db, _, member, _ = api
    response = client.post(f"/admin/users/{member.id}/deactivate")
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    db.refresh(member)
    assert member.is_active is False


def test_admin_can_reactivate_a_user(api):
    client, db, _, member, _ = api
    client.post(f"/admin/users/{member.id}/deactivate")
    response = client.post(f"/admin/users/{member.id}/reactivate")
    assert response.status_code == 200
    assert response.json()["is_active"] is True
    db.refresh(member)
    assert member.is_active is True


def test_deactivating_a_missing_user_is_rejected(api):
    client, *_ = api
    assert client.post("/admin/users/999/deactivate").status_code == 404


def test_reactivating_a_missing_user_is_rejected(api):
    client, *_ = api
    assert client.post("/admin/users/999/reactivate").status_code == 404


def test_admin_can_create_a_bin(api):
    client, db, *_ = api
    response = client.post("/admin/bins", json={"name": "Compost", "colour": "brown", "description": "Food waste"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Compost"
    assert body["is_active"] is True
    assert db.scalar(_sa.select(_sa.func.count()).select_from(_models.Bin).where(_models.Bin.name == "Compost")) == 1


def test_creating_a_duplicate_bin_name_is_rejected(api):
    client, *_ = api
    client.post("/admin/bins", json={"name": "Compost"})
    assert client.post("/admin/bins", json={"name": "Compost"}).status_code == 409


def test_admin_can_list_bins(api):
    client, *_ = api
    client.post("/admin/bins", json={"name": "Compost"})
    assert "Compost" in {row["name"] for row in client.get("/admin/bins").json()}


def test_admin_can_update_a_bin(api):
    client, *_ = api
    bin_id = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    response = client.patch(f"/admin/bins/{bin_id}", json={"colour": "brown"})
    assert response.status_code == 200
    assert response.json()["colour"] == "brown"
    assert response.json()["name"] == "Compost"


def test_renaming_a_bin_to_an_existing_name_is_rejected(api):
    client, *_ = api
    client.post("/admin/bins", json={"name": "Compost"})
    other_id = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    assert client.patch(f"/admin/bins/{other_id}", json={"name": "Compost"}).status_code == 409


def test_updating_a_missing_bin_is_rejected(api):
    client, *_ = api
    assert client.patch("/admin/bins/999", json={"colour": "brown"}).status_code == 404


def test_admin_can_deactivate_and_reactivate_a_bin(api):
    client, *_ = api
    bin_id = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    assert client.post(f"/admin/bins/{bin_id}/deactivate").json()["is_active"] is False
    assert client.post(f"/admin/bins/{bin_id}/reactivate").json()["is_active"] is True


def test_deactivating_a_missing_bin_is_rejected(api):
    client, *_ = api
    assert client.post("/admin/bins/999/deactivate").status_code == 404


def test_admin_can_hard_delete_an_unreferenced_bin(api):
    client, db, *_ = api
    bin_id = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    response = client.delete(f"/admin/bins/{bin_id}")
    assert response.status_code == 204
    assert db.get(_models.Bin, bin_id) is None


def test_deleting_a_missing_bin_is_rejected(api):
    client, *_ = api
    assert client.delete("/admin/bins/999").status_code == 404


def test_deleting_a_bin_referenced_by_a_mapping_is_rejected(api):
    client, db, _, member, _ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.flush()
    bin_id = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    db.add(_models.CategoryBin(category_id=category.id, bin_id=bin_id))
    db.commit()

    response = client.delete(f"/admin/bins/{bin_id}")

    assert response.status_code == 409
    assert db.get(_models.Bin, bin_id) is not None


def test_deleting_a_bin_referenced_only_by_a_prediction_is_rejected(api):
    client, db, _, member, _ = api
    bin_id = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.flush()
    db.add(
        _models.Prediction(predicted_category_id=category.id, confidence=0.5, chosen_bin_id=bin_id, user_id=member.id)
    )
    db.commit()

    response = client.delete(f"/admin/bins/{bin_id}")

    assert response.status_code == 409
    assert db.get(_models.Bin, bin_id) is not None


def test_admin_can_create_a_disposal_instruction(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()

    response = client.post(
        "/admin/disposal-instructions",
        json={"category_id": category.id, "instructions": "Rinse and recycle.", "notes": "Remove lids."},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["instructions"] == "Rinse and recycle."
    assert body["is_active"] is True


def test_creating_a_disposal_instruction_for_a_missing_category_is_rejected(api):
    client, *_ = api
    response = client.post(
        "/admin/disposal-instructions",
        json={"category_id": 999, "instructions": "Rinse and recycle."},
    )
    assert response.status_code == 400


def test_admin_can_list_disposal_instructions(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    client.post("/admin/disposal-instructions", json={"category_id": category.id, "instructions": "Rinse."})

    response = client.get("/admin/disposal-instructions")

    assert response.status_code == 200
    assert "Rinse." in {row["instructions"] for row in response.json()}


def test_admin_can_update_a_disposal_instruction(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    instruction_id = client.post(
        "/admin/disposal-instructions", json={"category_id": category.id, "instructions": "Rinse."}
    ).json()["id"]

    response = client.patch(f"/admin/disposal-instructions/{instruction_id}", json={"notes": "Remove lids."})

    assert response.status_code == 200
    assert response.json()["notes"] == "Remove lids."
    assert response.json()["instructions"] == "Rinse."


def test_updating_a_missing_disposal_instruction_is_rejected(api):
    client, *_ = api
    assert client.patch("/admin/disposal-instructions/999", json={"notes": "x"}).status_code == 404


def test_admin_can_deactivate_and_reactivate_a_disposal_instruction(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    instruction_id = client.post(
        "/admin/disposal-instructions", json={"category_id": category.id, "instructions": "Rinse."}
    ).json()["id"]

    assert client.post(f"/admin/disposal-instructions/{instruction_id}/deactivate").json()["is_active"] is False
    assert client.post(f"/admin/disposal-instructions/{instruction_id}/reactivate").json()["is_active"] is True


def test_deactivating_a_missing_disposal_instruction_is_rejected(api):
    client, *_ = api
    assert client.post("/admin/disposal-instructions/999/deactivate").status_code == 404


def test_admin_can_list_categories(api):
    client, *_ = api
    response = client.get("/admin/categories")
    assert response.status_code == 200
    assert "plastic_water_bottles" in {row["name"] for row in response.json()}


def test_admin_can_create_a_category_bin_mapping(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    bin_id = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]

    response = client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id})

    assert response.status_code == 201
    body = response.json()
    assert body["category_id"] == category.id
    assert body["bin_id"] == bin_id
    assert body["is_primary"] is False


def test_creating_a_mapping_for_a_missing_category_is_rejected(api):
    client, *_ = api
    bin_id = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    response = client.post("/admin/category-bins", json={"category_id": 999, "bin_id": bin_id})
    assert response.status_code == 400


def test_creating_a_mapping_for_a_missing_bin_is_rejected(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    response = client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": 999})
    assert response.status_code == 400


def test_duplicate_category_bin_mapping_is_rejected(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    bin_id = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id})

    response = client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id})

    assert response.status_code == 409


def test_a_second_primary_mapping_for_the_same_category_is_rejected(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    first_bin = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    second_bin = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": first_bin, "is_primary": True})

    response = client.post(
        "/admin/category-bins", json={"category_id": category.id, "bin_id": second_bin, "is_primary": True}
    )

    assert response.status_code == 409


def test_admin_can_promote_a_mapping_to_primary_once_the_old_one_is_unset(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    first_bin = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    second_bin = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    first_mapping_id = client.post(
        "/admin/category-bins", json={"category_id": category.id, "bin_id": first_bin, "is_primary": True}
    ).json()["id"]
    second_mapping_id = client.post(
        "/admin/category-bins", json={"category_id": category.id, "bin_id": second_bin}
    ).json()["id"]

    client.patch(f"/admin/category-bins/{first_mapping_id}", json={"is_primary": False})
    response = client.patch(f"/admin/category-bins/{second_mapping_id}", json={"is_primary": True})

    assert response.status_code == 200
    assert response.json()["is_primary"] is True


def test_updating_a_missing_mapping_is_rejected(api):
    client, *_ = api
    assert client.patch("/admin/category-bins/999", json={"is_primary": True}).status_code == 404


def test_admin_can_delete_a_mapping(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    bin_id = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    mapping_id = client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id}).json()["id"]

    response = client.delete(f"/admin/category-bins/{mapping_id}")

    assert response.status_code == 204
    assert db.get(_models.CategoryBin, mapping_id) is None


def test_deleting_a_missing_mapping_is_rejected(api):
    client, *_ = api
    assert client.delete("/admin/category-bins/999").status_code == 404


def test_deactivating_a_bins_primary_category_mapping_is_rejected(api):
    client, db, _, member, prediction = api
    response = client.post(f"/admin/bins/{prediction.chosen_bin_id}/deactivate")
    assert response.status_code == 409
    assert db.get(_models.Bin, prediction.chosen_bin_id).is_active is True


def test_deactivating_a_non_primary_bin_still_works(api):
    client, *_ = api
    bin_id = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    assert client.post(f"/admin/bins/{bin_id}/deactivate").status_code == 200


def test_a_normal_user_is_forbidden_from_every_admin_route(api):
    client, db, _, member, _ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    instruction_id = client.post(
        "/admin/disposal-instructions", json={"category_id": category.id, "instructions": "Rinse."}
    ).json()["id"]
    bin_id = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    mapping_id = client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id}).json()["id"]

    as_user(member)
    assert client.get("/admin/users").status_code == 403
    assert client.get(f"/admin/users/{member.id}").status_code == 403
    assert client.get(f"/admin/users/{member.id}/predictions").status_code == 403
    assert client.post(f"/admin/users/{member.id}/deactivate").status_code == 403
    assert client.post(f"/admin/users/{member.id}/reactivate").status_code == 403
    assert client.get("/admin/bins").status_code == 403
    assert client.post("/admin/bins", json={"name": "Landfill"}).status_code == 403
    assert client.patch(f"/admin/bins/{bin_id}", json={"colour": "grey"}).status_code == 403
    assert client.post(f"/admin/bins/{bin_id}/deactivate").status_code == 403
    assert client.post(f"/admin/bins/{bin_id}/reactivate").status_code == 403
    assert client.delete(f"/admin/bins/{bin_id}").status_code == 403
    assert client.get("/admin/disposal-instructions").status_code == 403
    assert client.post(
        "/admin/disposal-instructions", json={"category_id": category.id, "instructions": "x"}
    ).status_code == 403
    assert client.patch(f"/admin/disposal-instructions/{instruction_id}", json={"notes": "x"}).status_code == 403
    assert client.post(f"/admin/disposal-instructions/{instruction_id}/deactivate").status_code == 403
    assert client.post(f"/admin/disposal-instructions/{instruction_id}/reactivate").status_code == 403
    assert client.get("/admin/categories").status_code == 403
    assert client.get("/admin/category-bins").status_code == 403
    assert client.post(
        "/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id}
    ).status_code == 403
    assert client.patch(f"/admin/category-bins/{mapping_id}", json={"is_primary": True}).status_code == 403
    assert client.delete(f"/admin/category-bins/{mapping_id}").status_code == 403


def test_an_unauthenticated_request_is_rejected_from_every_admin_route(api):
    client, db, _, member, _ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    instruction_id = client.post(
        "/admin/disposal-instructions", json={"category_id": category.id, "instructions": "Rinse."}
    ).json()["id"]
    bin_id = client.post("/admin/bins", json={"name": "Compost"}).json()["id"]
    mapping_id = client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id}).json()["id"]

    override = _main.app.dependency_overrides.pop(_dependencies.get_current_user)
    try:
        assert client.get("/admin/users").status_code == 401
        assert client.get(f"/admin/users/{member.id}").status_code == 401
        assert client.get(f"/admin/users/{member.id}/predictions").status_code == 401
        assert client.post(f"/admin/users/{member.id}/deactivate").status_code == 401
        assert client.post(f"/admin/users/{member.id}/reactivate").status_code == 401
        assert client.get("/admin/bins").status_code == 401
        assert client.post("/admin/bins", json={"name": "Landfill"}).status_code == 401
        assert client.patch(f"/admin/bins/{bin_id}", json={"colour": "grey"}).status_code == 401
        assert client.post(f"/admin/bins/{bin_id}/deactivate").status_code == 401
        assert client.post(f"/admin/bins/{bin_id}/reactivate").status_code == 401
        assert client.delete(f"/admin/bins/{bin_id}").status_code == 401
        assert client.get("/admin/disposal-instructions").status_code == 401
        assert client.post(
            "/admin/disposal-instructions", json={"category_id": category.id, "instructions": "x"}
        ).status_code == 401
        assert client.patch(f"/admin/disposal-instructions/{instruction_id}", json={"notes": "x"}).status_code == 401
        assert client.post(f"/admin/disposal-instructions/{instruction_id}/deactivate").status_code == 401
        assert client.post(f"/admin/disposal-instructions/{instruction_id}/reactivate").status_code == 401
        assert client.get("/admin/categories").status_code == 401
        assert client.get("/admin/category-bins").status_code == 401
        assert client.post(
            "/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id}
        ).status_code == 401
        assert client.patch(f"/admin/category-bins/{mapping_id}", json={"is_primary": True}).status_code == 401
        assert client.delete(f"/admin/category-bins/{mapping_id}").status_code == 401
    finally:
        _main.app.dependency_overrides[_dependencies.get_current_user] = override


def test_creating_a_bin_without_a_name_is_rejected(api):
    client, *_ = api
    assert client.post("/admin/bins", json={}).status_code == 422


def test_creating_a_disposal_instruction_without_instructions_is_rejected(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    response = client.post("/admin/disposal-instructions", json={"category_id": category.id})
    assert response.status_code == 422


def test_creating_a_mapping_without_a_bin_id_is_rejected(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    response = client.post("/admin/category-bins", json={"category_id": category.id})
    assert response.status_code == 422


def test_updating_a_mapping_without_is_primary_is_rejected(api):
    client, db, *_ = api
    category = _models.Category(name="glass_bottles", model_label_index=99)
    db.add(category)
    db.commit()
    bin_id = client.post("/admin/bins", json={"name": "Landfill"}).json()["id"]
    mapping_id = client.post("/admin/category-bins", json={"category_id": category.id, "bin_id": bin_id}).json()["id"]

    assert client.patch(f"/admin/category-bins/{mapping_id}", json={}).status_code == 422
