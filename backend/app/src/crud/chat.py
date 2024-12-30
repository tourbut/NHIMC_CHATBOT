from typing import List
import uuid

from sqlalchemy import literal_column
from app.models import *
from app.src.schemas import chat as chat_schema
from sqlmodel import select, union_all
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_userllm(*, session: AsyncSession,user_id:uuid.UUID) -> List[chat_schema.GetUserLLM]| None:
    try:
        statement = select(literal_column("'user'").label("gubun"),
                           UserLLM.id,
                           LLM.source,
                           LLM.name,
                           LLM.type,
                           LLM.url,
                           UserAPIKey.api_key).where(UserLLM.user_id == user_id,
                                                    UserLLM.llm_id == LLM.id,
                                                    UserLLM.api_id == UserAPIKey.id,
                                                    UserLLM.active_yn == True,
                                                    LLM.type == "llm")
        userllm = await session.exec(statement)
        if not userllm:
            return None
        else:
            return userllm.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def get_deptllm(*, session: AsyncSession,user_id:uuid.UUID) -> List[chat_schema.GetDeptLLM]| None:
    try:
        statement = select(literal_column("'user'").label("gubun"),
                           DeptLLM.id,
                           LLM.source,
                           LLM.name,
                           LLM.type,
                           LLM.url,
                           DeptAPIKey.api_key).where(UserDept.user_id==user_id,
                                                  DeptLLM.dept_id == UserDept.dept_id,
                                                    DeptLLM.llm_id == LLM.id,
                                                    DeptLLM.api_id == DeptAPIKey.id,
                                                    DeptLLM.active_yn == True,
                                                    LLM.type == "llm")
        userllm = await session.exec(statement)
        if not userllm:
            return None
        else:
            return userllm.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e    


async def get_llm(*, session: AsyncSession,user_id:uuid.UUID,user_llm_id:uuid.UUID,dept_llm_id:uuid.UUID) -> List[chat_schema.GetUserLLM]| None:
    try:
        
        statement1 = select(literal_column("'user'").label("gubun"),
                            UserLLM.id.label("llm_id"),
                            LLM.source,
                            LLM.name,
                            LLM.type,
                            LLM.url,
                            UserAPIKey.api_key.label("api_key")).where(UserLLM.user_id == user_id,
                                                        UserLLM.llm_id == LLM.id,
                                                        UserLLM.api_id ==UserAPIKey.id,
                                                        UserLLM.active_yn == True)

        statement2 = select(literal_column("'dept'").label("gubun"),
                            DeptLLM.id.label("llm_id"),
                            LLM.source,
                            LLM.name,
                            LLM.type,
                            LLM.url,
                            DeptAPIKey.api_key.label("api_key")).where(UserDept.user_id==user_id,
                                                        DeptLLM.dept_id == UserDept.dept_id,
                                                        DeptLLM.llm_id == LLM.id,
                                                        DeptLLM.api_id ==DeptAPIKey.id,
                                                        DeptLLM.active_yn == True)
        
        statement = union_all(statement1, statement2)
                            
        llm = await session.exec(statement)
        
        if not llm:
            return None
        else:
            return llm.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e



async def create_usage(*,session: AsyncSession, usage: chat_schema.Usage) -> UserUsage| None:
    try:
        db_obj = UserUsage.model_validate(usage)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def create_chat(*, session: AsyncSession, current_user: User,chat_in: chat_schema.CreateChat) -> Chats:
    try:
        chat = Chats.model_validate(chat_in,update={"user_id":current_user.id})
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def create_messages(*, session: AsyncSession, messages:List[Messages],  usage: chat_schema.Usage) -> Messages:
    try:
        for message in messages:
            db_obj = Messages.model_validate(message)
            session.add(db_obj)
            await session.flush()
        db_usage = UserUsage.model_validate(usage)
        session.add(db_usage)
        await session.flush()
        
        await session.commit()
        await session.refresh(db_obj)
        await session.refresh(db_usage)
        
        return db_obj
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def create_usage(*,session: AsyncSession, usage: chat_schema.Usage) -> UserUsage| None:
    try:
        db_obj = UserUsage.model_validate(usage)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_messages(*, session: AsyncSession,current_user: User, chat_id:uuid.UUID) -> List[chat_schema.ReponseMessages]:
    try:
        statement = select(Messages).where(Messages.chat_id == chat_id,
                                        Messages.user_id == current_user.id,
                                        Messages.delete_yn == False)
        messages = await session.exec(statement)
        return messages.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_chat_list(*, session: AsyncSession, current_user: User) -> List[chat_schema.GetChat]:
    try:
        statement = select(Chats).where(Chats.user_id == current_user.id,
                                        Chats.delete_yn == False)
        chats = await session.exec(statement)
        return chats.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_chat(*, session: AsyncSession, chat_id:uuid.UUID) -> Chats:
    try:
        chat = await session.get(Chats, chat_id)
        return chat
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def update_chat(*,session: AsyncSession, chat: chat_schema.Update_Chat) -> Chats:
    try:
        db_chat = await session.get(Chats, chat.id)
        
        if not db_chat:
            return None
        else:
            update_dict = chat.model_dump(exclude_unset=True)
            db_chat.sqlmodel_update(update_dict)
            db_chat.update_date = datetime.now()
            session.add(db_chat)
            await session.commit()
            await session.refresh(db_chat)
        return db_chat
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_documents(*, session: AsyncSession, current_user: User) -> List[chat_schema.GetDocument]:
    try:                       
        statement = select(UserFiles.file_name.label("title"),
                           UserFiles.file_desc.label("description"),
                           UserFiles.collection_id,
                           UserFiles.id.label("user_file_id")).where(
                                                               UserFiles.delete_yn == False,
                                                               UserFiles.embedding_yn == True,)
                                     
        documents = await session.exec(statement)
        return documents.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e


async def get_document(*, session: AsyncSession,user_file_id: uuid.UUID) -> chat_schema.GetDocument:
    try:                       
        statement = select(UserFiles.file_name.label("title"),
                           UserFiles.file_desc.label("description"),
                           UserFiles.collection_id,
                           UserFiles.id.label("user_file_id")).where(UserFiles.id == user_file_id)
        documents = await session.exec(statement)
        return documents.first()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    