from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Category


ADMIN_HEADERS = {"X-Admin-Key": "local-development-only"}


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)
    with testing_session() as session:
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_database():
        yield db_session

    app.dependency_overrides[get_db] = override_database
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_customers_only_receive_active_categories(
    client: TestClient, db_session: Session
) -> None:
    db_session.add_all(
        [
            Category(name="Temakis", slug="temakis"),
            Category(name="Hidden", slug="hidden", active=False),
            Category(name="Combos", slug="combos"),
        ]
    )
    db_session.commit()

    response = client.get("/categories")

    assert response.status_code == 200
    assert [category["name"] for category in response.json()] == ["Combos", "Temakis"]


def test_administrator_can_create_update_and_deactivate_category(
    client: TestClient,
) -> None:
    created = client.post(
        "/admin/categories",
        headers=ADMIN_HEADERS,
        json={"name": "  Temakis   Especiais "},
    )
    assert created.status_code == 201
    assert created.json()["slug"] == "temakis-especiais"

    category_id = created.json()["id"]
    updated = client.patch(
        f"/admin/categories/{category_id}",
        headers=ADMIN_HEADERS,
        json={"name": "Temakis Premium"},
    )
    assert updated.status_code == 200
    assert updated.json()["slug"] == "temakis-premium"

    deactivated = client.delete(
        f"/admin/categories/{category_id}", headers=ADMIN_HEADERS
    )
    assert deactivated.status_code == 204
    assert client.get("/categories").json() == []


def test_management_requires_valid_administrator_key(client: TestClient) -> None:
    missing = client.post("/admin/categories", json={"name": "Combos"})
    invalid = client.post(
        "/admin/categories",
        headers={"X-Admin-Key": "wrong"},
        json={"name": "Combos"},
    )

    assert missing.status_code == 401
    assert missing.json()["detail"] == "An administrator API key is required."
    assert invalid.status_code == 403
    assert invalid.json()["detail"] == "The administrator API key is invalid."


def test_duplicate_invalid_and_unknown_categories_return_clear_errors(
    client: TestClient,
) -> None:
    first = client.post(
        "/admin/categories", headers=ADMIN_HEADERS, json={"name": "Combos"}
    )
    duplicate = client.post(
        "/admin/categories", headers=ADMIN_HEADERS, json={"name": "combos"}
    )
    invalid = client.post(
        "/admin/categories", headers=ADMIN_HEADERS, json={"name": " "}
    )
    unknown = client.patch(
        "/admin/categories/999", headers=ADMIN_HEADERS, json={"name": "Temakis"}
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "A category with this name already exists."
    assert invalid.status_code == 422
    assert unknown.status_code == 404
    assert unknown.json()["detail"] == "Category not found."
