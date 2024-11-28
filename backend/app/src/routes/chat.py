import uuid
import json
from typing import Any,List

from fastapi import APIRouter, HTTPException

from app.src.deps import SessionDep_async,CurrentUser,async_engine,engine
from app.src.crud import chat as chat_crud
from app.src.schemas import chat as chat_schema
from app.src.crud import pgvector as pgvector_crud
from app.src.schemas import pgvector as pgvector_schema
from fastapi.responses import StreamingResponse
from app.core.config import settings
from app.src.engine.llms.chain import (
    translate_chain,
    summarize_chain,
    chatbot_chain,
    thinking_chatbot_chain
)
from app.src.engine.llms.memory import pg_vetorstore_with_memory, pg_vetorstore
from datetime import datetime
from requests.exceptions import RequestException
from langchain_redis import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langchain_community.callbacks import get_openai_callback

router = APIRouter()

REDIS_URL = settings.REDIS_URL

# Function to get or create a RedisChatMessageHistory instance
def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id, redis_url=REDIS_URL, ttl=60 * 60 * 24 * 7)

@router.post("/send_message",response_model=chat_schema.OutMessage)
async def send_message(*, session: SessionDep_async, current_user: CurrentUser,chat_in: chat_schema.SendMessage):
    
    # Get userllm
    llm_with_embbeding = await chat_crud.get_llm(session=session,user_id=current_user.id,
                                  user_llm_id=chat_in.user_llm_id,
                                  dept_llm_id=chat_in.dept_llm_id)
    llm = None
    embedding = None
    
    for item in llm_with_embbeding:
        if item.llm_id in [chat_in.user_llm_id,chat_in.dept_llm_id] and item.type == "llm":
            llm = item
        elif chat_in.user_llm_id is not None and item.gubun == 'user' and item.type == "embedding":
            embedding = item
        elif chat_in.dept_llm_id is not None and item.gubun == 'dept' and item.type == "embedding":
            embedding = item
            
    # Get a postgres vectorstore with memory
    memory = pg_vetorstore_with_memory(connection=engine,
                                       collection_name=chat_in.chat_id.hex,
                                       api_key=embedding.api_key,
                                       source=embedding.source,
                                       model=embedding.name,
                                       search_kwargs={"k": 3})
    
    retriever = None
    collection = None
    if chat_in.document_id is not None:
        document = await chat_crud.get_document(session=session,user_file_id=chat_in.document_id)
        collection = await pgvector_crud.get_collection(session=session,collection_id=document.collection_id)
        retriever = pg_vetorstore(connection=engine,
                                    collection_name=collection.name,
                                    api_key=embedding.api_key,
                                    source=embedding.source,
                                    model=embedding.name,
                                    async_mode=False
                                    ).as_retriever(search_type="mmr",
                                                   search_kwargs={'k': 2, 'lambda_mult': 0.8})
    
    # Get or create a RedisChatMessageHistory instance
    history = get_redis_history(chat_in.chat_id.hex)
    
    user_message = chat_schema.CreateMessage(user_id=current_user.id,
                                             chat_id=chat_in.chat_id,
                                             name=current_user.name,
                                             content=chat_in.input,
                                             is_user=True)
    messages = []
    messages.append(user_message)
    document_meta = "관련 문서 없음" if collection is None else collection.cmetadata
    chain = thinking_chatbot_chain(api_key=llm.api_key,
                                    source=llm.source,
                                    model=llm.name,
                                    memory=memory,
                                    document_meta=document_meta,
                                    retriever=retriever,)
    
    async def chain_astream(chain,input):
    
        chunks=[]
        thought = None
        input_token=0
        output_token=0
        
        if llm.source == "openai":
            callback_handler = get_openai_callback()
            with callback_handler as cb:
                async for chunk in chain.astream({'input':input}):
                    thought = chunk['thought']
                    answer = chunk['answer']
                    chunks.append(answer)
                    yield chat_schema.OutMessage(content=answer.content,
                                                thought=None,
                                                tools = {'retriever': ''},
                                                input_token=None,
                                                output_token=None,
                                                is_done=False).model_dump_json()
                input_token = cb.prompt_tokens
                output_token = cb.completion_tokens
        else:
             async for chunk in chain.astream({'input':input}):
                    thought = chunk['thought']
                    answer = chunk['answer']
                    chunks.append(answer)
                    yield chat_schema.OutMessage(content=answer.content,
                                                thought=None,
                                                tools = {'retriever': ''},
                                                input_token=None,
                                                output_token=None,
                                                is_done=False).model_dump_json()
            
        response=chunks[0]
        
        for chunk in chunks[1:]:
            response+=chunk
        
        bot_message = chat_schema.CreateMessage(user_id=current_user.id,
                        chat_id=chat_in.chat_id,
                        name="바르미",
                        content=response.content,
                        thought=thought['thought'],
                        tools=json.dumps({'retriever': thought['context']}, ensure_ascii=False),
                        is_user=False)
        
        messages.append(bot_message)

        usage = chat_schema.Usage(user_llm_id=chat_in.user_llm_id,
                                  dept_llm_id=chat_in.dept_llm_id,
                                  input_token=input_token,
                                  output_token=output_token)
        
        await chat_crud.create_messages(session=session,messages=messages,usage=usage)
        
        # Add messages to chat history
        await history.aadd_messages([HumanMessage(content=user_message.content,
                                                  additional_kwargs={
                                                      "user_id":str(user_message.user_id),
                                                      "name":user_message.name,
                                                      "create_date":user_message.create_date.strftime("%Y-%m-%d %H:%M:%S")
                                                      }),])
        
        await history.aadd_messages([AIMessage(content=str(bot_message.content),
                                               additional_kwargs={
                                                   "user_id":str(bot_message.user_id),
                                                   "name":bot_message.name,
                                                   "thought":bot_message.thought,
                                                   "tools" : json.loads(bot_message.tools),
                                                   "create_date":bot_message.create_date.strftime("%Y-%m-%d %H:%M:%S")
                                                   })])
        
        memory.save_context(
            inputs={
                "human": user_message.content
                },
            outputs={
                "ai": bot_message.content
                },
            )
        
        yield chat_schema.OutMessage(content=bot_message.content,
                                     thought=bot_message.thought,
                                     tools = json.loads(bot_message.tools),
                                     input_token=input_token,
                                     output_token=output_token,
                                     create_date=bot_message.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                                     is_done=True).model_dump_json()
        
    return StreamingResponse(chain_astream(chain,chat_in.input),media_type='text/event-stream')

