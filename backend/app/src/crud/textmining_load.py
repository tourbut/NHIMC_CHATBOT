from typing import List
import uuid

from sqlalchemy import literal_column
from app.models import *
from app.src.schemas import textmining as textmining_schema
from sqlmodel import select, union_all, exists
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_tmmasters(session: AsyncSession) -> List[TmMaster]:
    try:
        statement = select(TmMaster).where(TmMaster.delete_yn == False, TmMaster.load_cplt_yn != 'Y')
        tmmasters = await session.exec(statement)
        return tmmasters.all()
    except Exception as e:
        print(e)
        raise e

async def update_tmmasters(session: AsyncSession) -> None:
    try:
        statement = select(TmMaster).where(TmMaster.delete_yn == False, TmMaster.load_cplt_yn != 'Y')
        tmmasters = await session.exec(statement)
        tmmasters = tmmasters.all()
        
        for tm in tmmasters:
            tm.load_cplt_yn = 'Y'
            session.add(tm)
        await session.commit()
    except Exception as e:
        print(e)
        raise e


async def get_tmdata_all(session: AsyncSession) -> List[TmData]:
    try:
        statement = select(TmData).where(TmData.delete_yn==False, TmData.load_cplt_yn != 'Y')
        tmdata = await session.exec(statement)
        return tmdata.all()
    except Exception as e:
        print(e)
        raise e

async def update_tmdata(session: AsyncSession):
    try:
        statement = select(TmData).where(TmData.delete_yn==False, TmData.load_cplt_yn != 'Y')
        tmdata = await session.exec(statement)
        tmdata = tmdata.all()
        
        for tm in tmdata:
            tm.load_cplt_yn = 'Y'
            session.add(tm)
        await session.commit()
    except Exception as e:
        print(e)
        raise e

async def get_topics(session: AsyncSession) -> List[TmTopic]:
    try:
        statement = select(TmTopic).where(TmTopic.delete_yn == False, TmTopic.load_cplt_yn != 'Y')
        topics = await session.exec(statement)
        return topics.all()
    except Exception as e:
        print(e)
        raise e

async def update_topics(session: AsyncSession) -> None:
    try:
        statement = select(TmTopic).where(TmTopic.delete_yn == False, TmTopic.load_cplt_yn != 'Y')
        topics = await session.exec(statement)
        topics = topics.all()
        
        for topic in topics:
            topic.load_cplt_yn = 'Y'
            session.add(topic)
        await session.commit()
    except Exception as e:
        print(e)
        raise e
    
async def get_tmresults_all(session: AsyncSession) -> List[TmResult]:
    try:
        statement = select(TmResult).where(TmResult.delete_yn==False, TmResult.load_cplt_yn != 'Y')
        tmresults = await session.exec(statement)
        return tmresults.all()
    except Exception as e:
        print(e)
        raise e

async def update_tmresults(session: AsyncSession) -> None:
    try:
        statement = select(TmResult).where(TmResult.delete_yn==False, TmResult.load_cplt_yn != 'Y')
        tmresults = await session.exec(statement)
        tmresults = tmresults.all()
        
        for tm in tmresults:
            tm.load_cplt_yn = 'Y'
            session.add(tm)
        await session.commit()
    except Exception as e:
        print(e)
        raise e
    
async def get_tminstructs_all(session: AsyncSession) -> List[TmInstruct]:
    try:
        statement = select(TmInstruct).where(TmInstruct.delete_yn == False, TmInstruct.load_cplt_yn != 'Y')
        tminstructs = await session.exec(statement)
        return tminstructs.all()
    except Exception as e:
        print(e)
        raise e

async def update_tminstructs(session: AsyncSession) -> None:
    try:
        statement = select(TmInstruct).where(TmInstruct.delete_yn == False, TmInstruct.load_cplt_yn != 'Y')
        tminstructs = await session.exec(statement)
        tminstructs = tminstructs.all()
        
        for tminstruct in tminstructs:
            tminstruct.load_cplt_yn = 'Y'
            session.add(tminstruct)
        await session.commit()
    except Exception as e:
        print(e)
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
    
async def update_tmexecsets(session: AsyncSession) -> None:
    try:
        statement = select(TmExecSet).where(TmExecSet.delete_yn == False)
        tmexecsets = await session.exec(statement)
        tmexecsets = tmexecsets.all()
        
        for tmexecset in tmexecsets:
            tmexecset.load_cplt_yn = 'Y'
            session.add(tmexecset)
        await session.commit()
    except Exception as e:
        print(e)
        raise e