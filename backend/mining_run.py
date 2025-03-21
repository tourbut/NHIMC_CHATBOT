import argparse
import pandas as pd
import asyncio

from datetime import datetime

from app.src.crud.textmining import get_mining_info, create_tmdatalist,create_tmmaster,create_tmresultlist,update_tmmaster,get_tmexecsets
from app.src.schemas import textmining as textmining_schema
from app.src.deps import async_engine,AsyncSession
from app.src.engine.textminig.miner import create_chain,chain_invoke
from app.src.utils.fromSybase import Sybase
from app.core.config import settings

settings.LLM_CACHE = True

BUFFER = 50 # 50개씩 묶어서 처리

async def run_single(exec_set_id):
    
    async with AsyncSession(async_engine) as session:        
        instruct_detail = await get_mining_info(session=session,tmexecset_id=exec_set_id)
        tmmaster_in = textmining_schema.CreateTmMaster(exec_set_id=exec_set_id,status='W')
        tmmaster = await create_tmmaster(session=session,tmmaster_in=tmmaster_in)
    
    MASTER_ID = tmmaster.id
    
    # Data Extraction
    db = Sybase()
    df_orgin = db.execute_pandas(instruct_detail.sql)
    
    tmp_tmdatalist = []
    
    for i in range(0,len(df_orgin)):
        tmdata = textmining_schema.CreateTmData(master_id=MASTER_ID,
                                                origin_key=df_orgin.iloc[i]['ORIGIN_KEY'],
                                                origin_text=df_orgin.iloc[i]['ORIGIN_TEXT'],)
        tmp_tmdatalist.append(tmdata)
        
    async with AsyncSession(async_engine) as session:
        tmdatalist = await create_tmdatalist(session=session,tmdatalist_in=tmp_tmdatalist) 
    
    # Text Mining
    chain = create_chain(instruct_detail=instruct_detail)
    tmp_tmresultlist = []
    for input_data in tmdatalist:
        responses,_,_ = await chain_invoke(chain,input_data.origin_text)
        seq = 0
        for response in responses:
            item_seq=0
            for key,value in response.model_dump().items():
                tmresult = textmining_schema.CreateTmResult(data_id=input_data.id,
                                                           master_id=MASTER_ID,
                                                           seq=seq,
                                                           item_seq=item_seq,
                                                           item_nm=key,
                                                           item_value=value)
                tmp_tmresultlist.append(tmresult)
                item_seq+=1
            seq+=1
    
    # 결과 저장
    async with AsyncSession(async_engine) as session:
        tmresultlist = await create_tmresultlist(session=session,tmresult_in=tmp_tmresultlist)
        tmmaster_update_in = textmining_schema.UpdateTmMaster(id=MASTER_ID,exec_set_id=exec_set_id,status='C',end_date=datetime.now())
        await update_tmmaster(session=session,tmmaster_in=tmmaster_update_in)

async def run_multi():
    async with AsyncSession(async_engine) as session:
        exec_set_list = await get_tmexecsets(session=session)
    
    try :
        for exec_set in exec_set_list:
            exec_set_id = exec_set.id
            print(f"Start Mining: {exec_set_id}")
            
            async with AsyncSession(async_engine) as session:
                    instruct_detail = await get_mining_info(session=session,tmexecset_id=exec_set_id)
                    tmmaster_in = textmining_schema.CreateTmMaster(exec_set_id=exec_set_id,status='W')
                    tmmaster = await create_tmmaster(session=session,tmmaster_in=tmmaster_in)
            
            MASTER_ID = tmmaster.id
            
            # Data Extraction
            db = Sybase()
            df_orgin = db.execute_pandas(instruct_detail.sql)
            
            tmp_tmdatalist = []
            
            for i in range(0,len(df_orgin)):
                tmdata = textmining_schema.CreateTmData(master_id=MASTER_ID,
                                                        origin_key=df_orgin.iloc[i]['ORIGIN_KEY'],
                                                        origin_text=df_orgin.iloc[i]['ORIGIN_TEXT'],)
                tmp_tmdatalist.append(tmdata)
                
            async with AsyncSession(async_engine) as session:
                tmdatalist = await create_tmdatalist(session=session,tmdatalist_in=tmp_tmdatalist) 
            
            # Text Mining
            chain = create_chain(instruct_detail=instruct_detail)
            tmp_tmresultlist = []
            for input_data in tmdatalist:
                responses,_,_ = await chain_invoke(chain,input_data.origin_text)
                seq = 0
                for response in responses:
                    item_seq=0
                    for key,value in response.model_dump().items():
                        tmresult = textmining_schema.CreateTmResult(data_id=input_data.id,
                                                                master_id=MASTER_ID,
                                                                seq=seq,
                                                                item_seq=item_seq,
                                                                item_nm=key,
                                                                item_value=value)
                        tmp_tmresultlist.append(tmresult)
                        item_seq+=1
                    seq+=1
                
                if len(tmp_tmresultlist) >= BUFFER:
                    async with AsyncSession(async_engine) as session:
                        await create_tmresultlist(session=session,tmresult_in=tmp_tmresultlist)
                        tmp_tmresultlist = []
            
            # 결과 저장
            async with AsyncSession(async_engine) as session:
                if len(tmp_tmresultlist) > 0:
                    tmresultlist = await create_tmresultlist(session=session,tmresult_in=tmp_tmresultlist)
                tmmaster_update_in = textmining_schema.UpdateTmMaster(id=MASTER_ID,exec_set_id=exec_set_id,status='C',end_date=datetime.now())
                await update_tmmaster(session=session,tmmaster_in=tmmaster_update_in)
                
    except Exception as e:
        print(e)
        tmmaster_update_in = textmining_schema.UpdateTmMaster(id=MASTER_ID,exec_set_id=exec_set_id,status='E',end_date=datetime.now(),comments=str(e))
        await update_tmmaster(session=session,tmmaster_in=tmmaster_update_in)
        raise e
    
if __name__ == "__main__":
    print("Start Mining...")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    arg_parser = argparse.ArgumentParser(description="Ilsan Hospital TextMining Engine")
    arg_parser.add_argument("--exec_set_id", help="실행ID(uuid)",required=False)
    args = arg_parser.parse_args()

    if args.exec_set_id:
        print('Run Single')
        exec_set_id = args.exec_set_id
        asyncio.run(run_single(exec_set_id))
    else:
        print('Run Multi')
        asyncio.run(run_multi())
        
    print("End Mining...")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    