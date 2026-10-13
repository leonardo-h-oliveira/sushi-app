import secrets
import base64
import binascii
import hashlib
import hmac
import json
import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import Cookie, Header, HTTPException, Request, status

from app.core.config import settings


UNSAFE_PRODUCTION_VALUES = {
    "admin_api_key": "local-development-only",
    "admin_username": "admin",
    "admin_password": "local-development-only",
    "auth_secret": "local-development-only",
}

_attempts: dict[str, deque[float]] = defaultdict(deque)


def enforce_rate_limit(request: Request, scope: str, limit: int, window_seconds: int = 60) -> None:
    """Apply a per-client limiter for the single-instance MVP deployment."""
    client = request.client.host if request.client else "unknown"
    attempts = _attempts[f"{scope}:{client}"]
    now = time.monotonic()
    while attempts and attempts[0] <= now - window_seconds:
        attempts.popleft()
    if len(attempts) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again shortly.",
            headers={"Retry-After": str(window_seconds)},
        )
    attempts.append(now)


def ensure_admin_security_configured() -> None:
    """Fail closed when a deployed environment still uses development credentials."""
    if settings.environment.lower() in {"development", "test"}:
        return
    unsafe = [
        name
        for name, unsafe_value in UNSAFE_PRODUCTION_VALUES.items()
        if getattr(settings, name) == unsafe_value
    ]
    if unsafe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrator access is not configured safely.",
        )


def require_admin(
    admin_session: Annotated[str | None, Cookie(alias=settings.auth_cookie_name)] = None,
    admin_api_key: Annotated[str | None, Header(alias="X-Admin-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Accept a signed administrator bearer session or the legacy API key."""
    ensure_admin_security_configured()

    bearer = authorization.removeprefix("Bearer ") if authorization and authorization.startswith("Bearer ") else None
    token = admin_session or bearer
    if token:
        if verify_token(token):
            return
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The administrator session is invalid or expired.")

    if settings.environment.lower() not in {"development", "test"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="An administrator session is required.",
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
