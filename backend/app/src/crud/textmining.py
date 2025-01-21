from typing import List
import uuid

from sqlalchemy import literal_column
from app.models import *
from app.src.schemas import textmining as textmining_schema
from sqlmodel import select, union_all
from sqlmodel.ext.asyncio.session import AsyncSession

async def create_topic(session: AsyncSession, current_user: User, topic_in: textmining_schema.CreateTopic) -> TmTopic:
    
    try :
        topic = TmTopic.model_validate(topic_in,update={"user_id":current_user.id})
        
        session.add(topic)
        await session.commit()
        await session.refresh(topic)
        return topic
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def update_topic(session: AsyncSession, current_user: User, topic_in: textmining_schema.UpdateTopic) -> TmTopic:
    try:
        topic = await session.get(TmTopic, topic_in.id)

        if topic.user_id != current_user.id:
            raise Exception("해당 주제의 생성자만 수정할 수 있습니다.")
        
        if not topic:
            return None
        else:
            update_dict = topic_in.model_dump(exclude_unset=True)
            topic.sqlmodel_update(update_dict)
            topic.update_date = datetime.now()
            session.add(topic)
            await session.commit()
            await session.refresh(topic)

        return topic
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_topics(session: AsyncSession) -> List[TmTopic]:
    try:
        statement = select(TmTopic).where(TmTopic.delete_yn == False)
        topics = await session.exec(statement)
        return topics.all()
    except Exception as e:
        print(e)
        raise e

async def get_topic(session: AsyncSession, topic_id: uuid.UUID) -> TmTopic:
    try:
        statement = select(TmTopic).where(TmTopic.id == topic_id)
        topic = await session.exec(statement)
        return topic.first()
    except Exception as e:
        print(e)
        raise e

async def create_tmllm(session: AsyncSession, tmllm_in: textmining_schema.CreateTmLLM) -> TmLLM:
    try:
        tmllm = TmLLM.model_validate(tmllm_in)
        session.add(tmllm)
        await session.commit()
        await session.refresh(tmllm)
        return tmllm
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def update_tmllm(session: AsyncSession, tmllm_in: textmining_schema.CreateTmLLM) -> TmLLM:
    try:
        tmllm = await session.get(TmLLM, tmllm_in.id)
    
        if not tmllm:
            return None
        else:
            update_dict = tmllm_in.model_dump(exclude_unset=True)
            tmllm.sqlmodel_update(update_dict)
            tmllm.update_date = datetime.now()
            session.add(tmllm)
            await session.commit()
            await session.refresh(tmllm)

        return tmllm
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_llm(*, session: AsyncSession) -> List[textmining_schema.Get_Out_TmLLM]| None:
    try:
        statement = select(LLM.id.label("llm_id"),
                           LLM.source,
                           LLM.type,
                           LLM.name,
                           LLM.description,
                           LLM.url).where(LLM.active_yn == True,LLM.type == "llm")
        llm = await session.exec(statement)
        if not llm:
            return None
        else:
            return llm.all()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e    

async def get_tmllm(session: AsyncSession) -> List[textmining_schema.Get_Out_TmLLM]:
    try:
        statement = select(TmLLM.id,
                           LLM.id.label("llm_id"),
                           LLM.source,
                           LLM.type,
                           LLM.name,
                           LLM.description,
                           LLM.url,
                           TmLLM.active_yn).where(TmLLM.delete_yn == False,
                                          TmLLM.llm_id == LLM.id)
        tmllms = await session.exec(statement)
        return tmllms.all()
    except Exception as e:
        print(e)
        raise e 
    
async def create_tmchat(session: AsyncSession, current_user: User, tmchat_in: textmining_schema.CreateTmChat) -> TmChats:
    try:
        tmchat = TmChats.model_validate(tmchat_in,update={"user_id":current_user.id})
        session.add(tmchat)
        await session.commit()
        await session.refresh(tmchat)
        return tmchat
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_tmchats(session: AsyncSession, current_user: User) -> List[textmining_schema.Get_Out_TmChat]:
    try:
        statement = (
            select(TmChats.id,
                TmChats.title,
                TmChats.instruct_id, 
                TmInstruct.title.label("instruct_title"),
                TmInstruct.topic_id,
                TmTopic.topic_name)
            .join(TmInstruct, TmChats.instruct_id == TmInstruct.id, isouter=True)
            .join(TmTopic, TmInstruct.topic_id == TmTopic.id, isouter=True)
            .where(TmChats.delete_yn == False,
                TmChats.user_id == current_user.id)
        )
        
        tmchats = await session.exec(statement)
        return tmchats.all()
    except Exception as e:
        print(e)
        raise e
    
