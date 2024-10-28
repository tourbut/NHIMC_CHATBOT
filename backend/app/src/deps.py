from collections.abc import Generator, AsyncGenerator
from typing import Annotated
import jwt

from sqlmodel import Session,create_engine


from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.src.utils import security
from app.models import User
from app.src.schemas.users import TokenPayload

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI_ASYNC))

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login"
)

SessionDep = Annotated[Session, Depends(get_db)]

SessionDep_async = Annotated[AsyncSession, Depends(get_async_db)]

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(session: SessionDep_async, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]