import hashlib
import secrets
import time

from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.admin import AdminUser, AdminSession

SESSION_SECONDS = 8 * 60 * 60


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**15, r=8, p=3, maxmem=64*1024*1024).hex()
    return f"scrypt$32768$8$3${salt}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$")
        if (algorithm, n, r, p) != ("scrypt", "32768", "8", "3"):
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), maxmem=64*1024*1024).hex()
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_admin(db: Session, username: str, password: str) -> AdminUser:
    username = username.strip().casefold()
    if not 1 <= len(username) <= 80 or not 12 <= len(password) <= 200:
        raise ValueError("Use a username up to 80 characters and a password of 12 to 200 characters.")
    if db.scalar(select(AdminUser).where(AdminUser.username == username)):
        raise ValueError("The administrator already exists. Use the explicit password reset command.")
    user = AdminUser(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return user


def authenticate(db: Session, username: str, password: str) -> str:
    username = username.strip().casefold()
    user = db.scalar(select(AdminUser).where(AdminUser.username == username).with_for_update())
    # Only isolated local/test environments support the old environment bootstrap.
    if user is None and settings.environment.lower() in {"development", "test"}:
        if secrets.compare_digest(username, settings.admin_username.strip().casefold()) and secrets.compare_digest(password, settings.admin_password):
            user = create_admin(db, username, password)
    now = int(time.time())
    if user and user.locked_until > now:
        raise HTTPException(status_code=429, detail="Too many requests. Try again shortly.", headers={"Retry-After": str(user.locked_until - now)})
    valid = verify_password(password, user.password_hash) if user else verify_password(password, _DUMMY_HASH)
    if not user or not user.active or user.role != "admin" or not valid:
        if user:
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.locked_until = now + 15 * 60
                user.failed_attempts = 0
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid administrator credentials.")
    user.failed_attempts = 0
    user.locked_until = 0
    token = secrets.token_urlsafe(32)
    # Expired session material is unnecessary after the expiry boundary.
    db.execute(delete(AdminSession).where(AdminSession.expires_at <= now))
    db.add(AdminSession(token_hash=token_hash(token), user_id=user.id, expires_at=now + SESSION_SECONDS))
    db.commit()
    return token


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def resolve_session(db: Session, token: str) -> AdminSession | None:
    if len(token) > 200:
        return None
    session = db.get(AdminSession, token_hash(token))
    if session is None or session.revoked or session.expires_at <= int(time.time()):
        return None
    user = db.get(AdminUser, session.user_id)
    return session if user and user.active and user.role == "admin" else None


def revoke_session(db: Session, session: AdminSession):
    session.revoked = True
    db.commit()


def reset_password(db: Session, username: str, password: str):
    if not 12 <= len(password) <= 200:
        raise ValueError("Use a password of 12 to 200 characters.")
    user = db.scalar(select(AdminUser).where(AdminUser.username == username.strip().casefold()).with_for_update())
    if user is None:
        raise ValueError("Administrator not found.")
    user.password_hash = hash_password(password)
    user.failed_attempts = 0
    user.locked_until = 0
    db.execute(update(AdminSession).where(AdminSession.user_id == user.id).values(revoked=True))
    db.commit()


_DUMMY_HASH = hash_password("unusable-dummy-password-" + secrets.token_hex(16))
