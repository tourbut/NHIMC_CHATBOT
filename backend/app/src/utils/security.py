from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

import hashlib
import base64
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"

async def sha512_base64(input_string):
    # SHA-512 해시 생성
    sha512_hash = hashlib.sha512(input_string.encode()).digest()
    # Base64로 인코딩
    base64_encoded = base64.b64encode(sha512_hash).decode()
    return base64_encoded


async def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire =  datetime.now(timezone.utc)  + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    if await sha512_base64(plain_password) == hashed_password:
        return True
    else :
        return False

async def get_password_hash(password: str) -> str:
    return await sha512_base64(password)
