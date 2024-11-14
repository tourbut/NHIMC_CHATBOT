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