async def get_tmchat(session: AsyncSession, tmchat_id: uuid.UUID) -> textmining_schema.Get_Out_TmChat:
    try:
        statement = (
            select(TmChats.id,
                TmChats.title,
                TmChats.instruct_id, 
                TmInstruct.title.label("instruct_title"),
                TmInstruct.topic_id,
                TmTopic.topic_name)
            .join(TmInstruct, TmChats.instruct_id == TmInstruct.id, isouter=True)
            .join(TmTopic, TmInstruct.topic_id == TmTopic.id, isouter=True)
            .where(TmChats.id == tmchat_id)
        )
        
        tmchat = await session.exec(statement)
        return tmchat.first()
    except Exception as e:
        print(e)
        raise e

async def update_tmchat(session: AsyncSession, tmchat_in: textmining_schema.UpdateTmChat) -> TmChats:
    try:
        tmchat = await session.get(TmChats, tmchat_in.id)
    
        if not tmchat:
            return None
        else:
            update_dict = tmchat_in.model_dump(exclude_unset=True)
            tmchat.sqlmodel_update(update_dict)
            tmchat.update_date = datetime.now()
            session.add(tmchat)
            await session.commit()
            await session.refresh(tmchat)

        return tmchat
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    

async def create_tmoutputschema(session: AsyncSession, current_user: User, tmoutputschema_in: textmining_schema.CreateTmOutputSchema) -> textmining_schema.Create_Out_TmOutputSchema:
    try:
        tmoutputschema = TmOutputSchema.model_validate(tmoutputschema_in,update={"user_id":current_user.id})
        session.add(tmoutputschema)
        await session.flush()
        
        for attr in tmoutputschema_in.attr:
            tmoutputschemaattr = TmOutputSchemaAttr.model_validate(attr,update={"user_id":current_user.id,"schema_id":tmoutputschema.id})
            session.add(tmoutputschemaattr)
            await session.flush()
        
        await session.commit()
        await session.refresh(tmoutputschema)
        await session.refresh(tmoutputschemaattr)
        
        rtn = textmining_schema.Get_Out_TmOutputSchema.model_validate(tmoutputschema,update={'attr':[tmoutputschemaattr]})
        
        return rtn
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def update_tmoutputschema(session: AsyncSession, current_user: User, tmoutputschema_in: textmining_schema.UpdateTmOutputSchema) -> textmining_schema.UpdateTmOutputSchema:
    try:
        tmoutputschema = await session.get(TmOutputSchema, tmoutputschema_in.id)
    
        if not tmoutputschema:
            return None
        else:
            update_dict = tmoutputschema_in.model_dump(exclude_unset=True)
            tmoutputschema.sqlmodel_update(update_dict)
            tmoutputschema.update_date = datetime.now()
            session.add(tmoutputschema)
            await session.flush()
        
        rtn_attr =[]
        for attr in tmoutputschema_in.attr:
            if attr.id is None:
                attr_without_id = textmining_schema.CreateTmOutputSchemaAttr.model_validate(attr)
                tmoutputschemaattr = TmOutputSchemaAttr.model_validate(attr_without_id,update={"user_id":current_user.id,"schema_id":tmoutputschema.id})
                session.add(tmoutputschemaattr)
            else:
                tmoutputschemaattr = await session.get(TmOutputSchemaAttr, attr.id)
                update_dict = attr.model_dump(exclude_unset=True)
                tmoutputschemaattr.sqlmodel_update(update_dict)
                tmoutputschemaattr.update_date = datetime.now()
                session.add(tmoutputschemaattr)
                
            await session.flush()
            rtn_item = textmining_schema.UpdateTmOutputSchemaAttr .model_validate(tmoutputschemaattr)
            rtn_attr.append(rtn_item)
            
        await session.commit()
        await session.refresh(tmoutputschema)
        await session.refresh(tmoutputschemaattr)
        
        rtn = textmining_schema.UpdateTmOutputSchema.model_validate(tmoutputschema,update={'attr':[rtn_attr]})
        
        return rtn

    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def get_tmoutputschemas(session: AsyncSession) -> List[textmining_schema.Get_Out_TmOutputSchema]:
    try:
        statement1 = select(TmOutputSchema)
        tmoutputschemas = await session.exec(statement1)
        
        outputschemas = tmoutputschemas.all()
        
        rtn = []
        for schema in outputschemas:  
            statement2 = select(TmOutputSchemaAttr).where(TmOutputSchemaAttr.schema_id == schema.id)
            tmoutputschemaattrs = await session.exec(statement2)
            
            tmp = textmining_schema.Get_Out_TmOutputSchema.model_validate(schema,update={'attr':tmoutputschemaattrs.all()})
            
            rtn.append(tmp)
        
        return rtn
    except Exception as e:
        print(e)
        raise e

