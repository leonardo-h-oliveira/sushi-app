from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import settings
from sqlalchemy.orm import Session
from app.core.security import enforce_rate_limit, require_admin
from app.database import get_db
from app.services.admin_identity import authenticate, revoke_session
from app.schemas.auth import LoginRequest, LoginResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])
Administrator = Annotated[None, Depends(require_admin)]


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Annotated[Session, Depends(get_db)]):
    origin = request.headers.get("origin")
    if origin and origin not in settings.cors_origins:
        raise HTTPException(status_code=403, detail="Untrusted browser origin.")
    enforce_rate_limit(request, "admin-login", settings.login_rate_limit)
    token = authenticate(db, payload.username, payload.password)
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
def logout(response: Response, session: Annotated[object, Depends(require_admin)], db: Annotated[Session, Depends(get_db)]):
    if session is not None:
        revoke_session(db, session)
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        secure=settings.environment.lower() not in {"development", "test"},
        samesite="none" if settings.environment.lower() not in {"development", "test"} else "lax",
    )
    return None
