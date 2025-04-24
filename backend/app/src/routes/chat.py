import uuid
import json
from typing import Any, Generator,List

from fastapi import APIRouter, HTTPException, Request

from app.src.deps import CheckpointerDep, SessionDep_async,CurrentUser,engine, redis_client
from app.src.crud import chat as chat_crud
from app.src.schemas import chat as chat_schema
from app.src.crud import pgvector as pgvector_crud
from fastapi.responses import StreamingResponse
from app.core.config import settings
from app.src.engine.llms.chain import (
    thought_chatbot_chain,
    chatbot_chain,
    create_llm,
)
from app.src.engine.llms.memory import pg_vetorstore_with_memory,pg_ParentDocumentRetriever,clear_memory
from datetime import datetime
from langchain_redis import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)

from app.src.engine.agent.node_graph import (
    acreate_agent_rag,
    create_agent_rag,
    acreate_agent_rag_v2
)
from app.src.engine.agent.tools import get_retriever_tool
from app.src.engine.llms.callbacks import get_openai_callback
from app.src.utils.graph import draw_graph

router = APIRouter()

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

@router.get("/get_messages",response_model=List[chat_schema.ReponseMessages])
async def get_messages(*, session: SessionDep_async, current_user: CurrentUser, id:uuid.UUID):
    
    async def create_messages_from_db(history,session,current_user, id):
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
        return messages
    
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
            messages = await create_messages_from_db(history,session,current_user, id)
            
    except Exception as e:
        print(e)
        messages = await create_messages_from_db(history,session,current_user, id)
    
    return messages