async def get_tmoutputschema_by_topic(session: AsyncSession, topic_id: uuid.UUID) -> List[textmining_schema.Get_Out_TmOutputSchema]:
    try:
        statement = select(TmOutputSchema).where(TmOutputSchema.topic_id == topic_id)
        tmoutputschemas = await session.exec(statement)
        return tmoutputschemas.all()
    except Exception as e:
        print(e)
        raise e
    
async def create_tmoutputschemaattr(session: AsyncSession, current_user: User, tmoutputschemaattrs_in: List[textmining_schema.CreateTmOutputSchemaAttr]) -> List[textmining_schema.CreateTmOutputSchemaAttr]:
    try:
        rtn = []
        for tmoutputschemaattr_in in tmoutputschemaattrs_in:
            tmoutputschemaattr = TmOutputSchemaAttr.model_validate(tmoutputschemaattr_in,update={"user_id":current_user.id})
            session.add(tmoutputschemaattr)
            await session.flush()
            rtn.append(tmoutputschemaattr)
        await session.commit()
        await session.refresh(tmoutputschemaattr)
        
        return rtn
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def get_tmoutputschemaattrs(session: AsyncSession, schema_id: uuid.UUID) -> List[textmining_schema.Get_Out_TmOutputSchemaAttr]:
    try:
        statement = select(TmOutputSchemaAttr).where(TmOutputSchemaAttr.schema_id == schema_id)
        tmoutputschemaattrs = await session.exec(statement)
        return tmoutputschemaattrs.all()
    except Exception as e:
        print(e)
        raise e
    
async def create_userprompt(session: AsyncSession, current_user: User, userprompt_in: textmining_schema.CreateUserPrompt) -> UserPrompt:
    try:
        userprompt = UserPrompt.model_validate(userprompt_in,update={"user_id":current_user.id})
        session.add(userprompt)
        await session.commit()
        await session.refresh(userprompt)
        return userprompt
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_userprompts(session: AsyncSession, current_user: User) -> List[textmining_schema.Get_Out_UserPrompt]:
    try:
        statement = select(UserPrompt).where(UserPrompt.user_id == current_user.id)
        userprompts = await session.exec(statement)
        return userprompts.all()
    except Exception as e:
        print(e)
        raise e
     
async def create_tminstruct(session: AsyncSession, current_user: User, tminstruct_in: textmining_schema.CreateTmInstruct) -> TmInstruct:
    try:
        i_prompt = textmining_schema.CreateUserPrompt(instruct_prompt=tminstruct_in.instruct_prompt, response_prompt=tminstruct_in.response_prompt)
        userprompt = UserPrompt.model_validate(i_prompt,update={"user_id":current_user.id})
        session.add(userprompt)
        await session.flush()
        
        tminstruct = TmInstruct.model_validate(tminstruct_in,update={"user_id":current_user.id,
                                                                     "userprompt_id":userprompt.id})
        session.add(tminstruct)
        await session.flush()
        await session.commit()
        await session.refresh(userprompt)
        await session.refresh(tminstruct)
        return tminstruct
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_tminstructs(session: AsyncSession, current_user: User, topic_id : uuid.UUID ) -> List[textmining_schema.Get_Out_TmInstruct]:
    try:
        statement = select(TmInstruct).where(TmInstruct.topic_id == topic_id,
                                             TmInstruct.user_id == current_user.id)
        tminstructs = await session.exec(statement)
        return tminstructs.all()
    except Exception as e:
        print(e)
        raise e
    
async def get_tminstruct(session: AsyncSession, tminstruct_id: uuid.UUID):
    try:
        statement = select( TmInstruct.id,
                            TmInstruct.title,
                            TmInstruct.memo,
                            TmInstruct.topic_id,
                            TmInstruct.mining_llm_id,
                            UserPrompt.instruct_prompt,
                            UserPrompt.response_prompt,
                            TmInstruct.output_schema_id,
                           ).where(TmInstruct.id == tminstruct_id,
                                   TmInstruct.userprompt_id == UserPrompt.id)
        tminstruct = await session.exec(statement)
        return tminstruct.first()
    except Exception as e:
        print(e)
        raise e

