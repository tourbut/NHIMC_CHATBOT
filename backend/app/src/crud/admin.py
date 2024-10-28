from typing import List
from app.models import *
from app.src.schemas import admin as admin_schema
from sqlmodel import Session, select


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