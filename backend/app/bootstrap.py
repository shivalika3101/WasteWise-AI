import pathlib as _pathlib
import re as _re
import alembic.command as _alembic_command
import alembic.config as _alembic_config
import alembic.script as _alembic_script
import sqlalchemy as _sa
import app.config as _config
import app.database as _database

_CREATE_TABLE_PATTERN = _re.compile(r"op\.create_table\(\s*['\"](\w+)['\"]")
_ADD_COLUMN_PATTERN = _re.compile(
    r"op\.add_column\(\s*['\"](\w+)['\"]\s*,\s*sa\.Column\(\s*['\"](\w+)['\"]",
    _re.DOTALL,
)
_CREATE_INDEX_PATTERN = _re.compile(
    r"op\.create_index\(\s*(?:op\.f\()?['\"](\w+)['\"]\)?\s*,\s*['\"](\w+)['\"]",
    _re.DOTALL,
)
_CREATE_FOREIGN_KEY_PATTERN = _re.compile(
    r"op\.create_foreign_key\(\s*['\"](\w+)['\"]\s*,\s*['\"](\w+)['\"]",
    _re.DOTALL,
)


def alembic_config() -> _alembic_config.Config:
    config = _alembic_config.Config(str(_pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"))
    config.attributes["configure_logger"] = False
    return config


def base_revision(config: _alembic_config.Config) -> str:
    script = _alembic_script.ScriptDirectory.from_config(config)
    return next(revision.revision for revision in script.walk_revisions() if revision.down_revision is None)


def revisions_oldest_first(config: _alembic_config.Config) -> list:
    script = _alembic_script.ScriptDirectory.from_config(config)
    return list(reversed(list(script.walk_revisions())))


def schema_changes_created_by(revision) -> dict[str, set]:
    source = _pathlib.Path(revision.module.__file__).read_text()
    return {
        "tables": set(_CREATE_TABLE_PATTERN.findall(source)),
        "columns": set(_ADD_COLUMN_PATTERN.findall(source)),
        "indexes": {(table, name) for name, table in _CREATE_INDEX_PATTERN.findall(source)},
        "foreign_keys": {(table, name) for name, table in _CREATE_FOREIGN_KEY_PATTERN.findall(source)},
    }


def schema_change_presence(inspector, changes: dict[str, set]) -> list[bool]:
    tables = set(inspector.get_table_names())
    presence = [table in tables for table in changes["tables"]]
    for table, column in changes["columns"]:
        columns = {item["name"] for item in inspector.get_columns(table)} if table in tables else set()
        presence.append(column in columns)
    for table, index in changes["indexes"]:
        indexes = {item["name"] for item in inspector.get_indexes(table)} if table in tables else set()
        presence.append(index in indexes)
    for table, foreign_key in changes["foreign_keys"]:
        foreign_keys = {item["name"] for item in inspector.get_foreign_keys(table)} if table in tables else set()
        presence.append(foreign_key in foreign_keys)
    return presence


def matching_revision(engine: _sa.Engine, config: _alembic_config.Config) -> str:
    inspector = _sa.inspect(engine)
    revisions = revisions_oldest_first(config)
    matched = None
    for revision in revisions:
        presence = schema_change_presence(inspector, schema_changes_created_by(revision))
        if all(presence):
            matched = revision.revision
            continue
        if any(presence):
            raise RuntimeError(f"Database schema only partially matches Alembic revision {revision.revision}")
        if matched is None:
            raise RuntimeError("Existing database does not match the Alembic baseline schema")
        break
    return matched


def database_exists(settings: _config.Settings) -> bool:
    engine = _sa.create_engine(settings.maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            statement = _sa.text("SELECT 1 FROM pg_database WHERE datname = :name")
            return connection.scalar(statement, {"name": settings.postgres_db}) is not None
    finally:
        engine.dispose()


def create_database(settings: _config.Settings) -> None:
    engine = _sa.create_engine(settings.maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            name = engine.dialect.identifier_preparer.quote(settings.postgres_db)
            connection.execute(_sa.text(f"CREATE DATABASE {name}"))
    finally:
        engine.dispose()


def has_unmanaged_tables(engine: _sa.Engine) -> bool:
    tables = set(_sa.inspect(engine).get_table_names())
    return bool(tables) and "alembic_version" not in tables


def run() -> None:
    settings = _config.get_settings()
    if not database_exists(settings):
        create_database(settings)
    config = alembic_config()
    engine = _database.get_engine()
    if has_unmanaged_tables(engine):
        _alembic_command.stamp(config, matching_revision(engine, config))
    _alembic_command.upgrade(config, "head")
