from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import Category, Product
from app.models.base import Base
from app.seed import CATEGORIES, PRODUCTS, seed_database


def test_seed_populates_the_complete_menu_without_duplicates() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    first_result = seed_database(session_factory)
    second_result = seed_database(session_factory)

    assert first_result == second_result == (len(CATEGORIES), len(PRODUCTS))
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Category)) == 17
        assert session.scalar(select(func.count()).select_from(Product)) == 10
        categories = list(session.scalars(select(Category).order_by(Category.sort_order)))
        assert [category.slug for category in categories] == [item["slug"] for item in CATEGORIES]


def test_seed_uses_normalized_menu_names_and_decimal_prices() -> None:
    names = {item["name"] for item in PRODUCTS}

    assert "Temaki Hot Roll Empanado Premium" in names
    assert "Rodízio Trufado Gourmet (62 peças)" in names
    assert all("Rool" not in name for name in names)
    assert all(item["price"].count(".") == 1 for item in PRODUCTS)
