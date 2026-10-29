import datetime as _datetime
import pydantic as _pydantic
import pytest as _pytest
import app.models as _models
import app.schemas as _schemas


def test_registration_accepts_a_valid_email_and_password():
    user = _schemas.UserCreate(email="zahra@example.com", password="correct horse")
    assert user.email == "zahra@example.com"


def test_registration_rejects_a_malformed_email():
    with _pytest.raises(_pydantic.ValidationError):
        _schemas.UserCreate(email="zahra", password="correct horse")


def test_registration_rejects_a_short_password():
    with _pytest.raises(_pydantic.ValidationError):
        _schemas.UserCreate(email="zahra@example.com", password="short")


def test_registration_rejects_a_password_over_the_bcrypt_limit():
    with _pytest.raises(_pydantic.ValidationError):
        _schemas.UserCreate(email="zahra@example.com", password="e" * 73)


def test_registration_measures_the_password_in_bytes():
    with _pytest.raises(_pydantic.ValidationError):
        _schemas.UserCreate(email="zahra@example.com", password="é" * 37)


def test_registration_lowercases_the_whole_address():
    user = _schemas.UserCreate(email="Zahra@EXAMPLE.COM", password="correct horse")
    assert user.email == "zahra@example.com"


def test_login_lowercases_the_address_the_same_way():
    credentials = _schemas.UserLogin(email="ZAHRA@Example.Com", password="correct horse")
    assert credentials.email == "zahra@example.com"


def test_registration_and_login_agree_on_the_stored_identity():
    user = _schemas.UserCreate(email="Zahra@Example.com", password="correct horse")
    credentials = _schemas.UserLogin(email="zahra@EXAMPLE.COM", password="correct horse")
    assert user.email == credentials.email


def test_login_does_not_impose_registration_rules():
    credentials = _schemas.UserLogin(email="zahra@example.com", password="x")
    assert credentials.password == "x"


def test_registration_ignores_a_role_field():
    user = _schemas.UserCreate(email="zahra@example.com", password="correct horse", role="admin")
    assert not hasattr(user, "role")


def test_user_read_declares_only_safe_fields():
    assert set(_schemas.UserRead.model_fields) == {"id", "email", "role", "created_at"}


def test_user_read_drops_the_password_hash_of_an_orm_user():
    user = _models.User(
        id=1,
        email="zahra@example.com",
        password_hash="$2b$12$notarealhash",
        role="user",
        created_at=_datetime.datetime(2026, 7, 19, 12, 0),
    )
    payload = _schemas.UserRead.model_validate(user).model_dump()
    assert payload == {
        "id": 1,
        "email": "zahra@example.com",
        "role": "user",
        "created_at": _datetime.datetime(2026, 7, 19, 12, 0),
    }


def test_token_defaults_to_the_bearer_type():
    assert _schemas.Token(access_token="a.b.c").token_type == "bearer"


def test_prediction_response_has_the_api_contract():
    assert set(_schemas.PredictionRead.model_fields) == {
        "prediction_id",
        "category",
        "confidence",
        "bin",
        "guidance",
    }


def test_prediction_response_rejects_an_invalid_confidence():
    with _pytest.raises(_pydantic.ValidationError):
        _schemas.PredictionRead(
            prediction_id=1,
            category="Plastic water bottle",
            confidence=1.1,
            bin="Mixed Dry Recycling",
            guidance="Empty and rinse, then recycle.",
        )


def test_prediction_history_response_declares_only_safe_fields():
    assert set(_schemas.PredictionHistoryRead.model_fields) == {
        "prediction_id",
        "category",
        "confidence",
        "bin",
        "guidance",
        "created_at",
    }
