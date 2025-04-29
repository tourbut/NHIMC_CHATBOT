import json
from typing import List
import uuid
from app.models import *
from app.src.schemas import chat as chat_schema
from sqlmodel import or_,and_, select, union_all,union,literal_column
from sqlalchemy.orm import aliased
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_userllm(*, session: AsyncSession,user_id:uuid.UUID) -> List[chat_schema.GetUserLLM]| None:
    try:
        statement = select(literal_column("'user'").label("gubun"),
                           UserLLM.id,
                           UserLLM.llm_id,
                           LLM.source,
                           LLM.name,
                           LLM.type,
                           LLM.url,
                           UserAPIKey.api_key).where(UserLLM.user_id == user_id,
                                                    UserLLM.llm_id == LLM.id,
                                                    UserLLM.api_id == UserAPIKey.id,
                                                    UserLLM.active_yn == True,
                                                    LLM.type == "llm",
                                                    LLM.is_active == True)
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
                           DeptLLM.llm_id,
                           LLM.source,
                           LLM.name,
                           LLM.type,
                           LLM.url,
                           LLM.is_agent,
                           DeptAPIKey.api_key).where(UserDept.user_id==user_id,
                                                  DeptLLM.dept_id == UserDept.dept_id,
                                                    DeptLLM.llm_id == LLM.id,
                                                    DeptLLM.api_id == DeptAPIKey.id,
                                                    DeptLLM.active_yn == True,
                                                    LLM.type == "llm",
                                                    LLM.is_active == True)
        userllm = await session.exec(statement)
        if not userllm:
            return None
        else:
            return userllm.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e    


async def get_llm(*, session: AsyncSession,user_id:uuid.UUID) -> List[chat_schema.GetUserLLM]| None:
    try:
        
        statement1 = select(literal_column("'user'").label("gubun"),
                            UserLLM.id.label("llm_id"),
                            LLM.id,
                            LLM.source,
                            LLM.name,
                            LLM.type,
                            LLM.url,
                            UserAPIKey.api_key.label("api_key")).where(UserLLM.user_id == user_id,
                                                        UserLLM.llm_id == LLM.id,
                                                        UserLLM.api_id ==UserAPIKey.id,
                                                        UserLLM.active_yn == True,
                                                        LLM.is_active == True)

        statement2 = select(literal_column("'dept'").label("gubun"),
                            DeptLLM.id.label("llm_id"),
                            LLM.id,
                            LLM.source,
                            LLM.name,
                            LLM.type,
                            LLM.url,
                            DeptAPIKey.api_key.label("api_key")).where(UserDept.user_id==user_id,
                                                        DeptLLM.dept_id == UserDept.dept_id,
                                                        DeptLLM.llm_id == LLM.id,
                                                        DeptLLM.api_id ==DeptAPIKey.id,
                                                        DeptLLM.active_yn == True,
                                                        LLM.is_active == True)
        
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

async def get_messages(*, session: AsyncSession,current_user: User, id:uuid.UUID) -> List[chat_schema.ReponseMessages]:
    try:
        statement = select(Messages).where(
            or_(
                Messages.chat_id == id,
                and_(
                    Messages.chatbot_id == id,
                    Messages.chat_id == None
                )
            ),
            Messages.user_id == current_user.id,
            Messages.delete_yn == False
        ).order_by(Messages.create_date)
        
        messages = await session.exec(statement)
        return messages.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def delete_messages(*, session: AsyncSession, current_user: User, id:uuid.UUID):
    try:
        statement = select(Messages).where(
            or_(
                Messages.chat_id == id,
                and_(
                    Messages.chatbot_id == id,
                    Messages.chat_id == None
                )
            ),
            Messages.user_id == current_user.id,
            Messages.delete_yn == False)
        
        tmp_messages = await session.exec(statement)
        
        messages = tmp_messages.all()
        
        if not messages:
            return None
        else:
            for message in messages:
                message.delete_yn = True
                session.add(message)
                await session.flush()
                
            await session.commit()
            
            for message in messages:
                await session.refresh(message)
                
            return message
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

async def get_chat(*, session: AsyncSession, chat_id:uuid.UUID) -> chat_schema.GetChat:
    try:
        statement = select(Chats.id,
                           Chats.title,
                           Chats.user_llm_id,
                           Chats.dept_llm_id,
                           Chats.user_file_id,
                           Chats.chatbot_id,
                           ChatBot.is_agent).where(Chats.chatbot_id == ChatBot.id,
                                                   Chats.id==chat_id)

        chat = await session.exec(statement)
        return chat.first()
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
  

