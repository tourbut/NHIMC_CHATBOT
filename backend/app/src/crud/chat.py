from typing import List
import uuid
from app.models import *
from app.src.schemas import chat as chat_schema
from sqlmodel import select, union_all
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_userllm(*, session: AsyncSession,user_id:uuid.UUID) -> List[chat_schema.GetUserLLM]| None:
    try:
        statement = select(UserLLM.id,
                        LLM.source,
                        LLM.name,
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
        
async def get_llm(*, session: AsyncSession,user_id:uuid.UUID,user_llm_id:uuid.UUID) -> chat_schema.GetUserLLM| None:
    try:
        statement = select(UserLLM.id,
                        LLM.source,
                        LLM.name,
                        UserAPIKey.api_key).where(UserLLM.user_id == user_id,
                                                    UserLLM.llm_id == LLM.id,
                                                    UserLLM.api_id ==UserAPIKey.id,
                                                    UserLLM.active_yn == True,
                                                    UserLLM.id == user_llm_id)
        userllm = await session.exec(statement)
        if not userllm:
            return None
        else:
            return userllm.first()
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
    
async def create_chat(*, session: AsyncSession, current_user: User,title:str,user_llm_id:uuid.UUID) -> Chats:
    try:
        chat = Chats(user_id=current_user.id,
                    title=title,
                    user_llm_id=user_llm_id)
        
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
        archive_statement = select(Archive.title.label("title"),
                                   Archive.collection_id).where(Archive.user_id == current_user.id,
                                                               Archive.delete_yn == False,
                                                               Archive.embedding_yn == True)
                                   
        userfiles_statement = select(UserFiles.file_name.label("title"),
                                     UserFiles.collection_id).where(UserFiles.user_id == current_user.id,
                                                               UserFiles.delete_yn == False,
                                                               UserFiles.embedding_yn == True)
                                     
        statement = union_all(archive_statement, userfiles_statement)
        
        documents = await session.exec(statement)
        return documents.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    