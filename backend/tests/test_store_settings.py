from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database import get_db
from app.main import app
from app.models import Base, Category, Product
from app.models.order import Order
from sqlalchemy import select, func


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
    product = Product(
        category=Category(name="Temakis", slug="temakis"),
        name="Temaki Salmão",
        description="",
        price=Decimal("29.90"),
    )
    db_session.add(product)
    db_session.commit()
    return product


def order_payload(product: Product, **changes):
    payload = {
        "customer_name": "Cliente Teste",
        "expected_total": "34.90",
        "phone": "35999999999",
        "fulfillment_method": "delivery",
        "payment_method": "pix",
        "address": {"street": "Rua Central", "number": "10", "neighborhood": "Centro"},
        "items": [{"product_id": product.id, "quantity": 1}],
    }
    payload.update(changes)
    return payload


def test_public_defaults_and_admin_update(client: TestClient) -> None:
    defaults = client.get("/store-settings")
    assert defaults.status_code == 200
    assert defaults.json()["delivery_fee"] == "5.00"
    assert client.patch("/admin/store-settings", json={"delivery_fee": 8}).status_code == 401

    updated = client.patch(
        "/admin/store-settings",
        headers={"X-Admin-Key": settings.admin_api_key},
        json={"delivery_fee": 8.5, "minimum_order": 25, "cash_enabled": False},
    )
    assert updated.status_code == 200
    assert updated.json()["delivery_fee"] == "8.50"
    assert updated.json()["minimum_order"] == "25.00"
    assert updated.json()["cash_enabled"] is False


def test_order_uses_fee_and_operational_rules(client: TestClient, product: Product) -> None:
    headers = {"X-Admin-Key": settings.admin_api_key}
    client.patch("/admin/store-settings", headers=headers, json={"delivery_fee": 9.5})
    created = client.post("/orders", json=order_payload(product, expected_total="39.40"))
    assert created.status_code == 201
    assert created.json()["delivery_fee"] == "9.50"

    client.patch("/admin/store-settings", headers=headers, json={"delivery_enabled": False})
    assert client.post("/orders", json=order_payload(product)).status_code == 409

    client.patch(
        "/admin/store-settings",
        headers=headers,
        json={"delivery_enabled": True, "minimum_order": 30},
    )
    below_minimum = client.post("/orders", json=order_payload(product))
    assert below_minimum.status_code == 422
    assert below_minimum.json()["detail"] == "The minimum order is 30.00."


def test_closed_store_and_disabled_payment_are_enforced(client: TestClient, product: Product) -> None:
    headers = {"X-Admin-Key": settings.admin_api_key}
    client.patch("/admin/store-settings", headers=headers, json={"is_open": False})
    assert client.post("/orders", json=order_payload(product)).status_code == 409

    client.patch(
        "/admin/store-settings",
        headers=headers,
        json={"is_open": True, "pix_enabled": False},
    )
    unavailable = client.post("/orders", json=order_payload(product))
    assert unavailable.status_code == 409
    assert unavailable.json()["detail"] == "The selected payment method is unavailable."


@pytest.mark.parametrize("field", ["is_open", "delivery_enabled", "pickup_enabled", "pix_enabled", "card_on_delivery_enabled", "cash_enabled", "delivery_fee", "minimum_order"])
def test_explicit_null_is_rejected_without_changing_settings(client, field):
    before = client.get("/store-settings").json()
    response = client.patch("/admin/store-settings", headers={"X-Admin-Key": settings.admin_api_key}, json={field: None})
    assert response.status_code == 422
    assert client.get("/store-settings").json() == before


def test_fee_change_requires_reconfirmation_and_creates_only_one_order(client, product, db_session):
    payload = order_payload(product)
    client.patch("/admin/store-settings", headers={"X-Admin-Key": settings.admin_api_key}, json={"delivery_fee": "10.00"})
    stale = client.post("/orders", json=payload)
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "price_changed"
    assert stale.json()["detail"]["total"] == "39.90"
    assert db_session.scalar(select(func.count()).select_from(Order)) == 0
    payload["expected_total"] = "39.90"
    assert client.post("/orders", json=payload).status_code == 201
    assert db_session.scalar(select(func.count()).select_from(Order)) == 1


