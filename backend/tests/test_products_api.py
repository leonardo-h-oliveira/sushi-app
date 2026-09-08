from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Category, Product


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


@pytest.fixture
def categories(db_session: Session) -> tuple[Category, Category]:
    active = Category(name="Temakis", slug="temakis")
    inactive = Category(name="Archived", slug="archived", active=False)
    db_session.add_all([active, inactive])
    db_session.commit()
    return active, inactive


def test_customers_list_and_filter_only_available_products(
    client: TestClient,
    db_session: Session,
    categories: tuple[Category, Category],
) -> None:
    active_category, inactive_category = categories
    db_session.add_all(
        [
            Product(
                category_id=active_category.id,
                name="Temaki Salmão",
                description="Salmão e cream cheese",
                price=Decimal("29.90"),
            ),
            Product(
                category_id=active_category.id,
                name="Unavailable",
                description="",
                price=Decimal("10.00"),
                active=False,
            ),
            Product(
                category_id=inactive_category.id,
                name="Hidden by category",
                description="",
                price=Decimal("12.00"),
            ),
        ]
    )
    db_session.commit()

    response = client.get("/products?category=temakis")

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == ["Temaki Salmão"]
    assert response.json()[0]["price"] == "29.90"


def test_customer_can_retrieve_available_product(
    client: TestClient,
    db_session: Session,
    categories: tuple[Category, Category],
) -> None:
    product = Product(
        category_id=categories[0].id,
        name="Hot Roll",
        description="Eight pieces",
        price=Decimal("24.90"),
    )
    db_session.add(product)
    db_session.commit()

    response = client.get(f"/products/{product.id}")

    assert response.status_code == 200
    assert response.json()["category"]["slug"] == "temakis"
    assert client.get("/products/999").status_code == 404


def test_administrator_can_create_and_update_product(
    client: TestClient, categories: tuple[Category, Category]
) -> None:
    created = client.post(
        "/admin/products",
        headers=ADMIN_HEADERS,
        json={
            "name": "  Combo   Especial ",
            "description": "30 pieces",
            "price": "59.90",
            "image_url": "https://example.com/combo.jpg",
            "category_id": categories[0].id,
        },
    )
    assert created.status_code == 201
    assert created.json()["name"] == "Combo Especial"
    assert created.json()["price"] == "59.90"

    product_id = created.json()["id"]
    updated = client.patch(
        f"/admin/products/{product_id}",
        headers=ADMIN_HEADERS,
        json={"price": "62.50", "active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["price"] == "62.50"
    assert updated.json()["active"] is False
    assert client.get(f"/products/{product_id}").status_code == 404


def test_product_management_requires_authorization(
    client: TestClient, categories: tuple[Category, Category]
) -> None:
    response = client.post(
        "/admin/products",
        json={"name": "Temaki", "price": "20.00", "category_id": categories[0].id},
    )
    assert response.status_code == 401


def test_invalid_price_category_and_empty_update_return_clear_errors(
    client: TestClient, categories: tuple[Category, Category]
) -> None:
    invalid_price = client.post(
        "/admin/products",
        headers=ADMIN_HEADERS,
        json={"name": "Temaki", "price": "-1.00", "category_id": categories[0].id},
    )
    unknown_category = client.post(
        "/admin/products",
        headers=ADMIN_HEADERS,
        json={"name": "Temaki", "price": "20.00", "category_id": 999},
    )

    assert invalid_price.status_code == 422
    assert unknown_category.status_code == 422
    assert unknown_category.json()["detail"] == "The selected category does not exist."
