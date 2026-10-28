from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import _attempts
from app.main import app


import pytest
from tests.test_store_settings import db_session, client


@pytest.fixture(autouse=True)
def clear_attempts():
    _attempts.clear()
    yield
    _attempts.clear()


def test_admin_can_login_and_use_bearer_token(client) -> None:
    response = client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"}).status_code == 204


def test_admin_cookie_authentication_and_logout(client) -> None:
    _attempts.clear()
    response = client.post(
        "/auth/login",
        json={"username": settings.admin_username, "password": settings.admin_password},
    )
    assert response.status_code == 200
    cookie = response.cookies.get(settings.auth_cookie_name)
    assert cookie
    assert "HttpOnly" in response.headers["set-cookie"]
    logout = client.post("/auth/logout")
    assert logout.status_code == 204
    assert f"{settings.auth_cookie_name}=\"\"" in logout.headers["set-cookie"]


def test_login_is_rate_limited(client) -> None:
    original_limit = settings.login_rate_limit
    try:
        object.__setattr__(settings, "login_rate_limit", 1)
        _attempts.clear()
        first = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
        blocked = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
        assert first.status_code == 401
        assert blocked.status_code == 429
        assert blocked.headers["retry-after"] == "60"
    finally:
        object.__setattr__(settings, "login_rate_limit", original_limit)
        _attempts.clear()


def test_invalid_credentials_and_expired_shape_are_rejected(client) -> None:
    invalid = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    protected = client.post("/auth/logout", headers={"Authorization": "Bearer invalid"})
    assert invalid.status_code == 401
    assert protected.status_code == 401


def test_deployed_environment_has_no_environment_password_fallback(client) -> None:
    original_environment = settings.environment
    original_username = settings.admin_username
    try:
        object.__setattr__(settings, "environment", "staging")
        object.__setattr__(settings, "admin_username", "admin")
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": settings.admin_password},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid administrator credentials."
    finally:
        object.__setattr__(settings, "environment", original_environment)
        object.__setattr__(settings, "admin_username", original_username)


def test_logout_revokes_captured_bearer_even_in_another_client(client):
    token = client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password}).json()["access_token"]
    assert client.get("/admin/store-settings", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert client.post("/auth/logout").status_code == 204
    assert client.get("/admin/store-settings", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_expired_and_disabled_accounts_cannot_use_sessions(client, db_session):
    from app.models.admin import AdminUser, AdminSession
    from app.services.admin_identity import token_hash
    token = client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password}).json()["access_token"]
    session = db_session.get(AdminSession, token_hash(token))
    session.expires_at = 1
    db_session.commit()
    assert client.get("/admin/store-settings").status_code == 401
    session.expires_at = 2**31 - 1
    db_session.get(AdminUser, session.user_id).active = False
    db_session.commit()
    assert client.get("/admin/store-settings").status_code == 401


def test_password_reset_revokes_sessions_and_hashes_password(client, db_session):
    from sqlalchemy import select
    from app.models.admin import AdminUser
    from app.services.admin_identity import reset_password, verify_password
    token = client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password}).json()["access_token"]
    reset_password(db_session, settings.admin_username, "different-password-for-testing")
    user = db_session.scalar(select(AdminUser))
    assert user.password_hash != "different-password-for-testing"
    assert verify_password("different-password-for-testing", user.password_hash)
    assert client.get("/admin/store-settings", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_account_lockout_persists_after_in_memory_limits_are_cleared(client):
    client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password})
    for _ in range(5):
        _attempts.clear()
        assert client.post("/auth/login", json={"username": settings.admin_username, "password": "wrong"}).status_code == 401
    _attempts.clear()
    assert client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password}).status_code == 429


def test_cookie_mutations_reject_untrusted_browser_origin(client):
    client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password})
    rejected = client.patch("/admin/store-settings", headers={"Origin": "https://untrusted.example"}, json={"is_open": False})
    assert rejected.status_code == 403


def test_deployed_cookie_is_secure_and_account_login_does_not_need_environment_password(client, db_session):
    from app.services.admin_identity import create_admin
    create_admin(db_session, "restaurant-owner", "unique-password-for-test")
    original = settings.environment
    try:
        object.__setattr__(settings, "environment", "production")
        response = client.post("/auth/login", json={"username": "restaurant-owner", "password": "unique-password-for-test"})
        assert response.status_code == 200
        assert "Secure" in response.headers["set-cookie"]
        assert "SameSite=none" in response.headers["set-cookie"]
        assert "HttpOnly" in response.headers["set-cookie"]
    finally:
        object.__setattr__(settings, "environment", original)
