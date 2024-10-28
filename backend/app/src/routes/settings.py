import uuid

from typing import Any, Annotated, List
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends

from app.src.deps import SessionDep_async,CurrentUser
from app.src.crud import settings as settings_crud
from app.src.schemas import settings as settings_schema

from app.core.config import settings

router = APIRouter()

@router.get("/get_llm", response_model=List[settings_schema.Get_LLM])
async def get_llm(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get LLM Settings
    """
    settings = await settings_crud.get_llm(session=session)
    return settings

@router.post("/create_apikey")
async def create_apikey(*, session: SessionDep_async, apikey_in: settings_schema.Create_Apikey, current_user: CurrentUser) -> Any:
    """
    Create API Key
    """
    apikey = await settings_crud.create_apikey(session=session, apikey_in=apikey_in,user_id=current_user.id)
    
@router.get("/get_apikey", response_model=List[settings_schema.Get_Apikey])
async def get_apikey(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get API Key
    """
    apikey = await settings_crud.get_apikey(session=session,user_id=current_user.id)
    return apikey

@router.put("/update_apikey")
async def update_apikey(*, session: SessionDep_async, apikey_update: settings_schema.Get_Apikey, current_user: CurrentUser) -> Any:
    """
    Update API Key
    """
    apikey = await settings_crud.update_apikey(session=session, apikey_update=apikey_update)
    

@router.get("/get_userllm", response_model=List[settings_schema.Get_UserLLM])
async def get_userllm(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get User LLM
    """
    userllm = await settings_crud.get_userllm(session=session,user_id=current_user.id)
    return userllm

@router.post("/create_userllm")
async def create_userllm(*, session: SessionDep_async, userllm_in: settings_schema.Create_UserLLM, current_user: CurrentUser) -> Any:
    """
    Create User LLM
    """
    userllm = await settings_crud.create_userllm(session=session, userllm_in=userllm_in,user_id=current_user.id)
    
@router.put("/update_userllm")
async def update_userllm(*, session: SessionDep_async, userllm_update: settings_schema.Update_UserLLM, current_user: CurrentUser) -> Any:
    """
    Update User LLM
    """
    userllm = await settings_crud.update_userllm(session=session, userllm_update=userllm_update)
    
@router.get("/get_userusage",response_model=List[settings_schema.Get_UserUsage])
async def get_userusage(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get User Usage
    """
    userusage = await settings_crud.get_userusage(session=session,user_id=current_user.id)
        
    return userusage