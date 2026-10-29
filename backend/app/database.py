import functools as _functools
import typing as _typing
import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import app.config as _config


class Base(_orm.DeclarativeBase):
    pass


@_functools.lru_cache
def get_engine() -> _sa.Engine:
    return _sa.create_engine(_config.get_settings().database_url, pool_pre_ping=True)


@_functools.lru_cache
def get_session_factory() -> _orm.sessionmaker:
    return _orm.sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def get_db() -> _typing.Iterator[_orm.Session]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