@router.post("/create_chat",response_model=chat_schema.ResponseChat)
async def create_chat(*, session: SessionDep_async, current_user: CurrentUser,chat_in: chat_schema.CreateChat):
    chat = await chat_crud.create_chat(session=session,current_user=current_user,chat_in=chat_in)
    return chat

@router.get("/get_chat_list",response_model=List[chat_schema.GetChat])
async def get_chat_list(*, session: SessionDep_async, current_user: CurrentUser):
    chats = await chat_crud.get_chat_list(session=session,current_user=current_user)
    return chats

@router.get("/get_messages",response_model=List[chat_schema.ReponseMessages])
async def get_messages(*, session: SessionDep_async, current_user: CurrentUser, chat_id:uuid.UUID):
    
    # Redis에서 메시지를 가져오는 코드
    try:
        history = get_redis_history(chat_id.hex)
        messages = []
        for message in history.messages:
            msg = chat_schema.ReponseMessages(
                chat_id=chat_id,
                name=message.additional_kwargs["name"],
                content=message.content,
                thought=message.additional_kwargs["thought"] if "thought" in message.additional_kwargs else None,
                tools=message.additional_kwargs["tools"] if "tools" in message.additional_kwargs else None,
                is_user=message.type == "human",
                create_date=datetime.strptime(message.additional_kwargs["create_date"],"%Y-%m-%d %H:%M:%S")
            )
            messages.append(msg)
        
        if len(history.messages)==0:
            messages = await chat_crud.get_messages(session=session,current_user=current_user,chat_id=chat_id)
                    # Add messages to chat history
            for message in messages:
                if message.is_user:
                    await history.aadd_messages([HumanMessage(content=message.content,
                                                        additional_kwargs={
                                                            "user_id":str(message.user_id),
                                                            "name":message.name,
                                                            "create_date":message.create_date.strftime("%Y-%m-%d %H:%M:%S")
                                                            }),])
                else:
                    await history.aadd_messages([AIMessage(content=str(message.content),
                                                        additional_kwargs={
                                                            "user_id":str(message.user_id),
                                                            "name":message.name,
                                                            "thought":message.thought,
                                                            "tools" : json.loads(message.tools),
                                                            "create_date":message.create_date.strftime("%Y-%m-%d %H:%M:%S")
                                                            })])
            
    except Exception as e:
        print(e)
        messages = await chat_crud.get_messages(session=session,current_user=current_user,chat_id=chat_id)
    
    return messages

@router.get("/get_userllm",response_model=List[chat_schema.GetUserLLM])
async def get_userllm(*, session: SessionDep_async, current_user: CurrentUser):
    userllm = await chat_crud.get_userllm(session=session,user_id=current_user.id)
    
    if userllm is None:
        return HTTPException(status_code=404,detail="User LLM not found")
    
    return userllm

@router.get("/get_deptllm",response_model=List[chat_schema.GetDeptLLM])
async def get_deptllm(*, session: SessionDep_async, current_user: CurrentUser):
    userllm = await chat_crud.get_deptllm(session=session,user_id=current_user.id)
    
    if userllm is None:
        return HTTPException(status_code=404,detail="User LLM not found")
    
    return userllm

@router.get("/get_documents",response_model=List[chat_schema.GetDocument])
async def get_documents(*, session: SessionDep_async, current_user: CurrentUser):
    documents = await chat_crud.get_documents(session=session,current_user=current_user)
    
    if documents is None:
        return HTTPException(status_code=404,detail="Document not found")
    
    return documents

@router.put("/delete_chat")
async def delete_chat(*, session: SessionDep_async, current_user: CurrentUser,chat_in:chat_schema.Update_Chat):
    history = RedisChatMessageHistory(session_id=chat_in.id.hex, redis_url=REDIS_URL)
    history.clear()
    chat_in.delete_yn = True
    
    chat = await chat_crud.update_chat(session=session,chat=chat_in)
    return {"message":"Chat deleted successfully"}

@router.get("/get_chat",response_model=chat_schema.GetChat)
async def get_chat(*, session: SessionDep_async, current_user: CurrentUser,chat_id:uuid.UUID):
    chat = await chat_crud.get_chat(session=session,chat_id=chat_id)
    
    if chat is None:
        return HTTPException(status_code=404,detail="Chat not found")
    
    return chat