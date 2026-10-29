import secrets as _secrets
import fastapi as _fastapi
import sqlalchemy as _sa
import app.dependencies as _dependencies
import app.models as _models
import app.schemas as _schemas
import app.security as _security

_UNKNOWN_USER_HASH = _security.hash_password(_secrets.token_urlsafe(32))

router = _fastapi.APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=_schemas.UserRead, status_code=_fastapi.status.HTTP_201_CREATED)
def register(payload: _schemas.UserCreate, db: _dependencies.Session):
    user = _models.User(email=payload.email, password_hash=_security.hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except _sa.exc.IntegrityError:
        db.rollback()
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    db.refresh(user)
    return user


@router.post("/login", response_model=_schemas.Token)
def login(payload: _schemas.UserLogin, db: _dependencies.Session):
    user = db.scalar(_sa.select(_models.User).where(_models.User.email == payload.email))
    matches = _security.verify_password(payload.password, user.password_hash if user else _UNKNOWN_USER_HASH)
    if user is None or not matches:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return _schemas.Token(access_token=_security.create_access_token(str(user.id)))


@router.post("/logout", status_code=_fastapi.status.HTTP_204_NO_CONTENT)
def logout(user: _dependencies.CurrentUser):
    return None
