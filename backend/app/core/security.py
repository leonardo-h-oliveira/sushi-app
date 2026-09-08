import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_admin(
    admin_api_key: Annotated[str | None, Header(alias="X-Admin-Key")] = None,
) -> None:
    """Protect administration routes until token authentication is introduced."""
    if (
        settings.environment.lower() not in {"development", "test"}
        and settings.admin_api_key == "local-development-only"
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrator access is not configured.",
        )

    if not admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="An administrator API key is required.",
        )

    if not secrets.compare_digest(admin_api_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The administrator API key is invalid.",
        )
