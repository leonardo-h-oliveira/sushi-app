from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def test_admin_can_login_and_use_bearer_token() -> None:
    response = client.post("/auth/login", json={"username": settings.admin_username, "password": settings.admin_password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"}).status_code == 204


def test_invalid_credentials_and_expired_shape_are_rejected() -> None:
    invalid = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    protected = client.post("/auth/logout", headers={"Authorization": "Bearer invalid"})
    assert invalid.status_code == 401
    assert protected.status_code == 401
