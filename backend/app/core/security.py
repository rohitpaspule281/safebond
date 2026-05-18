from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException

# PBKDF2-SHA256 avoids the bcrypt backend incompatibility seen on some
# Python 3.13 local environments while still providing a strong password hash.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> tuple[str, int]:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    expires_in = int((expire - datetime.now(timezone.utc)).total_seconds())
    return encoded_jwt, max(expires_in, 0)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedException(detail="Token could not be decoded.") from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise UnauthorizedException(detail="Invalid token type.")

    return payload
