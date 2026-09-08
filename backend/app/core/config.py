import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/sushi_app",
    )
    admin_api_key: str = os.getenv("ADMIN_API_KEY", "local-development-only")
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "local-development-only")
    auth_secret: str = os.getenv("AUTH_SECRET", "local-development-only")


settings = Settings()
