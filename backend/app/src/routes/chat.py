import uuid
import json
from typing import Any,List

from fastapi import APIRouter, HTTPException, Request

from app.src.deps import SessionDep_async,CurrentUser,async_engine,engine, redis_client
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
    thinking_chatbot_chain,
    thinking_chatbot_NoDoc_chain
)
from app.src.engine.llms.memory import pg_vetorstore_with_memory, pg_vetorstore,pg_ParentDocumentRetriever
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
def get_redis_history(session_id: str,redis_client) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id,
                                   ttl=60*60*24*7,
                                   redis_client=redis_client)

@router.post("/create_chat",response_model=chat_schema.ResponseChat)
async def create_chat(*, session: SessionDep_async, current_user: CurrentUser,chat_in: chat_schema.CreateChat):
    chat = await chat_crud.create_chat(session=session,current_user=current_user,chat_in=chat_in)
    return chat

@router.get("/get_chat_list",response_model=List[chat_schema.GetChat])
async def get_chat_list(*, session: SessionDep_async, current_user: CurrentUser):
    chats = await chat_crud.get_chat_list(session=session,current_user=current_user)
    return chats

@router.post("/send_message",response_model=chat_schema.OutMessage)
async def send_message(*,session: SessionDep_async, current_user: CurrentUser,chat_in: chat_schema.SendMessage):
    
    # Get userllm
    llm_with_embbeding = await chat_crud.get_llm(session=session,user_id=current_user.id)
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
                                       base_url=embedding.url,
                                       search_kwargs={"k": 3})
    
    retriever = None
    document = None
    if chat_in.document_id is not None:
        document = await chat_crud.get_document(session=session,user_file_id=chat_in.document_id)
        collection = await pgvector_crud.get_collection(session=session,collection_id=document.collection_id)
        retriever = pg_ParentDocumentRetriever(connection=engine,
                                    collection_name=collection.name,
                                    api_key=embedding.api_key,
                                    source=embedding.source,
                                    model=embedding.name,
                                    base_url=embedding.url,
                                    async_mode=False,
                                    splitter_options=collection.cmetadata
                                    )
    redis = await redis_client()
    # Get or create a RedisChatMessageHistory instance
    history = get_redis_history(chat_in.chat_id.hex,redis)
    
    user_message = chat_schema.CreateMessage(user_id=current_user.id,
                                             chat_id=chat_in.chat_id,
                                             name=current_user.name,
                                             content=chat_in.input,
                                             is_user=True,
                                             create_date=datetime.now(),
                                             update_date=datetime.now())
    messages = []
    messages.append(user_message)
    
    document_meta = "관련 문서 없음" if document is None else {'title':document.title,
                                                              'description':document.description,}
    if document is None:
        #제공된 문서가 없는 경우
        chain = thinking_chatbot_NoDoc_chain(api_key=llm.api_key,
                                             source=llm.source,
                                             model=llm.name,
                                             base_url=llm.url,
                                             memory=memory,
                                             )
    else:
        #제공된 문서가 있는 경우
        chain = thinking_chatbot_chain(api_key=llm.api_key,
                                        source=llm.source,
                                        model=llm.name,
                                        base_url=llm.url,
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
            
            input_token = chunks[0].usage_metadata['input_tokens']
            output_token = chunks[0].usage_metadata['output_tokens']
            
        response=chunks[0]
        
        for chunk in chunks[1:]:
            response+=chunk
        
        usage = chat_schema.Usage(user_llm_id=chat_in.user_llm_id,
                                  dept_llm_id=chat_in.dept_llm_id,
                                  input_token=input_token,
                                  output_token=output_token)
        
        bot_message = chat_schema.CreateMessage(user_id=current_user.id,
                        chat_id=chat_in.chat_id,
                        name="바르미",
                        content=response.content,
                        thought=thought.get('thought', ''),
                        tools=json.dumps({'retriever': thought.get('context', '') }, ensure_ascii=False),
                        is_user=False,
                        create_date=datetime.now(),
                        update_date=datetime.now())
        
        messages.append(bot_message)
        
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

@router.get("/get_messages",response_model=List[chat_schema.ReponseMessages])
async def get_messages(*, session: SessionDep_async, current_user: CurrentUser, id:uuid.UUID):
    
    # Redis에서 메시지를 가져오는 코드
    try:
        
        history = get_redis_history(id.hex,redis_client=await redis_client())
        messages = []
        for message in history.messages:
            msg = chat_schema.ReponseMessages(
                name=message.additional_kwargs["name"],
                content=message.content,
                thought=message.additional_kwargs["thought"] if "thought" in message.additional_kwargs else None,
                tools=message.additional_kwargs["tools"] if "tools" in message.additional_kwargs else None,
                is_user=message.type == "human",
                create_date=datetime.strptime(message.additional_kwargs["create_date"],"%Y-%m-%d %H:%M:%S")
            )
            messages.append(msg)
        
        if len(history.messages)==0:
            db_messages = await chat_crud.get_messages(session=session,current_user=current_user,id=id)
            # Add messages to chat history
            messages = []
            for message in db_messages:
                if message.is_user:
                    messages.append(chat_schema.ReponseMessages(
                                                                name=message.name,
                                                                content=message.content,
                                                                thought=None,
                                                                tools=None,
                                                                is_user=True,
                                                                create_date=message.create_date))
                    await history.aadd_messages([HumanMessage(content=message.content,
                                                        additional_kwargs={
                                                            "user_id":str(message.user_id),
                                                            "name":message.name,
                                                            "create_date":message.create_date.strftime("%Y-%m-%d %H:%M:%S")
                                                            }),])
                else:
                    messages.append(chat_schema.ReponseMessages(
                                                                name=message.name,
                                                                content=message.content,
                                                                thought=message.thought,
                                                                tools=json.loads(message.tools),
                                                                is_user=False,
                                                                create_date=message.create_date))
                        
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
        messages = await chat_crud.get_messages(session=session,current_user=current_user,id=id)
    
    return messages


@router.get("/get_messages_by_chatbot",response_model=List[chat_schema.ReponseMessages])
async def get_messages_by_chatbot(*, session: SessionDep_async, current_user: CurrentUser, id:uuid.UUID):
    
    # Redis에서 메시지를 가져오는 코드
    try:
        
        history = get_redis_history(id.hex,redis_client=await redis_client())
        messages = []
        for message in history.messages:
            msg = chat_schema.ReponseMessages(
                name=message.additional_kwargs["name"],
                content=message.content,
                thought=message.additional_kwargs["thought"] if "thought" in message.additional_kwargs else None,
                tools=message.additional_kwargs["tools"] if "tools" in message.additional_kwargs else None,
                is_user=message.type == "human",
                create_date=datetime.strptime(message.additional_kwargs["create_date"],"%Y-%m-%d %H:%M:%S")
            )
            messages.append(msg)
        
        if len(history.messages)==0:
            db_messages = await chat_crud.get_messages_by_chatbot_id(session=session,current_user=current_user,id=id)
            # Add messages to chat history
            messages = []
            for message in db_messages:
                if message.is_user:
                    messages.append(chat_schema.ReponseMessages(
                                                                name=message.name,
                                                                content=message.content,
                                                                thought=None,
                                                                tools=None,
                                                                is_user=True,
                                                                create_date=message.create_date))
                    await history.aadd_messages([HumanMessage(content=message.content,
                                                        additional_kwargs={
                                                            "user_id":str(message.user_id),
                                                            "name":message.name,
                                                            "create_date":message.create_date.strftime("%Y-%m-%d %H:%M:%S")
                                                            }),])
                else:
                    messages.append(chat_schema.ReponseMessages(
                                                                name=message.name,
                                                                content=message.content,
                                                                thought=message.thought,
                                                                tools=json.loads(message.tools),
                                                                is_user=False,
                                                                create_date=message.create_date))
                        
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
        messages = await chat_crud.get_messages_by_chatbot_id(session=session,current_user=current_user,id=id)
    
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

@router.post("/create_chatbot",response_model=chat_schema.Create_Out_ChatBot)
async def create_chatbot(*, session: SessionDep_async, current_user: CurrentUser,chatbot_in: chat_schema.CreateChatBot):
    chat = await chat_crud.create_chatbot(session=session,current_user=current_user,chatbot_in=chatbot_in)
    return chat

@router.put("/update_chatbot",response_model=chat_schema.Update_Out_ChatBot)
async def update_chatbot(*, session: SessionDep_async, current_user: CurrentUser,chatbot_in: chat_schema.UpdateChatBot):
    try:
        chat = await chat_crud.update_chatbot(session=session,current_user=current_user,chatbot_in=chatbot_in)
        return chat
    except Exception as e:
        return HTTPException(status_code=404,detail=e)

@router.get("/get_chatbot_list_by_userid",response_model=List[chat_schema.Get_Out_ChatBot])
async def get_chatbot_list_by_userid(*, session: SessionDep_async, current_user: CurrentUser):
    chatbots = await chat_crud.get_chatbot_list_by_userid(session=session,current_user=current_user)
    return chatbots

@router.get("/get_chatbot_list_by_public",response_model=List[chat_schema.Get_Out_ChatBot])
async def get_chatbot_list_by_public(*, session: SessionDep_async, current_user: CurrentUser):
    chatbots = await chat_crud.get_chatbot_list_by_public(session=session,current_user=current_user)
    return chatbots

@router.get("/get_chatbot",response_model=chat_schema.Get_Out_ChatBot)
async def get_chatbot(*, session: SessionDep_async, current_user: CurrentUser,chatbot_id:uuid.UUID):
    chatbot = await chat_crud.get_chatbot(session=session,chatbot_id=chatbot_id)
    
    if chatbot is None:
        return HTTPException(status_code=404,detail="Chatbot not found")
    
    return chatbot

@router.post("/create_botdocument",response_model=chat_schema.Create_Out_Document)
async def create_botdocument(*, session: SessionDep_async, current_user: CurrentUser,document_in: chat_schema.CreateBotDocument):
    document = await chat_crud.create_botdocument(session=session,current_user=current_user,document_in=document_in)
    return document

@router.get("/get_botdocuments",response_model=List[chat_schema.Get_Out_Document])
async def get_botdocuments(*, session: SessionDep_async, current_user: CurrentUser):
    documents = await chat_crud.get_botdocuments(session=session,current_user=current_user)
    
    if documents is None:
        return HTTPException(status_code=404,detail="Document not found")
    
    return documents

@router.post("/send_message_bot",response_model=chat_schema.OutMessage)
async def send_message_bot(*,session: SessionDep_async, current_user: CurrentUser,chat_in: chat_schema.SendMessageToChatbot):
    
    chabot_data = await chat_crud.get_chatbot_alldata(session=session,chatbot_id=chat_in.chatbot_id)
    all_user_model = await chat_crud.get_llm(session=session,user_id=current_user.id)
    
    userllm, deptllm, embedding = None, None, None

    for item in all_user_model:
        if item.id == chabot_data.userllm_id and item.type == "llm":
            userllm = item
        elif item.id == chabot_data.deptllm_id and item.type == "llm":
            deptllm = item
        elif item.id == chabot_data.embedding_id and item.type == "embedding":
            embedding = item
            
    llm = userllm if userllm else deptllm
    
    retriever = None
    
    # Get a postgres vectorstore with memory
    memory = pg_vetorstore_with_memory(connection=engine,
                                       collection_name=chat_in.chat_id.hex if chat_in.chat_id is not None else chat_in.chatbot_id.hex,
                                       api_key=embedding.api_key,
                                       source=embedding.source,
                                       model=embedding.name,
                                       base_url=embedding.url,
                                       search_kwargs={"k": 3})
    
    if chabot_data.collection_id is not None:
        collection = await pgvector_crud.get_collection(session=session,collection_id=chabot_data.collection_id)
        retriever = pg_ParentDocumentRetriever(connection=engine,
                                    collection_name=collection.name,
                                    api_key=embedding.api_key,
                                    source=embedding.source,
                                    model=embedding.name,
                                    base_url=embedding.url,
                                    async_mode=False,
                                    splitter_options=collection.cmetadata
                                    )
    
    document_meta = "관련 문서 없음" if chabot_data.file_title is None else {'title':chabot_data.file_title,
                                                              'description':chabot_data.file_description,}
    
    redis = await redis_client()
    # Get or create a RedisChatMessageHistory instance
    history = get_redis_history(chat_in.chat_id.hex if chat_in.chat_id is not None else chat_in.chatbot_id.hex
                                ,redis)
    
    user_message = chat_schema.CreateMessage(user_id=current_user.id,
                                             chat_id = chat_in.chat_id,
                                             chatbot_id=chat_in.chatbot_id,
                                             name=current_user.name,
                                             content=chat_in.input,
                                             is_user=True,
                                             create_date=datetime.now(),
                                             update_date=datetime.now())
    messages = []
    messages.append(user_message)
    
    chain = chatbot_chain(instruct_prompt=chabot_data.instruct_prompt,
                            thought_prompt=chabot_data.thought_prompt,
                            api_key=llm.api_key,
                            source=llm.source,
                            model=llm.name,
                            base_url=llm.url,
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
                                                is_done=False).model_dump_json() + '\n'
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
                                            is_done=False).model_dump_json() + '\n'
            
            input_token = chunks[0].usage_metadata['input_tokens']
            output_token = chunks[0].usage_metadata['output_tokens']
            
        response=chunks[0]
        
        for chunk in chunks[1:]:
            response+=chunk
        
        usage = chat_schema.Usage(user_llm_id=chabot_data.user_llm_id,
                                  dept_llm_id=chabot_data.dept_llm_id,
                                  input_token=input_token,
                                  output_token=output_token)
        
        bot_message = chat_schema.CreateMessage(user_id=current_user.id,
                                             chat_id = chat_in.chat_id,
                        chatbot_id=chat_in.chatbot_id,
                        name="바르미",
                        content=response.content,
                        thought=thought.get('thought', ''),
                        tools=json.dumps({'retriever': thought.get('document', '') }, ensure_ascii=False),
                        is_user=False,
                        create_date=datetime.now(),
                        update_date=datetime.now())
        messages.append(bot_message)
        
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
        
        final_response = chat_schema.OutMessage(content=bot_message.content,
                                     thought=bot_message.thought,
                                     tools = json.loads(bot_message.tools) if bot_message.tools else {'retriever': ''},
                                     input_token=input_token,
                                     output_token=output_token,
                                     create_date=bot_message.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                                     is_done=True).model_dump_json()
        yield final_response + '\n'
        
    return StreamingResponse(chain_astream(chain,chat_in.input),media_type='application/json')