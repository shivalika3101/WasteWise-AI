import logging.config as _logging_config
import alembic.context as _context
import sqlalchemy as _sa
import app.config as _config
import app.database as _database
import app.models as _models


config = _context.config

if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    _logging_config.fileConfig(config.config_file_name)

target_metadata = _database.Base.metadata


def run_migrations_offline() -> None:
    _context.configure(
        url=_config.get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with _context.begin_transaction():
        _context.run_migrations()


def run_migrations_online() -> None:
    connectable = _sa.create_engine(_config.get_settings().database_url, poolclass=_sa.pool.NullPool)
    with connectable.connect() as connection:
        _context.configure(connection=connection, target_metadata=target_metadata)
        with _context.begin_transaction():
            _context.run_migrations()


if _context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
