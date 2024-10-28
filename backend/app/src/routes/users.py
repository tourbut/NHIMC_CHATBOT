from typing import Any, Annotated
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from psycopg import DatabaseError

from app.src.utils import security
from fastapi.security import OAuth2PasswordRequestForm

from app.src.deps import SessionDep_async,CurrentUser
from app.src.crud import users as user_crud
from app.src.schemas import users as user_schema

from app.core.config import settings

router = APIRouter()

@router.post("/signup", response_model=user_schema.UserPublic)
async def signup(*, session: SessionDep_async, user_in: user_schema.UserCreate) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    
    user = await user_crud.create_user(session=session, user_create=user_in)
    
    return user

@router.post("/login")
async def login(
    session: SessionDep_async, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> user_schema.Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try :
        user = await user_crud.authenticate(session=session, empl_no=form_data.username, password=form_data.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail='Unknown error')
        
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return user_schema.Token(access_token=await security.create_access_token(str(user.id), expires_delta=access_token_expires),
                             name=user.name,
                             is_admin=user.is_admin)


@router.get("/get_user", response_model=user_schema.UserPublic)
async def get_user(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get User
    """

    return current_user

@router.get("/get_userdetail", response_model=user_schema.UserDetail)
async def get_userdetail(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get User
    """

    return current_user

@router.put("/update_detail/",response_model=user_schema.UserDetail)
async def update_detail(*, session: SessionDep_async, current_user: CurrentUser, detail_in: user_schema.UserDetail) -> Any:
    """
    Update User detail
    """
    
    user = await user_crud.update_detail(session=session, user_detail=detail_in, user_id=current_user.id)
    return user