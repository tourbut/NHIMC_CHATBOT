import uuid

from typing import List
from app.models import *
from app.src.schemas import archive as archive_schema
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_file_list(*,session: AsyncSession,user_id:uuid.UUID) -> UserFiles:
    query = select(UserFiles.id,
                   UserFiles.file_name,
                   UserFiles.file_size,
                   UserFiles.file_ext,
                   UserFiles.file_desc,
                   ).where(UserFiles.user_id == user_id,
                           UserFiles.delete_yn == False)
    files = await session.exec(query)
    if files is None:
        return None
    else:
        return files.all()

async def delete_file(*,session: AsyncSession,user_id:uuid.UUID,file_id:uuid.UUID) -> UserFiles| None:
    file = await session.get(UserFiles, file_id)
    if not file:
        return None
    else:
        file.delete_yn = True
        session.add(file)
        await session.commit()
        await session.refresh(file)
        return file

async def get_userllm(*, session: AsyncSession,user_id:uuid.UUID,llm_type:str) -> archive_schema.GetUserLLM| None:
    statement = select(UserLLM.id,
                       LLM.source,
                       LLM.name,
                       LLM.url,
                       UserAPIKey.api_key,
                       UserLLM.llm_id).where(UserLLM.user_id == user_id,
                                                   UserLLM.llm_id == LLM.id,
                                                   UserLLM.api_id ==UserAPIKey.id,
                                                   UserLLM.active_yn == True,
                                                   LLM.type==llm_type)
    userllm = await session.exec(statement)
    if not userllm:
        return None
    else:
        return userllm.first()


async def create_usage(*,session: AsyncSession, usage: archive_schema.Usage) -> UserUsage| None:
    db_obj = UserUsage.model_validate(usage)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def create_file(*,session: AsyncSession, file: archive_schema.FileUpload,user_id:uuid.UUID) -> UserFiles:
    db_obj = UserFiles.model_validate(file,update={"user_id":user_id})
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_file(*,session: AsyncSession, file: UserFiles) -> UserFiles:
    db_file = await session.get(UserFiles, file.id)
    
    if not db_file:
        return None
    else:
        update_dict = file.model_dump(exclude_unset=True)
        db_file.sqlmodel_update(update_dict)
        db_file.update_date = datetime.now()
        session.add(db_file)
        await session.commit()
        await session.refresh(db_file)
    return db_file

async def get_file(*,session: AsyncSession,file_id:uuid.UUID) -> UserFiles| None:
    file = await session.get(UserFiles, file_id)
    if not file:
        return None
    else:
        return file
    
async def create_botdocument(*, session: AsyncSession, current_user:User, document_in: archive_schema.CreateBotDocument) -> BotDocuments:
    try:
        db_obj = BotDocuments.model_validate(document_in,update={"user_id":current_user.id})
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    except Exception as e:
        print(e)
        await session.rollback()
        raise e