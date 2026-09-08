from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Category, Product, ProductAddon


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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
def product(db_session: Session) -> Product:
    category = Category(name="Temakis", slug="temakis")
    product = Product(category=category, name="Temaki Salmão", description="", price=Decimal("29.90"))
    product.addons.append(ProductAddon(name="Cream cheese extra", price_delta=Decimal("3.50")))
    db_session.add(product)
    db_session.commit()
    return product


def test_valid_checkout_creates_order_and_status_can_be_retrieved(
    client: TestClient, product: Product
) -> None:
    response = client.post(
        "/orders",
        json={
            "customer_name": "Ana Sushi",
            "phone": "35999999999",
            "fulfillment_method": "delivery",
            "payment_method": "pix",
            "address": {"street": "Rua Central", "number": "100", "neighborhood": "Centro"},
            "items": [{"product_id": product.id, "quantity": 2, "addon_ids": [product.addons[0].id], "notes": "Pouco shoyu"}],
        },
    )

    assert response.status_code == 201
    order = response.json()
    assert order["number"].startswith("SP")
    assert order["status"] == "received"
    assert order["subtotal"] == "66.80"
    assert order["delivery_fee"] == "5.00"
    assert order["total"] == "71.80"
    assert order["items"][0]["product_name"] == "Temaki Salmão"

    retrieved = client.get(f"/orders/{order['number']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["total"] == "71.80"


def test_pickup_has_no_delivery_fee(client: TestClient, product: Product) -> None:
    response = client.post(
        "/orders",
        json={
            "customer_name": "Bruno Sushi",
            "phone": "35988888888",
            "fulfillment_method": "pickup",
            "payment_method": "cash",
            "items": [{"product_id": product.id, "quantity": 1}],
        },
    )

    assert response.status_code == 201
    assert response.json()["delivery_fee"] == "0.00"
    assert response.json()["total"] == "29.90"


def test_invalid_order_data_returns_clear_errors(client: TestClient, product: Product) -> None:
    missing_address = client.post(
        "/orders",
        json={"customer_name": "Ana", "phone": "35999999999", "fulfillment_method": "delivery", "payment_method": "pix", "items": [{"product_id": product.id, "quantity": 1}]},
    )
    unavailable = client.post(
        "/orders",
        json={"customer_name": "Ana", "phone": "35999999999", "fulfillment_method": "pickup", "payment_method": "pix", "items": [{"product_id": 999, "quantity": 1}]},
    )
    unknown = client.get("/orders/SP000000-UNKNOWN")

    assert missing_address.status_code == 422
    assert unavailable.status_code == 422
    assert unavailable.json()["detail"] == "One of the selected products is unavailable."
    assert unknown.status_code == 404