# ChatBot
async def create_chatbot(*, session: AsyncSession, current_user: User, chatbot_in: chat_schema.CreateChatBot) -> chat_schema.Create_Out_ChatBot:
    try:
        chatbot = ChatBot.model_validate(chatbot_in,update={"user_id":current_user.id})
        session.add(chatbot)
        await session.commit()
        await session.refresh(chatbot)
        return chatbot
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def update_chatbot(*, session: AsyncSession, current_user: User, chatbot_in: chat_schema.UpdateChatBot) -> ChatBot:
    try:
        chatbot = await session.get(ChatBot, chatbot_in.id)
        if not chatbot:
            return None
        else:
            if chatbot.user_id != current_user.id:
                raise Exception("Not Authorized")
            update_dict = chatbot_in.model_dump(exclude_unset=True)
            chatbot.sqlmodel_update(update_dict,update={"search_kwargs":json.dumps(chatbot_in.search_kwargs)})
            chatbot.update_date = datetime.now()
            session.add(chatbot)
            await session.commit()
            await session.refresh(chatbot)
        return chatbot
    
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def get_chatbot(*, session: AsyncSession, chatbot_id:uuid.UUID) -> chat_schema.Get_Out_ChatBot:
    try:
        statement = select(ChatBot).where(ChatBot.id == chatbot_id)
        chatbot = await session.exec(statement)
        return chatbot.first()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
                            

async def get_chatbot_list_by_userid(*, session: AsyncSession, current_user: User) -> List[chat_schema.Get_Out_ChatBot]:
    try:
        statement = select(ChatBot).where(ChatBot.user_id == current_user.id,
                                           ChatBot.delete_yn == False)
        chatbots = await session.exec(statement)
        return chatbots.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_chatbot_list_by_public(*, session: AsyncSession, current_user: User) -> List[chat_schema.Get_Out_ChatBot]:
    try:
        
        statement1 = select(ChatBot).where(ChatBot.user_id == current_user.id,
                                           ChatBot.delete_yn == False)
        statement2 = select(ChatBot).where(ChatBot.is_public == True,
                                          ChatBot.delete_yn == False)
        statement = union(statement1, statement2)
        chatbots = await session.exec(statement)
        return chatbots.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_chatbot_list(*, session: AsyncSession) -> List[chat_schema.Get_Out_ChatBot]:
    try:
        statement = select(ChatBot).where(ChatBot.delete_yn == False)
        chatbots = await session.exec(statement)
        return chatbots.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

    
async def create_bottools(*, session: AsyncSession, bottools: chat_schema.CreateBotTools) -> BotTools:
    try:
        db_obj = BotTools.model_validate(bottools)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def create_tools(*, session: AsyncSession, tools: chat_schema.CreateTools) -> Tools:
    try:
        db_obj = Tools.model_validate(tools)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def create_botdocument(*, session: AsyncSession, current_user:User, document_in: chat_schema.CreateBotDocument) -> BotDocuments:
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

async def get_botdocuments(*, session: AsyncSession, current_user: User) -> List[chat_schema.Get_Out_Document]:
    """
    Get documents for chatbot
    유저가 속한 부서의 문서만 조회
    """
    try:                       
        statement = select( BotDocuments.id,
                            UserFiles.file_name.label("title"),
                            UserFiles.file_desc.label("description"),
                            UserFiles.collection_id,
                            UserFiles.id.label("user_file_id"),
                            BotDocuments.request_dept_id,
                            Dept.dept_nm.label("request_dept_nm"),
                            BotDocuments.is_active).where(UserFiles.delete_yn == False,
                                                          UserFiles.embedding_yn == True,
                                                          UserFiles.id == BotDocuments.userfile_id,
                                                          BotDocuments.request_dept_id == Dept.id,
                                                          UserDept.user_id == current_user.id,
                                                          UserDept.dept_id == BotDocuments.request_dept_id)
                                     
        documents = await session.exec(statement)
        return documents.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_chatbot_alldata(*, session: AsyncSession, chatbot_id:uuid.UUID) -> chat_schema.GetChatbotAllData:
    try:
        user_llm = aliased(LLM, name="user_llm")
        dept_llm = aliased(LLM, name="dept_llm")
        embedding_llm = aliased(LLM, name="embedding_llm")
        embedding_userllm = aliased(UserLLM, name="embedding_userllm")
        
        statement = select(
            ChatBot.id,
            ChatBot.instruct_prompt,
            ChatBot.thought_prompt,
            ChatBot.user_llm_id,
            ChatBot.dept_llm_id,
            user_llm.name.label("userllm_name"),
            UserLLM.llm_id.label("userllm_id"),
            dept_llm.name.label("deptllm_name"),
            DeptLLM.llm_id.label("deptllm_id"),
            embedding_llm.name.label("embedding_name"),
            embedding_userllm.llm_id.label("embedding_id"),
            UserFiles.file_name.label("file_title"),
            UserFiles.file_desc.label("file_description"),
            UserFiles.collection_id,
            ChatBot.bottools_id,
            ChatBot.temperature,
            ChatBot.search_kwargs,
            ).join(UserLLM, UserLLM.id == ChatBot.user_llm_id, isouter=True) \
             .join(DeptLLM, DeptLLM.id == ChatBot.dept_llm_id, isouter=True) \
             .join(UserFiles, UserFiles.id == ChatBot.user_file_id, isouter=True) \
             .join(embedding_userllm, embedding_userllm.id == UserFiles.embedding_user_llm_id, isouter=True) \
             .join(user_llm, user_llm.id == UserLLM.llm_id, isouter=True) \
             .join(dept_llm, dept_llm.id == DeptLLM.llm_id, isouter=True) \
             .join(embedding_llm, embedding_llm.id == embedding_userllm.llm_id, isouter=True) \
            .where(ChatBot.id == chatbot_id)
        
        chatbot = await session.exec(statement)
        return chatbot.first()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e