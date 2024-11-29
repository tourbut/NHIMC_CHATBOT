from typing import Any, Annotated, List
from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.src.deps import SessionDep_async,CurrentUser
from app.src.crud import admin as admin_crud
from app.src.schemas import admin as admin_schema

from app.core.config import settings

router = APIRouter()

@router.get("/get_llm", response_model=List[admin_schema.Get_LLM])
async def get_llm(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get LLM Settings
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    llms = await admin_crud.get_llm(session=session)
    return llms

@router.post("/create_llm")
async def create_llm(*, session: SessionDep_async, current_user: CurrentUser, llm_create: admin_schema.LLMCreate) -> Any:
    """
    Create LLM
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    llm = await admin_crud.create_llm(session=session, llm_create=llm_create)

@router.put("/update_llm", response_model=admin_schema.Get_LLM)
async def update_llm(*, session: SessionDep_async, current_user: CurrentUser, llm_update: admin_schema.Get_LLM) -> Any:
    """
    Update LLM 
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    llm = await admin_crud.update_llm(session=session, llm_update=llm_update)
    return llm

@router.post("/create_dept")
async def create_dept(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Create Department
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    dept = await admin_crud.create_dept(session=session)
    
@router.post("/create_apikey")
async def create_apikey(*, session: SessionDep_async, apikey_in: admin_schema.Create_Apikey, current_user: CurrentUser) -> Any:
    """
    Create API Key
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    apikey = await admin_crud.create_apikey(session=session, apikey_in=apikey_in)
    
@router.get("/get_apikey", response_model=List[admin_schema.Get_Apikey])
async def get_apikey(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get API Key
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    apikey = await admin_crud.get_apikey(session=session)
    return apikey

@router.put("/update_apikey")
async def update_apikey(*, session: SessionDep_async, apikey_update: admin_schema.Get_Apikey, current_user: CurrentUser) -> Any:
    """
    Update API Key
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    apikey = await admin_crud.update_apikey(session=session, apikey_update=apikey_update)
    
@router.get("/get_dept", response_model=List[admin_schema.Get_Dept])
async def get_dept(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get Department
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    dept = await admin_crud.get_dept(session=session)
    return dept


@router.get("/get_deptllm", response_model=List[admin_schema.Get_DeptLLM])
async def get_deptllm(*, session: SessionDep_async, current_user: CurrentUser) -> Any:
    """
    Get User LLM
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    userllm = await admin_crud.get_deptllm(session=session)
    return userllm

@router.post("/create_deptllm")
async def create_deptllm(*, session: SessionDep_async, deptllm_in: admin_schema.Create_DeptLLM, current_user: CurrentUser) -> Any:
    """
    Create User LLM
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    userllm = await admin_crud.create_deptllm(session=session, deptllm_in=deptllm_in)
    
@router.put("/update_deptllm")
async def update_deptllm(*, session: SessionDep_async, deptllm_update: admin_schema.Update_DeptLLM, current_user: CurrentUser) -> Any:
    """
    Update User LLM
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    userllm = await admin_crud.update_deptllm(session=session, deptllm_update=deptllm_update)
    
@router.get("/get_deptusage",response_model=List[admin_schema.Get_DeptUsage])
async def get_deptusage(*, session: SessionDep_async, current_user: CurrentUser,dept_id) -> Any:
    """
    Get User Usage
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    deptusage = await admin_crud.get_deptusage_all(session=session,dept_id=dept_id)
        
    return deptusage