@router.put("/clear_messages")
async def clear_messages(*, session: SessionDep_async, current_user: CurrentUser, in_id:chat_schema.ClearMessages):
    try :
        history = get_redis_history(in_id.id.hex,redis_client=await redis_client())
        await history.aclear()
        
        await chat_crud.delete_messages(session=session,current_user=current_user,id=in_id.id)
        
        clear_memory(connection=engine,
                     collection_name=in_id.id.hex,
                     api_key=settings.GLOBAL_EMBEDDING_API,
                     source=settings.GLOBAL_EMBEDDING_SOURCE,
                     model=settings.GLOBAL_EMBEDDING_MODEL,
                     base_url=settings.GLOBAL_EMBEDDING_URL)
        
        
        return {"message":"Messages cleared successfully"}
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=404,detail="Messages not found")

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
    try : 
        history = get_redis_history(chat_in.id.hex,redis_client=await redis_client())
        await history.aclear()
        
        await chat_crud.delete_messages(session=session,current_user=current_user,id=chat_in.id)
        
        clear_memory(connection=engine,
                     collection_name=chat_in.id.hex,
                     api_key=settings.GLOBAL_EMBEDDING_API,
                     source=settings.GLOBAL_EMBEDDING_SOURCE,
                     model=settings.GLOBAL_EMBEDDING_MODEL,
                     base_url=settings.GLOBAL_EMBEDDING_URL)
        
        chat_in.delete_yn = True
    
        chat = await chat_crud.update_chat(session=session,chat=chat_in)
        return {"message":"Chat deleted successfully"}
    except Exception as e:
        print(e)
        return HTTPException(status_code=404,detail="Chat not found")

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
    
    redis = await redis_client()
    # Get or create a RedisChatMessageHistory instance
    history = get_redis_history(chat_in.chat_id.hex if chat_in.chat_id is not None else chat_in.chatbot_id.hex,redis)
    # Get a postgres vectorstore with memory
    memory = pg_vetorstore_with_memory(connection=engine,
                                       collection_name=chat_in.chat_id.hex if chat_in.chat_id is not None else chat_in.chatbot_id.hex,
                                       api_key=settings.GLOBAL_EMBEDDING_API,
                                       source=settings.GLOBAL_EMBEDDING_SOURCE,
                                       model=settings.GLOBAL_EMBEDDING_MODEL,
                                       base_url=settings.GLOBAL_EMBEDDING_URL,
                                       search_kwargs={"k": 3},
                                       chat_memory=history)
    
    if chabot_data.collection_id is not None:
        collection = await pgvector_crud.get_collection(session=session,collection_id=chabot_data.collection_id)
        
        retriever_llm = create_llm(source='ollama',
                         model=settings.GLOBAL_LLM,
                         api_key=settings.GLOBAL_LLM_API,
                         base_url=settings.GLOBAL_LLM_URL,
                         temperature=0.1,
                         )
        retriever = pg_ParentDocumentRetriever(connection=engine,
                                    collection_name=collection.name,
                                    api_key=embedding.api_key,
                                    source=embedding.source,
                                    model=embedding.name,
                                    base_url=embedding.url,
                                    async_mode=False,
                                    splitter_options=collection.cmetadata,
                                    search_kwargs={"k": 500, "lambda": 0.3},
                                    )
    
    document_meta = "관련 문서 없음" if chabot_data.file_title is None else {'title':chabot_data.file_title,
                                                              'description':chabot_data.file_description,}
    
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
    
    if chabot_data.thought_prompt:
        chain = thought_chatbot_chain(instruct_prompt=chabot_data.instruct_prompt,
                                        thought_prompt=chabot_data.thought_prompt,
                                        temperature=chabot_data.temperature,
                                        api_key=llm.api_key,
                                        source=llm.source,
                                        model=llm.name,
                                        base_url=llm.url,
                                        memory=memory,
                                        document_meta=document_meta,
                                        retriever=retriever,
                                        retriever_score=json.loads(chabot_data.search_kwargs)['retriever_score'] if chabot_data.search_kwargs else None,
                                        allow_doc_num=json.loads(chabot_data.search_kwargs)['k'] if chabot_data.search_kwargs else 0)
    else:
    
        chain = chatbot_chain(instruct_prompt=chabot_data.instruct_prompt,
                                temperature=chabot_data.temperature,
                                api_key=llm.api_key,
                                source=llm.source,
                                model=llm.name,
                                base_url=llm.url,
                                memory=memory,
                                document_meta=document_meta,
                                retriever=retriever,
                                retriever_score=json.loads(chabot_data.search_kwargs)['retriever_score'] if chabot_data.search_kwargs else None,
                                allow_doc_num=json.loads(chabot_data.search_kwargs)['k'] if chabot_data.search_kwargs else 0)
        
    async def chain_astream(chain,input):
        chunks=[]
        thought=None
        document=None
        params = None
        input_token=0
        output_token=0
        
        
        callback_handler = get_openai_callback()
        
        with callback_handler as cb:
            streaming_msg =""
            async for chunk in chain.astream({'input':input}):
            
                params = chunk.get('params', params)
                thought = params.get('thought', thought) if params else thought
                document = params.get('document', document) if params else document
                
                answer = chunk.get('answer', None)
                
                if document is not None and streaming_msg == "":
                    yield chat_schema.OutMessage(content=document if type(document) is str else "",
                                                thought=None,
                                                tools = {'retriever': ''},
                                                input_token=None,
                                                output_token=None,
                                                create_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                is_done=False).model_dump_json() + '\n'
                if answer is None:
                    continue
                
                chunks.append(answer)
                
                streaming_msg+=answer.content
                yield chat_schema.OutMessage(content=streaming_msg,
                                            thought=None,
                                            tools = {'retriever': ''},
                                            input_token=None,
                                            output_token=None,
                                            create_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            is_done=False).model_dump_json() + '\n'

            input_token = cb.prompt_tokens
            output_token = cb.completion_tokens
            
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
                        thought=thought if thought else None,
                        tools=json.dumps({'retriever': document if document else '' }, ensure_ascii=False),
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




