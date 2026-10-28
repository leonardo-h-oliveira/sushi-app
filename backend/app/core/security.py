import secrets
import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import Cookie, Header, HTTPException, Request, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.admin_identity import resolve_session
from app.models.admin import AdminSession

from app.core.config import settings


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


def require_admin(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin_session: Annotated[str | None, Cookie(alias=settings.auth_cookie_name)] = None,
    admin_api_key: Annotated[str | None, Header(alias="X-Admin-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> AdminSession | None:
    """Authorize a persistent staff session or a development-only legacy key."""
    bearer = authorization.removeprefix("Bearer ") if authorization and authorization.startswith("Bearer ") else None
    token = admin_session or bearer
    if token:
        session = resolve_session(db, token)
        if session:
            if admin_session and request.method not in {"GET", "HEAD", "OPTIONS"}:
                origin = request.headers.get("origin")
                if origin not in settings.cors_origins and (origin or settings.environment.lower() not in {"development", "test"}):
                    raise HTTPException(status_code=403, detail="Untrusted browser origin.")
            request.state.admin_user_id = session.user_id
            return session
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
