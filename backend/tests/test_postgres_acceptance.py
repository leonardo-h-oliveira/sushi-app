"""Opt-in acceptance against an isolated PostgreSQL database, never production."""
import os

import pytest


@pytest.mark.skipif(not os.getenv("TEST_POSTGRES_URL"), reason="Requires a dedicated PostgreSQL test database")
def test_postgres_migrations_seed_order_and_staff_session():
    from alembic import command
    from alembic.config import Config
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine, func, select
    from sqlalchemy.engine import make_url
    from sqlalchemy.orm import Session

    from app.core.config import settings
    from app.database import get_db
    from app.main import app
    from app.models import Product
    from app.seed import seed_database
    from app.services.admin_identity import create_admin

    url = os.environ["TEST_POSTGRES_URL"]
    parsed = make_url(url)
    assert parsed.get_backend_name() == "postgresql" and parsed.database.endswith("_test")
    assert settings.database_url == url, "Seed and API must use the same isolated test database"
    config = Config("backend/alembic.ini")
    command.upgrade(config, "head")
    assert seed_database() == seed_database()
    engine = create_engine(url)
    with Session(engine, expire_on_commit=False) as db:
        before = db.scalar(select(func.count()).select_from(Product))
        assert before > 0
        create_admin(db, "acceptance-admin", "acceptance-test-password")
        app.dependency_overrides[get_db] = lambda: db
        try:
            with TestClient(app) as client:
                assert client.get("/orders").status_code == 401
                assert client.post("/auth/login", json={"username": "acceptance-admin", "password": "acceptance-test-password"}).status_code == 200
                product = next(item for item in client.get("/products").json() if item["name"] == "Poke de salmão")
                created = client.post("/orders", json={
                    "customer_name": "PostgreSQL acceptance", "phone": "35999990003",
                    "fulfillment_method": "pickup", "payment_method": "pix", "expected_total": product["price"],
                    "items": [{"product_id": product["id"], "quantity": 1}],
                })
                assert created.status_code == 201
                order = created.json()
                assert order["delivery_fee"] == "0.00"
                for state in ["preparing", "ready", "completed"]:
                    assert client.patch(f"/orders/{order['number']}/status", json={"status": state}).status_code == 200
                tracked = client.get(f"/orders/track/{order['tracking_token']}").json()
                assert tracked["status"] == "completed"
                assert "phone" not in tracked and "address" not in tracked
                token = client.cookies.get(settings.auth_cookie_name)
                assert client.post("/auth/logout").status_code == 204
                assert client.get("/orders", headers={"Authorization": f"Bearer {token}"}).status_code == 401
        finally:
            app.dependency_overrides.clear()
    engine.dispose()
