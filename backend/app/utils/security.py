"""
🔐 JWT + OTP helper utilities.
"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from app.config import settings


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=settings.otp_length))


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.jwt_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
