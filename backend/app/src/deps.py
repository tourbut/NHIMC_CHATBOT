from collections.abc import Generator, AsyncGenerator
import json
from typing import Annotated
import jwt

from sqlmodel import Session,create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from redis import Redis
import redis.asyncio as aioredis

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.src.utils import security
from app.models import User
from app.src.schemas.users import TokenPayload,Token

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI_ASYNC), echo=True if settings.DEBUG else False)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session
        
async def redis_client():
    redis_client = Redis(
        host=settings.REDIS_SERVER,
        port=settings.REDIS_PORT,
        username=settings.REDIS_USER,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    return redis_client

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login"
)

SessionDep = Annotated[Session, Depends(get_db)]

SessionDep_async = Annotated[AsyncSession, Depends(get_async_db)]

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(session: SessionDep_async, token: TokenDep) -> Token:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

        token_data = TokenPayload(**payload)
        
        redis = await redis_client()
        cache_data = redis.get(f"user:{token_data.sub}")
        token_data = Token(**json.loads(cache_data))
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e
            )
            
    if not token_data:
        raise HTTPException(status_code=404, detail="User not found")
    if not token_data.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return token_data

CurrentUser = Annotated[Token, Depends(get_current_user)]

