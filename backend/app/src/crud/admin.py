from typing import List
from app.models import *
from app.src.schemas import admin as admin_schema
from sqlmodel import Session, select
from app.src.utils.fromOracle import get_isis_dept

async def create_dept(*, session: Session) -> List[Dept]:
    depts=await get_isis_dept()
    
    statement = select(Dept)
    db_dept = await session.exec(statement)
    rslt= db_dept.all()
    if rslt:
        return rslt
    else:
        for dept in depts:
            obj = Dept(dept_cd=dept[0], dept_nm=dept[1])
            db_obj = Dept.model_validate(obj)
            session.add(db_obj)
            await session.flush()
    
        await session.commit()
        return db_obj

async def create_llm(*, session: Session, llm_create: admin_schema.LLMCreate) -> LLM:
    db_obj = LLM.model_validate(llm_create)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_llm(*, session: Session, llm_update: admin_schema.Get_LLM) -> LLM:
    llm = await session.get(LLM, llm_update.id)
    
    if not llm:
        return None
    else:
        update_dict = llm_update.model_dump(exclude_unset=True)
        llm.sqlmodel_update(update_dict)
        llm.update_date = datetime.now()
        session.add(llm)
        await session.commit()
        await session.refresh(llm)

    return llm

async def get_llm(*, session: Session) -> List[LLM]| None:
    statement = select(LLM)
    llm = await session.exec(statement)

    if not llm:
        return None
    else:
        return llm.all()
    
async def create_apikey(*, session: Session, apikey_in: admin_schema.Create_Apikey) -> DeptAPIKey:
    db_obj = DeptAPIKey.model_validate(apikey_in)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def get_apikey(*, session: Session) -> List[admin_schema.Get_Apikey]| None:
    
    statement = select(DeptAPIKey)
    
    apikey = await session.exec(statement)
    if not apikey:
        return None
    else:
        return apikey.all()

async def update_apikey(*, session: Session, apikey_update: admin_schema.Get_Apikey) -> DeptAPIKey:
    apikey = await session.get(DeptAPIKey, apikey_update.id)
    
    if not apikey:
        return None
    else:
        update_dict = apikey_update.model_dump(exclude_unset=True)
        apikey.sqlmodel_update(update_dict)
        apikey.update_date = datetime.now()
        session.add(apikey)
        await session.commit()
        await session.refresh(apikey)

    return apikey

async def get_dept(*, session: Session) -> List[Dept]| None:
    statement = select(Dept).where(Dept.is_active == True)
    dept = await session.exec(statement)
    if not dept:
        return None
    else:
        return dept.all()