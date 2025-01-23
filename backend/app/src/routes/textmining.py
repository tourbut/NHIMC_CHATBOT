import uuid

from typing import Any, Annotated, List
from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException, Depends

from app.src.deps import SessionDep_async,CurrentUser
from app.src.crud import textmining as textmining_crud
from app.src.schemas import textmining as textmining_schema
from langchain_community.callbacks import get_openai_callback
from fastapi.responses import StreamingResponse

from app.src.engine.llms.miner import create_chain,chain_astream,chain_invoke
from app.core.config import settings

router = APIRouter()


@router.post("/create_topic",response_model=textmining_schema.Create_Out_Topic)
async def create_topic(*, session: SessionDep_async, current_user: CurrentUser,topic_in: textmining_schema.CreateTopic):
    topic = await textmining_crud.create_topic(session=session,current_user=current_user,topic_in=topic_in)
    return topic

@router.put("/update_topic",response_model=textmining_schema.UpdateTopic)
async def update_topic(*, session: SessionDep_async, current_user: CurrentUser,topic_in: textmining_schema.UpdateTopic):
    topic = await textmining_crud.update_topic(session=session,current_user=current_user,topic_in=topic_in)
    return topic
    

@router.get("/get_topics",response_model=List[textmining_schema.Get_Out_Topic])
async def get_topics(*, session: SessionDep_async):
    topics = await textmining_crud.get_topics(session=session)
    return topics

@router.get("/get_topic/{topic_id}",response_model=textmining_schema.Get_Out_Topic)
async def get_topic(*, session: SessionDep_async, topic_id: uuid.UUID):
    topic = await textmining_crud.get_topic(session=session,topic_id=topic_id)
    return topic

@router.post("/create_tmllm",response_model=textmining_schema.CreateTmLLM)
async def create_tmllm(*, session: SessionDep_async, current_user: CurrentUser,tmllm_in: textmining_schema.CreateTmLLM):
    
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    tmllm = await textmining_crud.create_tmllm(session=session,tmllm_in=tmllm_in)
    return tmllm

@router.put("/update_tmllm",response_model=textmining_schema.Get_Out_TmLLM)
async def update_tmllm(*, session: SessionDep_async, current_user: CurrentUser,tmllm_in: textmining_schema.CreateTmLLM):
        
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    tmllm = await textmining_crud.update_tmllm(session=session,tmllm_in=tmllm_in)
    return tmllm

@router.get("/get_tmllm",response_model=List[textmining_schema.Get_Out_TmLLM])
async def get_tmllm(*, session: SessionDep_async):
    tmllms = await textmining_crud.get_tmllm(session=session)
    return tmllms

@router.get("/get_llm",response_model=List[textmining_schema.Get_Out_TmLLM])
async def get_llm(*, session: SessionDep_async):
    llms = await textmining_crud.get_llm(session=session)
    return llms

@router.post("/create_tmchat",response_model=textmining_schema.Create_Out_TmChat)
async def create_tmchat(*, session: SessionDep_async, current_user: CurrentUser,tmchat_in: textmining_schema.CreateTmChat):
    
    tmchat = await textmining_crud.create_tmchat(session=session,current_user=current_user,tmchat_in=tmchat_in)
    return tmchat

@router.get("/get_tmchats",response_model=List[textmining_schema.Get_Out_TmChat])
async def get_tmchats(*, session: SessionDep_async, current_user: CurrentUser):
    tmchats = await textmining_crud.get_tmchats(session=session,current_user=current_user)
    return tmchats

@router.get("/get_tmchat",response_model=textmining_schema.Get_Out_TmChat)
async def get_tmchat(*, session: SessionDep_async, current_user: CurrentUser, tmchat_id: uuid.UUID):
    tmchat = await textmining_crud.get_tmchat(session=session,tmchat_id=tmchat_id)
    return tmchat

@router.put("/update_tmchat",response_model=textmining_schema.UpdateTmChat)
async def update_tmchat(*, session: SessionDep_async, current_user: CurrentUser,tmchat_in: textmining_schema.UpdateTmChat):
       
    tmchat = await textmining_crud.update_tmchat(session=session,tmchat_in=tmchat_in)
    return tmchat

@router.post("/create_tmoutputschema",response_model=textmining_schema.Create_Out_TmOutputSchema)
async def create_tmoutputschema(*, session: SessionDep_async, current_user: CurrentUser,
                                tmoutputschema_in: textmining_schema.CreateTmOutputSchema):
    tmoutputschema = await textmining_crud.create_tmoutputschema(session=session,current_user=current_user,tmoutputschema_in=tmoutputschema_in)
    return tmoutputschema

@router.put("/update_tmoutputschema",response_model=textmining_schema.UpdateTmOutputSchema)
async def update_tmoutputschema(*, session: SessionDep_async, current_user: CurrentUser,
                                tmoutputschema_in: textmining_schema.UpdateTmOutputSchema):
    tmoutputschema = await textmining_crud.update_tmoutputschema(session=session,current_user=current_user,tmoutputschema_in=tmoutputschema_in)
    return tmoutputschema