async def get_tminstruct_detail(session: AsyncSession, current_user: User, instruct_id: uuid.UUID) -> textmining_schema.Get_Out_TmInstructDetail:
    try:
        statement1 = select( TmInstruct.id,
                            TmInstruct.title,
                            TmInstruct.memo,
                            TmInstruct.topic_id,
                            TmTopic.topic_name,
                            TmInstruct.mining_llm_id,
                            LLM.name.label("mining_llm_name"),
                            LLM.url.label("mining_llm_url"),
                            UserPrompt.instruct_prompt,
                            UserPrompt.response_prompt,
                            TmInstruct.output_schema_id,
                            TmOutputSchema.schema_name.label("output_schema_name"),
                            TmOutputSchema.schema_desc.label("output_schema_desc"),
                           ).where(TmInstruct.id == instruct_id,
                                   TmInstruct.user_id == current_user.id,
                                   TmInstruct.topic_id == TmTopic.id,
                                   TmInstruct.mining_llm_id == TmLLM.id,
                                   TmLLM.llm_id == LLM.id,
                                   TmInstruct.userprompt_id == UserPrompt.id,
                                   TmInstruct.output_schema_id == TmOutputSchema.id)
        tminstruct = await session.exec(statement1)
        result1 = tminstruct.first()
        
        statement2 = select(TmOutputSchemaAttr).where(TmOutputSchemaAttr.schema_id == result1.output_schema_id)
        tmoutputschemaattrs = await session.exec(statement2)

        rtn = textmining_schema.Get_Out_TmInstructDetail.model_validate(result1,update={'output_schema_attr':tmoutputschemaattrs.all()})
        return rtn
    except Exception as e:
        print(e)
        raise e

async def update_tminstruct(session: AsyncSession, tminstruct_in: textmining_schema.UpdateTmInstruct):
    try:
        tminstruct = await session.get(TmInstruct, tminstruct_in.id)
    
        if not tminstruct:
            return None
        else:
            update_dict = tminstruct_in.model_dump(exclude_unset=True)
            tminstruct.sqlmodel_update(update_dict)
            tminstruct.update_date = datetime.now()
            session.add(tminstruct)
            await session.commit()
            await session.refresh(tminstruct)

        return tminstruct
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def create_tmmessages(session: AsyncSession, current_user: User, 
                            tmmessages_in: List[textmining_schema.CreateTmMessages],
                            usage:textmining_schema.Usage) -> List[TmMessages]:
    try:
        rtn = []
        for tmmessages_in in tmmessages_in:
            tmmessages = TmMessages.model_validate(tmmessages_in,update={"user_id":current_user.id})
            session.add(tmmessages)
            await session.flush()
            rtn.append(tmmessages)
            
        db_usage = UserUsage.model_validate(usage)
        session.add(db_usage)
        
        await session.flush()
        await session.commit()
        await session.refresh(tmmessages)
        await session.refresh(db_usage)
        
        return rtn
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def get_tmmessages(session: AsyncSession, current_user: User, tmchat_id: uuid.UUID) -> List[textmining_schema.Get_Out_TmMessages]:
    try:
        statement = select(TmMessages).where(TmMessages.chat_id == tmchat_id,
                                             TmMessages.user_id == current_user.id).order_by(TmMessages.create_date)
        tmmessages = await session.exec(statement)
        return tmmessages.all()
    except Exception as e:
        print(e)
        raise e
    
async def create_tmextract(session: AsyncSession, current_user: User, tmextract_in: textmining_schema.CreateTmExtract) -> TmExtract:
    try:
        tmextract = TmExtract.model_validate(tmextract_in,update={"user_id":current_user.id})
        session.add(tmextract)
        await session.commit()
        await session.refresh(tmextract)
        return tmextract
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_tmextracts(session: AsyncSession, current_user: User) -> List[textmining_schema.Get_Out_TmExtract]:
    try:
        statement = select(TmExtract).where(TmExtract.delete_yn == False,
                                          TmExtract.user_id == current_user.id)
        tmextracts = await session.exec(statement)
        return tmextracts.all()
    except Exception as e:
        print(e)
        raise e

async def get_tmextract(session: AsyncSession, tmextract_id: uuid.UUID) -> textmining_schema.Get_Out_TmExtract:
    try:
        statement = select(TmExtract).where(TmExtract.id == tmextract_id)
        tmextract = await session.exec(statement)
        return tmextract.first()
    except Exception as e:
        print(e)
        raise e

