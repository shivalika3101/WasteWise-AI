import logging as _logging

import fastapi.testclient as _testclient
import pytest as _pytest
import sqlalchemy as _sa
import app.bootstrap as _bootstrap
import app.config as _config
import app.database as _database
import app.main as _main
import app.security as _security

TEST_DATABASE = "waste_app_auth_test"
EMAIL = "zahra@example.com"
PASSWORD = "correct horse"


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


@_pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", TEST_DATABASE)
    monkeypatch.setenv("JWT_SECRET_KEY", "k" * 32)
    clear_caches()
    drop_test_database()
    _bootstrap.run()
    yield _testclient.TestClient(_main.app)
    _database.get_engine().dispose()
    clear_caches()
    drop_test_database()


def register(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/register", json={"email": email, "password": password})


def login(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def stored_hash(email=EMAIL) -> str:
    with _database.get_engine().connect() as connection:
        return connection.scalar(_sa.text("SELECT password_hash FROM users WHERE email = :email"), {"email": email})


def stored_role(email=EMAIL) -> str:
    with _database.get_engine().connect() as connection:
        return connection.scalar(_sa.text("SELECT role FROM users WHERE email = :email"), {"email": email})


def test_registration_returns_the_safe_user(client):
    response = register(client)
    assert response.status_code == 201
    assert set(response.json()) == {"id", "email", "role", "created_at"}
    assert response.json()["email"] == EMAIL


def test_registration_never_returns_the_password(client):
    body = register(client).text
    assert PASSWORD not in body
    assert "password_hash" not in body


def test_registration_stores_a_hash_not_the_password(client):
    register(client)
    digest = stored_hash()
    assert digest != PASSWORD
    assert digest.startswith("$2b$")
    assert _security.verify_password(PASSWORD, digest)


def test_a_duplicate_email_is_rejected(client):
    register(client)
    response = register(client)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_a_duplicate_email_in_another_case_is_rejected(client):
    register(client)
    response = register(client, email="ZAHRA@Example.COM")
    assert response.status_code == 409


def test_a_rejected_duplicate_leaves_one_user(client):
    register(client)
    register(client, password="a different password")
    with _database.get_engine().connect() as connection:
        assert connection.scalar(_sa.text("SELECT count(*) FROM users")) == 1
    assert _security.verify_password(PASSWORD, stored_hash())


def test_registration_ignores_a_role_in_the_request_body(client):
    response = client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD, "role": "admin"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "user"
    assert stored_role() == "user"


def test_registration_rejects_a_malformed_email(client):
    assert register(client, email="zahra").status_code == 422


def test_registration_rejects_a_short_password(client):
    assert register(client, password="short").status_code == 422


def test_login_returns_a_bearer_token(client):
    register(client)
    response = login(client)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_the_token_identifies_the_registered_user(client):
    user_id = register(client).json()["id"]
    token = login(client).json()["access_token"]
    assert _security.subject_from_token(token) == str(user_id)


def test_login_accepts_the_email_in_any_case(client):
    register(client)
    assert login(client, email="ZAHRA@Example.COM").status_code == 200


def test_a_wrong_password_is_refused(client):
    register(client)
    response = login(client, password="wrong horse")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_an_unknown_email_is_refused_identically(client):
    register(client)
    wrong_password = login(client, password="wrong horse")
    unknown_email = login(client, email="nobody@example.com")
    assert unknown_email.status_code == wrong_password.status_code == 401
    assert unknown_email.json() == wrong_password.json()


def test_a_failed_login_returns_no_token(client):
    register(client)
    assert "access_token" not in login(client, password="wrong horse").json()


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def registered_token(client) -> str:
    register(client)
    return login(client).json()["access_token"]


def test_the_current_user_is_identified_by_the_token(client):
    user_id = register(client).json()["id"]
    token = login(client).json()["access_token"]
    response = client.get("/users/me", headers=bearer(token))
    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "email": EMAIL,
        "role": "user",
        "created_at": response.json()["created_at"],
    }


def test_the_current_user_never_exposes_the_password_hash(client):
    body = client.get("/users/me", headers=bearer(registered_token(client))).text
    assert "password_hash" not in body
    assert "$2b$" not in body


def test_a_missing_token_is_refused(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_a_wrong_scheme_is_refused(client):
    response = client.get("/users/me", headers={"Authorization": f"Basic {registered_token(client)}"})
    assert response.status_code == 401


def test_a_garbage_token_is_refused(client):
    registered_token(client)
    response = client.get("/users/me", headers=bearer("not.a.token"))
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Could not validate credentials"


def test_a_tampered_token_is_refused(client):
    token = registered_token(client)
    assert client.get("/users/me", headers=bearer(token[:-4] + "AAAA")).status_code == 401


def test_a_token_signed_with_another_secret_is_refused(client, monkeypatch):
    registered_token(client)
    monkeypatch.setenv("JWT_SECRET_KEY", "z" * 32)
    _config.get_settings.cache_clear()
    forged = _security.create_access_token("1")
    monkeypatch.setenv("JWT_SECRET_KEY", "k" * 32)
    _config.get_settings.cache_clear()
    assert client.get("/users/me", headers=bearer(forged)).status_code == 401


def test_an_expired_token_is_refused(client, monkeypatch):
    register(client)
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "-1")
    _config.get_settings.cache_clear()
    expired = _security.create_access_token("1")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "30")
    _config.get_settings.cache_clear()
    assert client.get("/users/me", headers=bearer(expired)).status_code == 401


def test_a_token_for_a_deleted_user_is_refused(client):
    token = registered_token(client)
    with _database.get_engine().begin() as connection:
        connection.execute(_sa.text("DELETE FROM users"))
    assert client.get("/users/me", headers=bearer(token)).status_code == 401


def test_a_token_for_a_deactivated_user_is_refused(client):
    token = registered_token(client)
    with _database.get_engine().begin() as connection:
        connection.execute(_sa.text("UPDATE users SET is_active = false WHERE email = :email"), {"email": EMAIL})
    assert client.get("/users/me", headers=bearer(token)).status_code == 401


def test_a_deactivated_admins_token_cannot_reach_admin_routes(client):
    token = registered_token(client)
    with _database.get_engine().begin() as connection:
        connection.execute(
            _sa.text("UPDATE users SET role = 'admin', is_active = false WHERE email = :email"), {"email": EMAIL}
        )
    assert client.get("/admin/users", headers=bearer(token)).status_code == 401


def test_signing_out_is_accepted(client):
    response = client.post("/auth/logout", headers=bearer(registered_token(client)))
    assert response.status_code == 204
    assert response.content == b""


def test_signing_out_requires_a_token(client):
    assert client.post("/auth/logout").status_code == 401


def test_the_token_still_works_after_signing_out(client):
    token = registered_token(client)
    client.post("/auth/logout", headers=bearer(token))
    assert client.get("/users/me", headers=bearer(token)).status_code == 200


def test_registration_login_and_authenticated_requests_never_log_sensitive_values(client, caplog):
    with caplog.at_level(_logging.DEBUG):
        register(client)
        token = login(client).json()["access_token"]
        client.get("/users/me", headers=bearer(token))

    assert PASSWORD not in caplog.text
    assert token not in caplog.text
