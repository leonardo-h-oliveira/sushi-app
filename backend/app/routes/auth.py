import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import settings
from app.core.security import create_token, enforce_rate_limit, ensure_admin_security_configured, require_admin
from app.schemas.auth import LoginRequest, LoginResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])
Administrator = Annotated[None, Depends(require_admin)]


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response):
    ensure_admin_security_configured()
    enforce_rate_limit(request, "admin-login", settings.login_rate_limit)
    if not (
        secrets.compare_digest(payload.username, settings.admin_username)
        and secrets.compare_digest(payload.password, settings.admin_password)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid administrator credentials.")
    token = create_token(payload.username)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.environment.lower() not in {"development", "test"},
        samesite="none" if settings.environment.lower() not in {"development", "test"} else "lax",
        max_age=60 * 60 * 8,
        path="/",
    )
    return LoginResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, _: Administrator):
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        secure=settings.environment.lower() not in {"development", "test"},
        samesite="none" if settings.environment.lower() not in {"development", "test"} else "lax",
    )
    return None
