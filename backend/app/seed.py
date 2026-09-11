"""Populate the database with the initial Sushi Poços menu."""

from collections.abc import Callable
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import SessionLocal
from app.models import Category, Product

STORE = {
    "name": "Sushi Poços",
    "address": "R. Canadá, 333 - Jardim Quisisana, Poços de Caldas - MG, 37701-235, Brasil",
    "delivery_time": "55 - 60 min",
}

CATEGORIES = [
    {"name": "Destaques e Promoções", "slug": "destaques-promocoes"},
    {"name": "Sushis Tradicionais", "slug": "sushis-tradicionais"},
    {"name": "Sushis Variados Gourmet", "slug": "sushis-variados-gourmet"},
    {"name": "Hot Rolls Variados Premium", "slug": "hot-rolls-variados-premium"},
    {"name": "Niguiris Variados", "slug": "niguiris-variados"},
    {"name": "Joys Variados Premium", "slug": "joys-variados-premium"},
    {"name": "Temakis Variados Premium", "slug": "temakis-variados-premium"},
    {"name": "Pokes Variados Premium", "slug": "pokes-variados-premium"},
    {"name": "Sashimis de Salmão Poços", "slug": "sashimis-de-salmao-pocos"},
    {"name": "Uramakis Variados Premium", "slug": "uramakis-variados-premium"},
    {"name": "Carpaccios Variados", "slug": "carpaccios-variados"},
    {"name": "Harumakis e Gyozas", "slug": "harumakis-gyozas"},
    {"name": "Teppans Variados Poços", "slug": "teppans-variados-pocos"},
    {"name": "Bebidas", "slug": "bebidas"},
    {"name": "Saladas Veganas e Vegetarianas", "slug": "saladas-veganas-vegetarianas"},
    {"name": "Shimeji Box", "slug": "shimeji-box"},
    {"name": "Yakisoba", "slug": "yakisoba"},
]


def _product(
    category_slug: str,
    name: str,
    price: str,
    description: str = "",
    original_price: str | None = None,
    discount_percent: int | None = None,
) -> dict[str, str | int | None]:
    return {
        "category_slug": category_slug,
        "name": name,
        "price": price,
        "description": description,
        "original_price": original_price,
        "discount_percent": discount_percent,
    }


