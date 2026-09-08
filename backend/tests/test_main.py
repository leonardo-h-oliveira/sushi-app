from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_api_status() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Sushi App API funcionando"}


def test_products_returns_temporary_catalog() -> None:
    response = client.get("/products")

    assert response.status_code == 200
    products = response.json()
    assert len(products) == 3
    assert products[0]["name"] == "Hot Roll"
    assert all(product["active"] for product in products)