def test_product_price_change_requires_reconfirmation(client, product, db_session):
    payload = order_payload(product)
    product.price = Decimal("35.00")
    db_session.commit()
    response = client.post("/orders", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"]["total"] == "40.00"


def test_pickup_ignores_fee_and_accepts_exact_minimum(client, product):
    client.patch("/admin/store-settings", headers={"X-Admin-Key": settings.admin_api_key}, json={"delivery_fee": "100.00", "minimum_order": "29.90"})
    response = client.post("/orders", json=order_payload(product, fulfillment_method="pickup", address=None, expected_total="29.90"))
    assert response.status_code == 201
    assert response.json()["delivery_fee"] == "0.00"


def test_total_confirmation_is_required(client, product):
    payload = order_payload(product)
    del payload["expected_total"]
    assert client.post("/orders", json=payload).status_code == 422


def test_configured_delivery_area_rejects_unknown_neighborhood(client, product):
    headers = {"X-Admin-Key": settings.admin_api_key}
    assert client.patch("/admin/store-settings", headers=headers, json={"delivery_neighborhoods": ["São José"]}).status_code == 200
    assert client.post("/orders", json=order_payload(product)).status_code == 422
    payload = order_payload(product, address={"street": "Rua Central", "number": "10", "neighborhood": "  SAO JOSE  "})
    assert client.post("/orders", json=payload).status_code == 201
    payload["address"]["city"] = "Outra cidade"
    assert client.post("/orders", json=payload).status_code == 422
    assert client.post("/orders", json=order_payload(product, fulfillment_method="pickup", address=None, expected_total="29.90")).status_code == 201


def test_cash_change_is_validated_and_visible_to_staff(client, product):
    insufficient = client.post("/orders", json=order_payload(product, payment_method="cash", cash_change_for="30.00"))
    assert insufficient.status_code == 422
    non_cash = client.post("/orders", json=order_payload(product, cash_change_for="50.00"))
    assert non_cash.status_code == 422
    response = client.post("/orders", json=order_payload(product, payment_method="cash", cash_change_for="50.00"))
    assert response.status_code == 201
    assert response.json()["cash_change_for"] == "50.00"
    orders = client.get("/orders", headers={"X-Admin-Key": settings.admin_api_key}).json()
    assert orders[0]["cash_change_for"] == "50.00"
    no_change = client.post("/orders", json=order_payload(product, payment_method="cash"))
    assert no_change.status_code == 201
    assert no_change.json()["cash_change_for"] is None


def test_live_order_readiness_requires_delivery_area_and_pix_instructions(client):
    headers = {"X-Admin-Key": settings.admin_api_key}
    assert client.patch("/admin/store-settings", headers=headers, json={"operations_ready": True}).status_code == 422
    ready = client.patch("/admin/store-settings", headers=headers, json={"operations_ready": True, "delivery_neighborhoods": ["Centro"], "pix_instructions": "Solicite a chave à equipe."})
    assert ready.status_code == 200
    assert client.patch("/admin/store-settings", headers=headers, json={"delivery_neighborhoods": []}).status_code == 422


@pytest.mark.parametrize("payload", [
    {"schedule_enabled": True},
    {"opening_hours": [{"weekday": 7, "opens": "18:00", "closes": "23:00"}]},
    {"opening_hours": [{"weekday": 1, "opens": "25:00", "closes": "23:00"}]},
    {"opening_hours": [{"weekday": 1, "opens": "18:00", "closes": "18:00"}]},
    {"closed_dates": ["2026-02-30"]},
])
def test_invalid_operating_rules_are_rejected(client, payload):
    assert client.patch("/admin/store-settings", headers={"X-Admin-Key": settings.admin_api_key}, json=payload).status_code == 422


@pytest.mark.parametrize("instant, expected", [
    ("2026-10-27T20:59:00+00:00", False),
    ("2026-10-27T21:00:00+00:00", True),
    ("2026-10-28T04:59:00+00:00", True),
    ("2026-10-28T05:00:00+00:00", False),
])
def test_opening_hours_use_sao_paulo_and_support_overnight(instant, expected):
    from datetime import datetime
    from types import SimpleNamespace
    from app.services.operating_rules import availability
    store = SimpleNamespace(is_open=True, operations_ready=True, schedule_enabled=True,
                            opening_hours=[{"weekday": 1, "opens": "18:00", "closes": "02:00"}], closed_dates=[])
    assert availability(store, datetime.fromisoformat(instant))[0] is expected


def test_special_closure_and_manual_override_take_priority():
    from datetime import datetime
    from types import SimpleNamespace
    from app.services.operating_rules import availability
    store = SimpleNamespace(is_open=True, operations_ready=True, schedule_enabled=True,
                            opening_hours=[{"weekday": 1, "opens": "18:00", "closes": "02:00"}], closed_dates=["2026-10-28"])
    assert availability(store, datetime.fromisoformat("2026-10-28T01:00:00-03:00"))[0] is False
    store.closed_dates = []
    store.is_open = False
    assert availability(store, datetime.fromisoformat("2026-10-27T19:00:00-03:00")) == (False, None)


def test_published_environment_stays_closed_until_rules_are_confirmed(monkeypatch):
    from types import SimpleNamespace
    from app.services import operating_rules
    monkeypatch.setattr(operating_rules, "settings", SimpleNamespace(environment="production"))
    store = SimpleNamespace(is_open=True, operations_ready=False)
    assert operating_rules.availability(store) == (False, None)
