import datetime as _datetime
import bcrypt as _bcrypt
import jwt as _jwt
import app.config as _config


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return _bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(subject: str) -> str:
    settings = _config.get_settings()
    expires_at = _datetime.datetime.now(_datetime.UTC) + _datetime.timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return _jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def subject_from_token(token: str) -> str | None:
    settings = _config.get_settings()
    try:
        payload = _jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except _jwt.InvalidTokenError:
        return None
    return payload["sub"]
