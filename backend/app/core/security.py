import secrets
import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_admin(
    admin_api_key: Annotated[str | None, Header(alias="X-Admin-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Accept a signed administrator bearer session or the legacy API key."""
    if (
        settings.environment.lower() not in {"development", "test"}
        and settings.admin_api_key == "local-development-only"
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrator access is not configured.",
        )

    if authorization and authorization.startswith("Bearer "):
        if verify_token(authorization.removeprefix("Bearer ")):
            return
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The administrator session is invalid or expired.")

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


def create_token(username: str) -> str:
    payload = {"sub": username, "exp": int(time.time()) + 60 * 60 * 8}
    encoded = _encode(payload)
    signature = _signature(encoded)
    return f"{encoded}.{signature}"


def verify_token(token: str) -> bool:
    try:
        encoded, signature = token.split(".", 1)
        expected = _signature(encoded)
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        return hmac.compare_digest(signature, expected) and payload.get("exp", 0) > int(time.time())
    except (ValueError, TypeError, json.JSONDecodeError, binascii.Error):
        return False


def _encode(payload: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")


def _signature(encoded: str) -> str:
    return hmac.new(settings.auth_secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
