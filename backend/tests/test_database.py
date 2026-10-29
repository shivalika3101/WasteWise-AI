import pytest as _pytest
import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import app.config as _config
import app.database as _database


@_pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_USER", "admin")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")
    monkeypatch.setenv("POSTGRES_DB", "waste_app")
    monkeypatch.setenv("JWT_SECRET_KEY", "k" * 32)
    _config.get_settings.cache_clear()
    _database.get_engine.cache_clear()
    _database.get_session_factory.cache_clear()
    yield
    _config.get_settings.cache_clear()
    _database.get_engine.cache_clear()
    _database.get_session_factory.cache_clear()


def test_engine_uses_the_application_database():
    url = _database.get_engine().url
    assert url.drivername == "postgresql+psycopg"
    assert url.database == "waste_app"


def test_engine_is_cached():
    assert _database.get_engine() is _database.get_engine()


def test_session_factory_is_bound_to_the_engine():
    assert _database.get_session_factory().kw["bind"] is _database.get_engine()


def test_base_is_declarative():
    assert issubclass(_database.Base, _orm.DeclarativeBase)
    assert isinstance(_database.Base.metadata, _sa.MetaData)


def test_get_db_yields_a_bound_session():
    generator = _database.get_db()
    session = next(generator)
    assert isinstance(session, _orm.Session)
    assert session.get_bind() is _database.get_engine()
    generator.close()


def test_get_db_closes_the_session(monkeypatch):
    generator = _database.get_db()
    session = next(generator)
    closed = []
    monkeypatch.setattr(session, "close", lambda: closed.append(True))
    with _pytest.raises(StopIteration):
        next(generator)
    assert closed == [True]
