import fastapi as _fastapi
import pytest as _pytest
import app.dependencies as _dependencies
import app.models as _models


def user_with_role(role: str) -> _models.User:
    return _models.User(id=1, email="zahra@example.com", password_hash="not-used", role=role)


def test_an_admin_passes_through():
    admin = user_with_role("admin")
    assert _dependencies.get_current_admin(admin) is admin


def test_a_normal_user_is_forbidden():
    with _pytest.raises(_fastapi.HTTPException) as excinfo:
        _dependencies.get_current_admin(user_with_role("user"))
    assert excinfo.value.status_code == 403


def test_an_unrecognised_role_is_forbidden():
    with _pytest.raises(_fastapi.HTTPException) as excinfo:
        _dependencies.get_current_admin(user_with_role("superadmin"))
    assert excinfo.value.status_code == 403