async def get_tmextracts_by_topic(session: AsyncSession, topic_id: uuid.UUID) -> List[textmining_schema.Get_Out_TmExtract]:
    try:
        statement = select(TmExtract).where(TmExtract.topic_id == topic_id)
        tmextracts = await session.exec(statement)
        return tmextracts.all()
    except Exception as e:
        print(e)
        raise e

async def create_tmexecset(session: AsyncSession, current_user: User, tmexecset_in: textmining_schema.CreateTmExecSet) -> TmExecSet:
    try:
        tmexecset = TmExecSet.model_validate(tmexecset_in,update={"user_id":current_user.id})
        session.add(tmexecset)
        await session.commit()
        await session.refresh(tmexecset)
        return tmexecset
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def get_tmexecsets(session: AsyncSession, current_user: User = None) -> List[textmining_schema.Get_Out_TmExecSet]:
    try:
        if current_user is None:
            statement = select(TmExecSet).where(TmExecSet.delete_yn == False)
        else :
            statement = select(TmExecSet).where(TmExecSet.delete_yn == False,
                                                TmExecSet.user_id == current_user.id)
        tmexecsets = await session.exec(statement)
        return tmexecsets.all()
    except Exception as e:
        print(e)
        raise e
    
async def get_tmexecset(session: AsyncSession, tmexecset_id: uuid.UUID) -> textmining_schema.Get_Out_TmExecSet:
    try:
        statement = select(TmExecSet).where(TmExecSet.id == tmexecset_id)
        tmexecset = await session.exec(statement)
        return tmexecset.first()
    except Exception as e:
        print(e)
        raise e
    
async def create_tmmaster(session: AsyncSession, tmmaster_in: textmining_schema.CreateTmMaster) -> TmMaster:
    try:
        tmmaster = TmMaster.model_validate(tmmaster_in)
        session.add(tmmaster)
        await session.commit()
        await session.refresh(tmmaster)
        return tmmaster
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
    
async def get_tmmasters(session: AsyncSession) -> List[textmining_schema.Get_Out_TmMaster]:
    try:
        statement = select(TmMaster).where(TmMaster.delete_yn == False)
        tmmasters = await session.exec(statement)
        return tmmasters.all()
    except Exception as e:
        print(e)
        raise e

async def get_tmmaster(session: AsyncSession, tmmaster_id: uuid.UUID) -> textmining_schema.Get_Out_TmMaster:
    try:
        statement = select(TmMaster).where(TmMaster.id == tmmaster_id)
        tmmaster = await session.exec(statement)
        return tmmaster.first()
    except Exception as e:
        print(e)
        raise e

async def create_tmdata(session: AsyncSession, tmdata_in: textmining_schema.CreateTmData) -> TmData:
    try:
        tmdata = TmData.model_validate(tmdata_in)
        session.add(tmdata)
        await session.commit()
        await session.refresh(tmdata)
        return tmdata
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_tmdata(session: AsyncSession, master_id: uuid.UUID) -> List[textmining_schema.Get_Out_TmData]:
    try:
        statement = select(TmData).where(TmData.master_id == master_id)
        tmdata = await session.exec(statement)
        return tmdata.all()
    except Exception as e:
        print(e)
        raise e
    
async def create_tmresult(session: AsyncSession, tmresult_in: textmining_schema.CreateTmResult) -> TmResult:
    try:
        tmresult = TmResult.model_validate(tmresult_in)
        session.add(tmresult)
        await session.commit()
        await session.refresh(tmresult)
        return tmresult
    except Exception as e:
        print(e)
        await session.rollback()
        raise e

async def get_tmresults(session: AsyncSession, master_id: uuid.UUID) -> List[textmining_schema.Get_Out_TmResult]:
    try:
        statement = select(TmResult).where(TmResult.master_id == master_id)
        tmresults = await session.exec(statement)
        return tmresults.all()
    except Exception as e:
        print(e)
        raise e

async def get_tmresult_by_data(session: AsyncSession, master_id: uuid.UUID, data_id: uuid.UUID) -> textmining_schema.Get_Out_TmResult:
    try:
        statement = select(TmResult).where(TmResult.master_id == master_id,
                                           TmResult.data_id == data_id)
        tmresult = await session.exec(statement)
        return tmresult.first()
    except Exception as e:
        print(e)
        raise e
    
