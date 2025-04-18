import datetime
from typing import Any, Annotated
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, Request
from psycopg import DatabaseError

from app.src.utils import security
from fastapi.security import OAuth2PasswordRequestForm

from app.src.deps import SessionDep_async,CurrentUser,redis_client
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
async def login(request: Request, 
    session: SessionDep_async, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> user_schema.Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try :
        user = await user_crud.authenticate(session=session, empl_no=form_data.username, password=form_data.password)
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail='Unknown error')
        
    if not user:
        raise HTTPException(status_code=400, detail="사번 또는 패스워드가 틀렸습니다.")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 계정입니다.")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    client_ip = request.client.host
    
    user_token = user_schema.Token(
        id=user.id,
        access_token=await security.create_access_token(str(user.id), expires_delta=access_token_expires),
        name=user.name,
        is_admin=user.is_admin,
        is_active=user.is_active,
        dept_id=user.dept_id,
        dept_cd=user.dept_cd,
        dept_nm=user.dept_nm,
        client_ip=client_ip,
        create_date=datetime.datetime.now()
        )
    
    redis = request.app.state.redis
    
    await redis.setex(
        name = f"user:{user.id}",
        time = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 토큰 만료시간과 동일하게 설정
        value = user_token.model_dump_json()
    )
    
    return user_token

@router.post("/logout")
async def logout(request: Request, current_user: CurrentUser) -> Any:
    """
    OAuth2 compatible token logout, remove access token from redis
    """
    redis = request.app.state.redis
    await redis.delete(f"user:{current_user.id}")
    return {"detail": "Logged out"}

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