import datetime as _datetime
import jwt as _jwt
import pytest as _pytest
import app.config as _config
import app.models as _models
import app.security as _security

PASSWORD = "correct horse"
SECRET = "k" * 32


@_pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "admin")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "30")
    _config.get_settings.cache_clear()
    yield
    _config.get_settings.cache_clear()


def test_hashing_does_not_store_the_password():
    digest = _security.hash_password(PASSWORD)
    assert digest != PASSWORD
    assert PASSWORD not in digest


def test_a_password_verifies_against_its_own_hash():
    assert _security.verify_password(PASSWORD, _security.hash_password(PASSWORD))


def test_a_wrong_password_does_not_verify():
    digest = _security.hash_password(PASSWORD)
    assert not _security.verify_password("wrong horse", digest)
    assert not _security.verify_password(PASSWORD.upper(), digest)


def test_each_hash_uses_a_fresh_salt():
    first = _security.hash_password(PASSWORD)
    second = _security.hash_password(PASSWORD)
    assert first != second
    assert _security.verify_password(PASSWORD, first)
    assert _security.verify_password(PASSWORD, second)


def test_the_hash_fits_the_password_hash_column():
    length = _models.User.__table__.columns["password_hash"].type.length
    assert len(_security.hash_password(PASSWORD)) <= length


def test_the_longest_allowed_password_is_hashable():
    password = "e" * 72
    assert _security.verify_password(password, _security.hash_password(password))


def test_a_password_over_the_limit_is_refused():
    with _pytest.raises(ValueError):
        _security.hash_password("e" * 73)


def test_a_unicode_password_round_trips():
    password = "zähra-café-🔑"
    assert _security.verify_password(password, _security.hash_password(password))


def test_a_token_round_trips_its_subject():
    assert _security.subject_from_token(_security.create_access_token("7")) == "7"


def test_the_token_carries_the_configured_lifetime(monkeypatch):
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "30")
    _config.get_settings.cache_clear()
    before = _datetime.datetime.now(_datetime.UTC)
    payload = _jwt.decode(_security.create_access_token("7"), SECRET, algorithms=["HS256"])
    expires_at = _datetime.datetime.fromtimestamp(payload["exp"], _datetime.UTC)
    assert _datetime.timedelta(minutes=29) < expires_at - before <= _datetime.timedelta(minutes=30)


def test_an_expired_token_is_rejected(monkeypatch):
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "-1")
    _config.get_settings.cache_clear()
    assert _security.subject_from_token(_security.create_access_token("7")) is None


def test_a_token_signed_with_another_secret_is_rejected():
    forged = _jwt.encode(
        {"sub": "7", "exp": _datetime.datetime.now(_datetime.UTC) + _datetime.timedelta(minutes=30)},
        "a" * 32,
        algorithm="HS256",
    )
    assert _security.subject_from_token(forged) is None


def test_a_tampered_token_is_rejected():
    token = _security.create_access_token("7")
    assert _security.subject_from_token(token[:-4] + "AAAA") is None


def test_an_unsigned_token_is_rejected():
    forged = _jwt.encode({"sub": "7"}, key="", algorithm="none")
    assert _security.subject_from_token(forged) is None


def test_a_token_without_an_expiry_is_rejected():
    eternal = _jwt.encode({"sub": "7"}, SECRET, algorithm="HS256")
    assert _security.subject_from_token(eternal) is None


def test_malformed_tokens_are_rejected():
    for token in ["", "not.a.token", "aaa.bbb.ccc"]:
        assert _security.subject_from_token(token) is None
