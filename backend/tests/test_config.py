import pytest as _pytest
import pydantic as _pydantic
import app.config as _config


@_pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_USER", "admin")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")
    monkeypatch.setenv("POSTGRES_DB", "waste_app")
    monkeypatch.setenv("POSTGRES_MAINTENANCE_DB", "postgres")
    monkeypatch.setenv("POSTGRES_CONNECT_TIMEOUT", "10")
    monkeypatch.setenv("JWT_SECRET_KEY", "k" * 32)
    _config.get_settings.cache_clear()
    yield
    _config.get_settings.cache_clear()


def test_settings_from_environment():
    settings = _config.get_settings()
    assert settings.postgres_user == "admin"
    assert settings.postgres_port == 5432
    assert settings.postgres_db == "waste_app"


def test_database_url():
    assert _config.get_settings().database_url == "postgresql+psycopg://admin:password@localhost:5432/waste_app?connect_timeout=10"


def test_maintenance_url():
    assert _config.get_settings().maintenance_url == "postgresql+psycopg://admin:password@localhost:5432/postgres?connect_timeout=10"


def test_credentials_are_escaped(monkeypatch):
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss word/1")
    _config.get_settings.cache_clear()
    assert _config.get_settings().database_url == "postgresql+psycopg://admin:p%40ss+word%2F1@localhost:5432/waste_app?connect_timeout=10"


def test_connect_timeout_is_configurable(monkeypatch):
    monkeypatch.setenv("POSTGRES_CONNECT_TIMEOUT", "3")
    _config.get_settings.cache_clear()
    assert _config.get_settings().database_url.endswith("?connect_timeout=3")


def test_invalid_port_is_rejected(monkeypatch):
    monkeypatch.setenv("POSTGRES_PORT", "not-a-port")
    with _pytest.raises(_pydantic.ValidationError):
        _config.Settings(_env_file=None)


def test_missing_credentials_are_rejected(monkeypatch):
    monkeypatch.delenv("POSTGRES_USER")
    monkeypatch.delenv("POSTGRES_PASSWORD")
    with _pytest.raises(_pydantic.ValidationError):
        _config.Settings(_env_file=None)


def test_token_defaults():
    settings = _config.get_settings()
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_expire_minutes == 30


def test_missing_secret_key_is_rejected(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY")
    with _pytest.raises(_pydantic.ValidationError):
        _config.Settings(_env_file=None)


def test_short_secret_key_is_rejected(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "k" * 31)
    with _pytest.raises(_pydantic.ValidationError):
        _config.Settings(_env_file=None)


def test_settings_are_cached():
    assert _config.get_settings() is _config.get_settings()
