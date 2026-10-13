from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import _attempts, ensure_admin_security_configured
from app.main import app


client = TestClient(app)


def test_admin_can_login_and_use_bearer_token() -> None:
    response = client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"}).status_code == 204


def test_admin_cookie_authentication_and_logout() -> None:
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


def test_login_is_rate_limited() -> None:
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


def test_invalid_credentials_and_expired_shape_are_rejected() -> None:
    invalid = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    protected = client.post("/auth/logout", headers={"Authorization": "Bearer invalid"})
    assert invalid.status_code == 401
    assert protected.status_code == 401


def test_deployed_environment_rejects_all_development_admin_defaults() -> None:
    original_environment = settings.environment
    original_username = settings.admin_username
    try:
        object.__setattr__(settings, "environment", "staging")
        object.__setattr__(settings, "admin_username", "admin")
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": settings.admin_password},
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "Administrator access is not configured safely."
    finally:
        object.__setattr__(settings, "environment", original_environment)
        object.__setattr__(settings, "admin_username", original_username)