PRODUCTS = [
    _product(
        "destaques-promocoes",
        "Temaki Hot Roll Empanado Premium",
        "24.90",
        original_price="29.90",
        discount_percent=17,
    ),
    _product(
        "sushis-tradicionais",
        "Rodízio Japonês em Casa (64 peças)",
        "149.99",
        "2 harumakis de queijo, 2 harumakis de chocolate, 2 gyozas de carne bovina, 2 camarões empanados, 2 lulas, 5 hot rolls Filadélfia, 5 hot rolls mineiros com couve frita, 4 hot rolls de banana com creme de avelã, 1 mini porção de shimeji, 1 mini porção de teppan, 1 salada de sunomono, 1 carpaccio de salmão ao molho ponzu com 5 fatias, 6 sashimis de salmão fresco, 2 uramakis de salmão grelhado com Doritos, 2 uramakis de salmão Filadélfia com couve e 2 uramakis Filadélfia.",
    ),
    _product(
        "sushis-tradicionais",
        "Rodízio Trufado Gourmet (62 peças)",
        "189.99",
        "Carpaccio de salmão com ovas, tataki, sunomono, gyozas suínas, camarões, harumakis de queijo, legumes e doce de leite, hot rolls variados, sashimis de salmão e polvo, sashimis trufados com ovas black e flor de sal, uramakis, hossomakis, joys e niguiris variados.",
        original_price="199.00",
        discount_percent=5,
    ),
    _product(
        "sushis-tradicionais",
        "Combo Família Premium (75 peças)",
        "169.90",
        "10 sashimis de salmão, 10 sashimis de salmão trufado com flor de sal, 5 sashimis de salmão maçaricado, 8 uramakis de salmão Filadélfia, 8 hossomakis de salmão, 8 joys variados de salmão, 8 niguiris de salmão, 8 camarões empanados e 10 hot rolls variados.",
    ),
    _product(
        "sushis-tradicionais",
        "Combinado Top 2 (42 peças)",
        "89.99",
        "10 sashimis de salmão, 4 uramakis de salmão Filadélfia, 4 hossomakis de salmão grelhado, 4 uramakis de salmão grelhado, 8 hossomakis de salmão, 4 joys de salmão, 4 niguiris de salmão e 10 hot rolls variados.",
    ),
    _product(
        "sushis-tradicionais",
        "Combo Sushis Tradicionais (38 peças)",
        "84.99",
        "4 sashimis de salmão, 8 uramakis de salmão, 8 hossomakis de salmão, 4 joys de salmão, 4 niguiris de salmão e 10 hot rolls variados.",
    ),
    _product(
        "sushis-tradicionais",
        "Combinado Casal Feliz (42 peças + 2 temakis)",
        "99.99",
        "10 sashimis de salmão, 4 uramakis especiais de salmão, 8 hossomakis de salmão, 4 niguiris de salmão, 6 joys de salmão, 10 hot rolls e 2 temakis Filadélfia.",
    ),
    _product(
        "sushis-tradicionais",
        "Combinado Especial Salmão (25 peças)",
        "84.99",
        "5 sashimis de salmão, 4 uramakis especiais, 4 uramakis de salmão, 4 niguiris de salmão, 4 joys de salmão e 4 hot rolls.",
    ),
    _product(
        "sushis-tradicionais",
        "Combinado Só Sushi (20 peças)",
        "49.90",
        "4 uramakis de salmão, 4 uramakis de salmão grelhado, 4 hossomakis grelhados, 4 hossomakis de salmão e 4 hot rolls variados.",
    ),
    _product(
        "sushis-tradicionais",
        "Combinado Salmão Tradicional (40 peças)",
        "94.99",
        "8 sashimis de salmão, 8 hossomakis de salmão, 8 uramakis de salmão, 4 joys, 4 niguiris de salmão e 10 hot rolls.",
    ),
]


def seed_categories(session: Session) -> dict[str, Category]:
    """Create or update categories without duplicating them."""
    existing = {category.slug: category for category in session.scalars(select(Category)).all()}
    categories: dict[str, Category] = {}
    for sort_order, data in enumerate(CATEGORIES, start=1):
        category = existing.get(data["slug"])
        if category is None:
            category = Category(**data)
            session.add(category)
        category.name = data["name"]
        category.sort_order = sort_order
        category.active = True
        categories[data["slug"]] = category
    session.flush()
    return categories


def seed_products(session: Session, categories: dict[str, Category]) -> list[Product]:
    """Create or update products without duplicating them."""
    existing = {
        (product.category.slug, product.name): product
        for product in session.scalars(select(Product).options(selectinload(Product.category))).all()
    }
    products: list[Product] = []
    positions: dict[str, int] = {}
    for data in PRODUCTS:
        category_slug = str(data["category_slug"])
        positions[category_slug] = positions.get(category_slug, 0) + 1
        product = existing.get((category_slug, str(data["name"])))
        if product is None:
            product = Product(
                category=categories[category_slug],
                name=str(data["name"]),
                price=Decimal(str(data["price"])),
            )
            session.add(product)
        product.description = str(data["description"])
        product.price = Decimal(str(data["price"]))
        product.sort_order = positions[category_slug]
        product.active = True
        products.append(product)
    session.flush()
    return products


def seed_database(session_factory: Callable[[], Session] = SessionLocal) -> tuple[int, int]:
    """Populate the configured database and return menu totals."""
    with session_factory() as session:
        categories = seed_categories(session)
        products = seed_products(session, categories)
        session.commit()
    return len(categories), len(products)


if __name__ == "__main__":
    category_count, product_count = seed_database()
    print(f"Seed completed: {category_count} categories and {product_count} products available.")
