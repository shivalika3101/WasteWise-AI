import functools as _functools
import pathlib as _pathlib
import urllib.parse as _parse
import pydantic as _pydantic
import pydantic_settings as _pydantic_settings


class Settings(_pydantic_settings.BaseSettings):
    model_config = _pydantic_settings.SettingsConfigDict(
        env_file=_pathlib.Path(__file__).resolve().parents[1] / ".env",
        extra="ignore",
    )

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str = "waste_app"
    postgres_maintenance_db: str = "postgres"
    postgres_connect_timeout: int = 10
    jwt_secret_key: str = _pydantic.Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    frontend_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    def url_for(self, database: str) -> str:
        user = _parse.quote_plus(self.postgres_user)
        password = _parse.quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg://{user}:{password}@{self.postgres_host}:{self.postgres_port}/{database}"
            f"?connect_timeout={self.postgres_connect_timeout}"
        )

    @property
    def database_url(self) -> str:
        return self.url_for(self.postgres_db)

    @property
    def maintenance_url(self) -> str:
        return self.url_for(self.postgres_maintenance_db)


@_functools.lru_cache
def get_settings() -> Settings:
    return Settings()