@router.get("/get_tmoutputschemas",response_model=List[textmining_schema.Get_Out_TmOutputSchema])
async def get_tmoutputschemas(*, session: SessionDep_async, current_user: CurrentUser):
    tmoutputschemas = await textmining_crud.get_tmoutputschemas(session=session)
    return tmoutputschemas

@router.get("/get_tmoutputschemas/{topic_id}",response_model=List[textmining_schema.Get_Out_TmOutputSchema])
async def get_tmoutputschema_by_topic(*, session: SessionDep_async, current_user: CurrentUser, topic_id: uuid.UUID):
    tmoutputschemas = await textmining_crud.get_tmoutputschema_by_topic(session=session,topic_id=topic_id)
    return tmoutputschemas

@router.post("/create_tmoutputschemaattr",response_model=textmining_schema.CreateTmOutputSchemaAttr)
async def create_tmoutputschemaattr(*, session: SessionDep_async, current_user: CurrentUser,
                                    tmoutputschemaattr_in: textmining_schema.CreateTmOutputSchemaAttr):
    tmoutputschemaattr = await textmining_crud.create_tmoutputschemaattr(session=session,current_user=current_user
                                                                         ,tmoutputschemaattr_in=tmoutputschemaattr_in)
    return tmoutputschemaattr

@router.get("/get_tmoutputschemaattrs/{schema_id}",response_model=List[textmining_schema.Get_Out_TmOutputSchemaAttr])
async def get_tmoutputschemaattrs(*, session: SessionDep_async, current_user: CurrentUser, schema_id: uuid.UUID):
    tmoutputschemaattrs = await textmining_crud.get_tmoutputschemaattrs(session=session,schema_id=schema_id)
    return tmoutputschemaattrs

@router.post("/create_userprompt",response_model=textmining_schema.CreateUserPrompt)
async def create_userprompt(*, session: SessionDep_async, current_user: CurrentUser,
                            userprompt_in: textmining_schema.CreateUserPrompt):
    userprompt = await textmining_crud.create_userprompt(session=session,current_user=current_user
                                                         ,userprompt_in=userprompt_in)
    return userprompt

@router.get("/get_userprompts",response_model=List[textmining_schema.Get_Out_UserPrompt])
async def get_userprompts(*, session: SessionDep_async, current_user: CurrentUser):
    userprompts = await textmining_crud.get_userprompts(session=session,current_user=current_user)
    return userprompts

@router.post("/create_tminstruct",response_model=textmining_schema.Create_Out_TmInstruct)
async def create_tminstruct(*, session: SessionDep_async, current_user: CurrentUser,
                            tminstruct_in: textmining_schema.CreateTmInstruct):   
    tminstruct = await textmining_crud.create_tminstruct(session=session,current_user=current_user
                                                         ,tminstruct_in=tminstruct_in)

    tmchat_in = textmining_schema.UpdateTmChat(id=tminstruct_in.chat_id,instruct_id=tminstruct.id)
    tmchat = await textmining_crud.update_tmchat(session=session,tmchat_in=tmchat_in)

    return tmchat

@router.get("/get_tminstructs/{topic_id}",response_model=List[textmining_schema.Get_Out_TmInstruct])
async def get_tminstructs(*, session: SessionDep_async, current_user: CurrentUser, topic_id: uuid.UUID):
    tminstructs = await textmining_crud.get_tminstructs(session=session,current_user=current_user,topic_id=topic_id)
    return tminstructs

@router.get("/get_tminstruct/",response_model=textmining_schema.Get_Out_TmInstruct)
async def get_tminstruct(*, session: SessionDep_async, current_user: CurrentUser, tminstruct_id: uuid.UUID):
    tminstruct = await textmining_crud.get_tminstruct(session=session,tminstruct_id=tminstruct_id)
    return tminstruct

@router.put("/update_tminstruct",response_model=textmining_schema.UpdateTmInstruct)
async def update_tminstruct(*, session: SessionDep_async, current_user: CurrentUser,
                            tminstruct_in: textmining_schema.UpdateTmInstruct):
    tminstruct = await textmining_crud.update_tminstruct(session=session,tminstruct_in=tminstruct_in)
    return tminstruct

@router.post("/create_tmextract",response_model=textmining_schema.CreateTmExtract)
async def create_tmextract(*, session: SessionDep_async, current_user: CurrentUser,
                            tmextract_in: textmining_schema.CreateTmExtract):
    tmextract = await textmining_crud.create_tmextract(session=session,current_user=current_user
                                                       ,tmextract_in=tmextract_in)
    return tmextract

@router.get("/get_tmextracts/{topic_id}",response_model=List[textmining_schema.Get_Out_TmExtract])
async def get_tmextracts(*, session: SessionDep_async, current_user: CurrentUser, topic_id: uuid.UUID):
    tmextracts = await textmining_crud.get_tmextracts(session=session,current_user=current_user)
    return tmextracts

