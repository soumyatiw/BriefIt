from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
# pyrefly: ignore [missing-import]
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.config import settings
from api.database import get_db

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload["exp"] = expire
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc


def get_current_user_id(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> int:
    """Extract the user ID (integer PK) from the Bearer token.  Raises 401 if invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if not email:
            raise ValueError("missing sub claim")
    except (ValueError, Exception):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    from api.models.user import User
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user.id


def get_current_user_id_optional(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> int | None:
    """Like get_current_user_id, but returns None instead of raising — feed works logged-out."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if not email:
            return None
    except Exception:
        return None

    from api.models.user import User
    user = db.query(User).filter(User.email == email).first()
    return user.id if user else None