@router.post("/send_message_by_agent",response_model=chat_schema.OutMessage)
async def send_message_by_agent(*,checkpointer: CheckpointerDep,session: SessionDep_async, current_user: CurrentUser,chat_in: chat_schema.SendMessageToChatbot):
    
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
    if chabot_data.collection_id is not None:
        collection = await pgvector_crud.get_collection(session=session,collection_id=chabot_data.collection_id)
        
        retriever = pg_ParentDocumentRetriever(connection=engine,
                                    collection_name=collection.name,
                                    api_key=embedding.api_key,
                                    source=embedding.source,
                                    model=embedding.name,
                                    base_url=embedding.url,
                                    async_mode=False,
                                    splitter_options=collection.cmetadata,
                                    search_kwargs={"k": 500, "lambda": 0.3},
                                    )

    agent_llm = create_llm(source=llm.source,
                    model=llm.name,
                    api_key=llm.api_key,
                    base_url=llm.url,
                    temperature=0.5,
                    )
    
    json_llm = create_llm(source=llm.source,
                    model=llm.name,
                    api_key=llm.api_key,
                    base_url=llm.url,
                    format="json",
                    temperature=0,
                    )
    redis = await redis_client()
    # Get or create a RedisChatMessageHistory instance
    history = get_redis_history(chat_in.chat_id.hex if chat_in.chat_id is not None else chat_in.chatbot_id.hex,redis)
    
    # Get a postgres vectorstore with memory
    memory = pg_vetorstore_with_memory(connection=engine,
                                       collection_name=chat_in.chat_id.hex if chat_in.chat_id is not None else chat_in.chatbot_id.hex,
                                       api_key=settings.GLOBAL_EMBEDDING_API,
                                       source=settings.GLOBAL_EMBEDDING_SOURCE,
                                       model=settings.GLOBAL_EMBEDDING_MODEL,
                                       base_url=settings.GLOBAL_EMBEDDING_URL,
                                       search_kwargs={"k": 3},
                                       chat_memory=history)
    
    # 메모리 저장소 생성
    document_meta = "관련 문서 없음" if chabot_data.file_title is None else {'title':chabot_data.file_title,
                                                              'description':chabot_data.file_description,}
    document_options = {"document_prompt": "{page_content}",
                        "document_separator": "<---split--->",
                        "document_metadata": document_meta
                        }
    
    retriever_tool = get_retriever_tool(
        retriever=retriever,
        name="retriever",
        description=f"Search and return information about {document_meta}.",
        document_prompt=document_options.get("document_prompt"),
        document_separator=document_options.get("document_separator")
    )
    
    tools = [retriever_tool] 
    
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    graph = acreate_agent_rag_v2(llm=agent_llm,json_llm=json_llm,
                             tools=tools,checkpointer=checkpointer,
                             document_options=document_options)
    
    from langchain_core.runnables import RunnableConfig

    config = RunnableConfig(
        recursion_limit=30,  # 최대 10개의 노드까지 방문. 그 이상은 RecursionError 발생
        configurable={"thread_id": f"user_{chat_in.chat_id}"},  # 스레드 ID 설정
        stream_mode = "values"
    )
    
    human_message= HumanMessage(content=chat_in.input,
                                additional_kwargs={
                                    "user_id":str(current_user.id),
                                    "name":current_user.name,
                                    "create_date":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })

    bot_message = chat_schema.CreateMessage(user_id=current_user.id,
                                             chat_id = chat_in.chat_id,
                        chatbot_id=chat_in.chatbot_id,
                        name="바르미",
                        content="",
                        thought=None,
                        tools= json.dumps({'retriever': '' }, ensure_ascii=False),
                        is_user=False,
                        create_date=datetime.now(),
                        update_date=datetime.now())
    input_token = 0
    output_token = 0
    out_message = chat_schema.OutMessage(content=bot_message.content,
                                     thought=bot_message.thought,
                                     tools = json.loads(bot_message.tools) if bot_message.tools else {'retriever': ''},
                                     input_token=0,
                                     output_token=0,
                                     create_date=bot_message.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                                     is_done=True)
    async def chain_astream(graph,input,config):
        async for event in graph.astream({"input": input}, config=config):
            if event.get('agent'):
                for value in event.values():
                    if value.get('output'):
                        out_message.content = value["output"]
                        input_token = value["messages"][-1].usage_metadata["input_tokens"]
                        output_token = value["messages"][-1].usage_metadata["output_tokens"]
                        out_message.input_token = input_token
                        out_message.output_token = output_token
                    if value.get('tool_calls'):
                        tool_calls = value.get('tool_calls')
                        if tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0:
                            args = tool_calls[0].get('args', {})
                            query = args.get('query')
                            if query is not None:
                                out_message.content = f"문서 검색중...\n 검색어: {query}"
                            else:
                                out_message.content = ""  # 또는 적절한 기본값  
            if event.get('retrieve'):
                for value in event.values():
                    if value.get('messages'):
                        content = value.get('messages')[-1].content.replace('\\n','\n')
                        out_message.content = f"검색결과\n ```\n{content}```"
            if event.get('rerank'):
                for value in event.values():
                    out_message.content = f"문서 판별중\n {value.get('eval_doc')}"
            if event.get('rewrite'):
                for value in event.values():
                    print(value)
            if event.get('generate'):
                for value in event.values():
                    out_message.content = value.get('output')
                    input_token = value.get('messages')[-1].usage_metadata["input_tokens"]
                    output_token = value.get('messages')[-1].usage_metadata["output_tokens"]
                    out_message.tools = {'retriever': "\n\n".join(value.get('context'))}
                    out_message.input_token = input_token
                    out_message.output_token = output_token
                    
            yield out_message.model_dump_json() + '\n'
        
    
    return StreamingResponse(chain_astream(graph,chat_in.input,config),media_type='application/json')
        

            