@router.get("/get_tmextract/{tmextract_id}",response_model=textmining_schema.Get_Out_TmExtract)
async def get_tmextract(*, session: SessionDep_async, current_user: CurrentUser, tmextract_id: uuid.UUID):
    tmextract = await textmining_crud.get_tmextract(session=session,tmextract_id=tmextract_id)
    return tmextract

@router.get("/get_tmextracts_by_topic/{topic_id}",response_model=List[textmining_schema.Get_Out_TmExtract])
async def get_tmextracts_by_topic(*, session: SessionDep_async, current_user: CurrentUser, topic_id: uuid.UUID):
    tmextracts = await textmining_crud.get_tmextracts_by_topic(session=session,topic_id=topic_id)
    return tmextracts

@router.post("/create_tmexecset",response_model=textmining_schema.CreateTmExecSet)
async def create_tmexecset(*, session: SessionDep_async, current_user: CurrentUser,
                           tmexecset_in: textmining_schema.CreateTmExecSet):
    tmexecset = await textmining_crud.create_tmexecset(session=session,current_user=current_user
                                                       ,tmexecset_in=tmexecset_in)
    return tmexecset

@router.get("/get_tmexecsets",response_model=List[textmining_schema.Get_Out_TmExecSet])
async def get_tmexecsets(*, session: SessionDep_async, current_user: CurrentUser):
    tmexecsets = await textmining_crud.get_tmexecsets(session=session,current_user=current_user)
    return tmexecsets

@router.post("/create_tmmaster",response_model=textmining_schema.CreateTmMaster)
async def create_tmmaster(*, session: SessionDep_async, current_user: CurrentUser,
                          tmmaster_in: textmining_schema.CreateTmMaster):
    tmmaster = await textmining_crud.create_tmmaster(session=session,current_user=current_user
                                                     ,tmmaster_in=tmmaster_in)
    return tmmaster

@router.get("/get_tmmasters",response_model=List[textmining_schema.Get_Out_TmMaster])
async def get_tmmasters(*, session: SessionDep_async, current_user: CurrentUser):
    tmmasters = await textmining_crud.get_tmmasters(session=session)
    return tmmasters

@router.get("/get_tmmaster/{tmmaster_id}",response_model=textmining_schema.Get_Out_TmMaster)
async def get_tmmaster(*, session: SessionDep_async, current_user: CurrentUser, tmmaster_id: uuid.UUID):
    tmmaster = await textmining_crud.get_tmmaster(session=session,tmmaster_id=tmmaster_id)
    return tmmaster

@router.post("/send_message",response_model=textmining_schema.OutMessage)
async def send_message(*, session: SessionDep_async, current_user: CurrentUser,tmchat_in: textmining_schema.SendMessage):
    
    '''Send a message to the chat
    chat_id와 instrction_id로 
    userprompt_id, mining_llm_id, output_schema_id로 각각의 값을 조회후 마이닝 모델 구성'''
    
    instruct_detail = await textmining_crud.get_tminstruct_detail(session=session,current_user=current_user,instruct_id=tmchat_in.instruct_id)
    
    chain = create_chain(instruct_detail=instruct_detail)
    
    user_message = textmining_schema.CreateTmMessages(user_id=current_user.id,
                                        chat_id=tmchat_in.chat_id,
                                        name=current_user.name,
                                        content=tmchat_in.input,
                                        is_user=True,
                                        create_date=datetime.now(),
                                        update_date=datetime.now())
    
    response,token,prompt = await chain_invoke(chain,tmchat_in.input)

    if response:
        out_message = "```\n"
        
        for content in response:
            out_message += str(content)+"\n"
        
        out_message += "\n```"
    else:
        out_message = "None"
    
    messages = []
    messages.append(user_message)
    
    bot_message = textmining_schema.CreateTmMessages(user_id=current_user.id,
                                                    chat_id=tmchat_in.chat_id,
                                                    name="미드미",
                                                    content=out_message,
                                                    full_prompt=prompt.text,
                                                    is_user=False,
                                                    create_date=datetime.now(),
                                                    update_date=datetime.now())
    messages.append(bot_message)
    
    usage = textmining_schema.Usage(tm_llm_id=instruct_detail.mining_llm_id,
                                  input_token=token[0],
                                  output_token=token[1])
    
    await textmining_crud.create_tmmessages(session=session,current_user=current_user,tmmessages_in=messages,usage=usage)
            
    rtn = textmining_schema.OutMessage(content=out_message,
                                       full_prompt=prompt.text,
                                        input_token=token[0],
                                        output_token=token[1],
                                        is_done=True)
    return rtn
    

@router.get("/get_messages",response_model=List[textmining_schema.Get_Out_TmMessages])
async def get_messages(*, session: SessionDep_async, current_user: CurrentUser, chat_id: uuid.UUID):
    messages = await textmining_crud.get_tmmessages(session=session,current_user=current_user,tmchat_id=chat_id)
    return messages