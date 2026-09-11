"""Command-line entry point for the database seeder."""

from app.seed import seed_database


if __name__ == "__main__":
    category_count, product_count = seed_database()
    print(
        f"Seed completed: {category_count} categories and "
        f"{product_count} products available."
    )
