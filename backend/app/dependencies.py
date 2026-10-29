import typing as _typing
import fastapi as _fastapi
import fastapi.security as _fastapi_security
import sqlalchemy.orm as _orm
import app.database as _database
import app.models as _models
import app.security as _security

Session = _typing.Annotated[_orm.Session, _fastapi.Depends(_database.get_db)]

_bearer = _fastapi_security.HTTPBearer()
_Credentials = _typing.Annotated[_fastapi_security.HTTPAuthorizationCredentials, _fastapi.Depends(_bearer)]


def get_current_user(credentials: _Credentials, db: Session) -> _models.User:
    subject = _security.subject_from_token(credentials.credentials)
    user = db.get(_models.User, int(subject)) if subject is not None else None
    if user is None or not user.is_active:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = _typing.Annotated[_models.User, _fastapi.Depends(get_current_user)]


def get_current_admin(user: CurrentUser) -> _models.User:
    if user.role != "admin":
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


AdminUser = _typing.Annotated[_models.User, _fastapi.Depends(get_current_admin)]
