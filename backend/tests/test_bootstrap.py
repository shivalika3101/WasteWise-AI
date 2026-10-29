import pytest as _pytest
import sqlalchemy as _sa
import alembic.command as _alembic_command
import app.bootstrap as _bootstrap
import app.config as _config
import app.database as _database

TEST_DATABASE = "waste_app_test"


def postgres_is_available() -> bool:
    try:
        engine = _sa.create_engine(_config.Settings().maintenance_url, isolation_level="AUTOCOMMIT")
    except Exception:
        return False
    try:
        with engine.connect():
            return True
    except Exception:
        return False
    finally:
        engine.dispose()


pytestmark = _pytest.mark.skipif(not postgres_is_available(), reason="PostgreSQL is not running")


def drop_test_database():
    engine = _sa.create_engine(_config.Settings().maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(_sa.text(f'DROP DATABASE IF EXISTS "{TEST_DATABASE}" WITH (FORCE)'))
    finally:
        engine.dispose()


def clear_caches():
    _config.get_settings.cache_clear()
    _database.get_engine.cache_clear()
    _database.get_session_factory.cache_clear()


def current_version() -> str | None:
    with _database.get_engine().connect() as connection:
        return connection.scalar(_sa.text("SELECT version_num FROM alembic_version"))


def table_names() -> set[str]:
    return set(_sa.inspect(_database.get_engine()).get_table_names())


@_pytest.fixture
def scratch_database(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", TEST_DATABASE)
    clear_caches()
    drop_test_database()
    yield
    _database.get_engine().dispose()
    clear_caches()
    drop_test_database()


def test_fresh_start_creates_the_database_and_migrates(scratch_database):
    assert not _bootstrap.database_exists(_config.get_settings())
    _bootstrap.run()
    assert _bootstrap.database_exists(_config.get_settings())
    assert {"categories", "bins", "category_bins", "disposal_instructions", "predictions"} <= table_names()
    assert current_version() is not None


def test_restart_changes_nothing(scratch_database):
    _bootstrap.run()
    version = current_version()
    tables = table_names()
    _bootstrap.run()
    assert current_version() == version
    assert table_names() == tables


def test_existing_database_is_adopted_without_losing_data(scratch_database):
    settings = _config.get_settings()
    _bootstrap.create_database(settings)
    _alembic_command.upgrade(_bootstrap.alembic_config(), "head")
    with _database.get_engine().begin() as connection:
        connection.execute(_sa.text("DROP TABLE alembic_version"))
        connection.execute(_sa.text("INSERT INTO bins (name, colour) VALUES ('Existing Bin', 'green')"))

    assert "alembic_version" not in table_names()
    _bootstrap.run()

    assert current_version() is not None
    with _database.get_engine().connect() as connection:
        assert connection.scalar(_sa.text("SELECT count(*) FROM bins")) == 1
        assert connection.scalar(_sa.text("SELECT name FROM bins")) == "Existing Bin"


def test_an_empty_existing_database_is_migrated(scratch_database):
    _bootstrap.create_database(_config.get_settings())
    assert table_names() == set()
    _bootstrap.run()
    assert {"categories", "bins"} <= table_names()
    assert current_version() is not None


def test_unreachable_database_raises(monkeypatch):
    monkeypatch.setenv("POSTGRES_PORT", "5999")
    monkeypatch.setenv("POSTGRES_CONNECT_TIMEOUT", "1")
    clear_caches()
    try:
        with _pytest.raises(_sa.exc.OperationalError):
            _bootstrap.run()
    finally:
        clear_caches()


def test_wrong_credentials_raise(monkeypatch):
    monkeypatch.setenv("POSTGRES_PASSWORD", "definitely-not-the-password")
    clear_caches()
    try:
        with _pytest.raises(_sa.exc.OperationalError):
            _bootstrap.run()
    finally:
        clear_caches()
