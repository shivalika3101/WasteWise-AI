import fastapi as _fastapi
import app.dependencies as _dependencies
import app.schemas as _schemas

router = _fastapi.APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=_schemas.UserRead)
def read_current_user(user: _dependencies.CurrentUser):
    return user
