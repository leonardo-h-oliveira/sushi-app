import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import create_token, require_admin
from app.schemas.auth import LoginRequest, LoginResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])
Administrator = Annotated[None, Depends(require_admin)]


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if not (
        secrets.compare_digest(payload.username, settings.admin_username)
        and secrets.compare_digest(payload.password, settings.admin_password)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid administrator credentials.")
    return LoginResponse(access_token=create_token(payload.username))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(_: Administrator):
    return None
