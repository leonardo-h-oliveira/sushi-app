import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _csv_environment(name: str, default: str) -> tuple[str, ...]:
    return tuple(
        value.strip()
        for value in os.getenv(name, default).split(",")
        if value.strip()
    )


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
    auth_cookie_name: str = os.getenv("AUTH_COOKIE_NAME", "sushi_admin_session")
    login_rate_limit: int = int(os.getenv("LOGIN_RATE_LIMIT", "5"))
    tracking_rate_limit: int = int(os.getenv("TRACKING_RATE_LIMIT", "60"))
    cors_origins: tuple[str, ...] = _csv_environment(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    )


settings = Settings()
