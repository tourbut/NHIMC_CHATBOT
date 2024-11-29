from typing import List
from app.models import *
from app.src.schemas import settings as settings_schema
from sqlmodel import Session, select, func,union_all

async def get_llm(*, session: Session) -> List[LLM]| None:
    statement = select(LLM)
    llm = await session.exec(statement)

    if not llm:
        return None
    else:
        return llm.all()
    
async def create_apikey(*, session: Session, apikey_in: settings_schema.Create_Apikey,user_id:uuid.UUID) -> UserAPIKey:
    db_obj = UserAPIKey.model_validate(apikey_in,update={"user_id":user_id})
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def get_apikey(*, session: Session,user_id:uuid.UUID) -> List[UserAPIKey]| None:
    statement = select(UserAPIKey).where(UserAPIKey.user_id == user_id)
    apikey = await session.exec(statement)
    if not apikey:
        return None
    else:
        return apikey.all()

async def update_apikey(*, session: Session, apikey_update: settings_schema.Get_Apikey) -> UserAPIKey:
    apikey = await session.get(UserAPIKey, apikey_update.id)
    
    if not apikey:
        return None
    else:
        update_dict = apikey_update.model_dump(exclude_unset=True)
        apikey.sqlmodel_update(update_dict)
        apikey.update_date = datetime.now()
        session.add(apikey)
        await session.commit()
        await session.refresh(apikey)

    return apikey


async def get_userllm(*, session: Session,user_id:uuid.UUID) -> List[UserLLM]| None:
    statement = select(UserLLM.id,
                       LLM.source,
                       LLM.name,
                       UserAPIKey.api_key,
                       UserLLM.active_yn).where(UserLLM.user_id == user_id,
                                                   UserLLM.llm_id == LLM.id,
                                                   UserLLM.api_id ==UserAPIKey.id)
    userllm = await session.exec(statement)
    if not userllm:
        return None
    else:
        return userllm.all()
    
async def create_userllm(*, session: Session, userllm_in: settings_schema.Create_UserLLM,user_id:uuid.UUID) -> UserLLM:
    db_obj = UserLLM.model_validate(userllm_in,update={"user_id":user_id})
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_userllm(*, session: Session, userllm_update: settings_schema.Update_UserLLM) -> UserLLM:
    userllm = await session.get(UserLLM, userllm_update.id)
    
    if not userllm:
        return None
    else:
        update_dict = userllm_update.model_dump(exclude_unset=True)
        userllm.sqlmodel_update(update_dict)
        userllm.update_date = datetime.now()
        session.add(userllm)
        await session.commit()
        await session.refresh(userllm)

    return userllm

async def get_userusage(*, session: Session,user_id:uuid.UUID):
    statement1 = select(User.name.label("name"),
                        LLM.source,
                       LLM.name.label("llm_name"),
                       func.date(UserUsage.usage_date).label("usage_date"),
                       func.sum(UserUsage.input_token).label("input_token"),
                       func.sum(UserUsage.output_token).label("output_token"),
                       func.sum((UserUsage.input_token / 1000000) * LLM.input_price + (UserUsage.output_token / 1000000) * LLM.output_price).label("cost") # 1M 토큰당 비용(1M = 1,000,000)
                       ).where(User.id == user_id,
                           UserLLM.user_id == User.id,
                                UserLLM.llm_id == LLM.id,
                                UserLLM.api_id ==UserAPIKey.id,
                                UserUsage.user_llm_id == UserLLM.id).group_by(User.name,LLM.source,LLM.name,
                                                                              func.date(UserUsage.usage_date)).order_by(func.date(UserUsage.usage_date).desc())
    statement2 = select(Dept.dept_nm.label("name"),
                        LLM.source,
                       LLM.name.label("llm_name"),
                       func.date(UserUsage.usage_date).label("usage_date"),
                       func.sum(UserUsage.input_token).label("input_token"),
                       func.sum(UserUsage.output_token).label("output_token"),
                       func.sum((UserUsage.input_token / 1000000) * LLM.input_price + (UserUsage.output_token / 1000000) * LLM.output_price).label("cost") # 1M 토큰당 비용(1M = 1,000,000)
                       ).where(User.id == user_id,
                               UserDept.user_id == User.id,
                               Dept.id == UserDept.dept_id,
                               DeptLLM.dept_id == Dept.id,
                                DeptLLM.llm_id == LLM.id,
                                DeptLLM.api_id ==DeptAPIKey.id,
                                UserUsage.dept_llm_id == DeptLLM.id).group_by(Dept.dept_nm,LLM.source,LLM.name,
                                                                              func.date(UserUsage.usage_date)).order_by(func.date(UserUsage.usage_date).desc())
    statement = union_all(statement1,statement2)
    userusage = await session.exec(statement)
    if not userusage:
        return None
    else:
        return userusage.all()
    

async def get_deptusage(*, session: Session,dept_id:uuid.UUID):
    statement = select(LLM.source,
                       LLM.name,
                       func.date(UserUsage.usage_date).label("usage_date"),
                       func.sum(UserUsage.input_token).label("input_token"),
                       func.sum(UserUsage.output_token).label("output_token"),
                       func.sum((UserUsage.input_token / 1000000) * LLM.input_price + (UserUsage.output_token / 1000000) * LLM.output_price).label("cost") # 1M 토큰당 비용(1M = 1,000,000)
                       ).where(DeptLLM.dept_id == dept_id,
                                DeptLLM.llm_id == LLM.id,
                                DeptLLM.api_id ==DeptAPIKey.id,
                                UserUsage.dept_llm_id == DeptLLM.id).group_by(LLM.source,
                                                                                LLM.name,
                                                                                func.date(UserUsage.usage_date)).order_by(func.date(UserUsage.usage_date).desc())
    
    userusage = await session.exec(statement)
    if not userusage:
        return None
    else:
        return userusage.all()
    
async def get_deptusage_all(*, session: Session):
    statement = select(LLM.source,
                       LLM.name,
                       func.date(UserUsage.usage_date).label("usage_date"),
                       func.sum(UserUsage.input_token).label("input_token"),
                       func.sum(UserUsage.output_token).label("output_token"),
                       func.sum((UserUsage.input_token / 1000000) * LLM.input_price + (UserUsage.output_token / 1000000) * LLM.output_price).label("cost") # 1M 토큰당 비용(1M = 1,000,000)
                       ).where(DeptLLM.llm_id == LLM.id,
                               DeptLLM.api_id ==DeptAPIKey.id,
                                UserUsage.dept_llm_id == DeptLLM.id).group_by(LLM.source,
                                                                                LLM.name,
                                                                                func.date(UserUsage.usage_date)).order_by(func.date(UserUsage.usage_date).desc())
    
    userusage = await session.exec(statement)
    if not userusage:
        return None
    else:
        return userusage.all()