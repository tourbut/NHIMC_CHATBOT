from collections.abc import Generator, AsyncGenerator
import json
from typing import Annotated
import jwt

from sqlmodel import Session,create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

import redis
import redis.asyncio as aioredis

from fastapi import Depends, HTTPException, Request, status
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
    
    conn_pool = redis.ConnectionPool.from_url(f"redis://{settings.REDIS_USER}:{settings.REDIS_PASSWORD}@{settings.REDIS_SERVER}:{settings.REDIS_PORT}",
                                              db=0,
                                              max_connections=10,
                                              decode_responses=True)
    
    return redis.Redis(connection_pool=conn_pool)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login"
)

SessionDep = Annotated[Session, Depends(get_db)]

SessionDep_async = Annotated[AsyncSession, Depends(get_async_db)]

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(request:Request,session: SessionDep_async, token: TokenDep) -> Token:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

        token_data = TokenPayload(**payload)
        
        redis =  request.app.state.redis
        cache_data = await redis.get(f"user:{token_data.sub}")
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

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# 기존 SQLAlchemy 엔진에서 연결 문자열 추출
DB_URI = str(settings.SQLALCHEMY_DATABASE_URI)

# AsyncConnectionPool 생성
async def get_checkpointer() -> AsyncGenerator[AsyncPostgresSaver, None]:
    
    async_pool = AsyncConnectionPool(
        conninfo=DB_URI,
        max_size=20,
        kwargs={"autocommit": True}
    )
    
    checkpointer = AsyncPostgresSaver(async_pool)  # 객체 생성
    
    await checkpointer.setup()  # 테이블 생성 필수
    
    yield checkpointer  # 생성된 객체를 반환

CheckpointerDep = Annotated[AsyncPostgresSaver, Depends(get_checkpointer)]