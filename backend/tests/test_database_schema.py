from decimal import Decimal

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.models import Category, Product, ProductAddon


EXPECTED_TABLES = {
    "addresses",
    "alembic_version",
    "categories",
    "customers",
    "order_item_addons",
    "order_item_variants",
    "order_items",
    "orders",
    "product_addons",
    "product_variant_groups",
    "product_variants",
    "products",
}


def create_alembic_config(database_url: str) -> Config:
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_initial_migration_upgrades_and_downgrades(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'schema.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = create_alembic_config(database_url)

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES

    command.downgrade(config, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]


def test_product_relationships_and_decimal_prices(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'relationships.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(create_alembic_config(database_url), "head")
    engine = create_engine(database_url)

    with Session(engine) as session:
        category = Category(name="Temakis", slug="temakis")
        product = Product(
            category=category,
            name="Temaki Salmão",
            description="Salmão com cream cheese",
            price=Decimal("29.90"),
        )
        product.addons.append(
            ProductAddon(name="Cream cheese extra", price_delta=Decimal("3.50"))
        )
        session.add(product)
        session.commit()

        stored_product = session.get(Product, product.id)
        assert stored_product is not None
        assert stored_product.category.slug == "temakis"
        assert stored_product.price == Decimal("29.90")
        assert stored_product.addons[0].price_delta == Decimal("3.50")


def test_schema_contains_expected_foreign_keys_and_checks(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'constraints.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(create_alembic_config(database_url), "head")
    inspector = inspect(create_engine(database_url))

    order_targets = {
        foreign_key["referred_table"]
        for foreign_key in inspector.get_foreign_keys("orders")
    }
    order_item_targets = {
        foreign_key["referred_table"]
        for foreign_key in inspector.get_foreign_keys("order_items")
    }
    product_checks = {
        constraint["name"] for constraint in inspector.get_check_constraints("products")
    }
    order_item_checks = {
        constraint["name"]
        for constraint in inspector.get_check_constraints("order_items")
    }

    assert order_targets == {"addresses", "customers"}
    assert order_item_targets == {"orders", "products"}
    assert "ck_products_price_non_negative" in product_checks
    assert "ck_products_original_price_above_price" in product_checks
    assert "ck_order_items_quantity_positive" in order_item_checks
