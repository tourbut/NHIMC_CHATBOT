import argparse
import pandas as pd
import asyncio

from datetime import datetime
import uuid

from app.src.crud.textmining import (
    get_mining_info, 
    create_tmdatalist,
    create_tmmaster,
    create_tmresultlist,
    update_tmmaster,
    get_tmmaster_by_exec_set_id,
    get_tmdata
)


from app.src.crud.textmining_load import (
    get_topics,
    update_topics,
    get_tmmasters,
    update_tmmasters,
    get_tmdata_all,
    update_tmdata,
    get_tmresults_all,
    update_tmresults,
    get_tminstructs_all,
    update_tminstructs,
    get_tmexecsets,
    update_tmexecsets,
)
from app.src.schemas import textmining as textmining_schema
from app.src.deps import async_engine,AsyncSession
from app.src.engine.textminig.miner import create_chain,chain_invoke
from app.src.utils.fromSybase import Sybase
from app.core.config import settings

settings.LLM_CACHE = True

BUFFER = 50 # 50개씩 묶어서 처리
async def to_dataframe(data):
    """Convert a list of Pydantic models to a pandas DataFrame."""
    
    df = pd.DataFrame([item.model_dump() for item in data])
    
    for col in df.columns:
        if isinstance(df[col].iloc[0], datetime):
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(df[col].iloc[0], bool):
            df[col] = df[col].apply(lambda x: 'Y' if x else 'N')
        elif isinstance(df[col].iloc[0], str):
            df[col] = df[col].fillna('')
        elif isinstance(df[col].iloc[0], uuid.UUID):
            # Convert UUID to string
            df[col] = df[col].astype(str)
        else:
            df[col] = df[col].fillna('')
            
    df.reset_index(drop=True)
    
    return df

async def run_multi(exec_set_id=None):
    async with AsyncSession(async_engine) as session:
        exec_set_list = await get_tmexecsets(session=session)
    
    try :
        for exec_set in exec_set_list:
            
            if exec_set_id:
                if exec_set.id != exec_set_id:
                    continue
                
            exec_set_id = exec_set.id
            print(f"Start Mining: {exec_set_id}")
            
            async with AsyncSession(async_engine) as session:
                instruct_detail = await get_mining_info(session=session,tmexecset_id=exec_set_id)
                
                existing_tmmasters = await get_tmmaster_by_exec_set_id(session=session,exec_set_id=exec_set_id)
                tmdatalist_keys = []
                for existing_tmmaster in existing_tmmasters:
                    LAST_MASTER_ID = existing_tmmaster.id if existing_tmmaster else None
                    if LAST_MASTER_ID:
                        tmdata = await get_tmdata(session=session,master_id=LAST_MASTER_ID)
                        for data in tmdata:
                            tmdatalist_keys.append(data.origin_key)
                        print(f"LAST_MASTER_ID: {LAST_MASTER_ID}, Data Count: {len(tmdatalist_keys)}")
                # tmdatalist_keys 중복제거
                tmdatalist_keys = list(set(tmdatalist_keys))
                
                tmmaster_in = textmining_schema.CreateTmMaster(exec_set_id=exec_set_id,status='W')
                tmmaster = await create_tmmaster(session=session,tmmaster_in=tmmaster_in)
                
            MASTER_ID = tmmaster.id
            
            # Data Extraction
            syb_db = Sybase()
            df_orgin = syb_db.execute_pandas(instruct_detail.sql)
            
            tmp_tmdatalist = []
            
            for i in range(0,len(df_orgin)):
                if df_orgin.iloc[i]['ORIGIN_KEY'] in tmdatalist_keys:
                    continue
                
                tmdata = textmining_schema.CreateTmData(master_id=MASTER_ID,
                                                        origin_key=df_orgin.iloc[i]['ORIGIN_KEY'],
                                                        origin_text=df_orgin.iloc[i]['ORIGIN_TEXT'],)
                tmp_tmdatalist.append(tmdata)
                
            print(f"Data Extraction: {len(tmp_tmdatalist)}")
            async with AsyncSession(async_engine) as session:
                tmdatalist = await create_tmdatalist(session=session,tmdatalist_in=tmp_tmdatalist) 
            
            # Text Mining
            chain = create_chain(instruct_detail=instruct_detail)
            tmp_tmresultlist = []
            result_cnt = 0
            for input_data in tmdatalist:
                
                #0.1초 대기
                await asyncio.sleep(0.1)
                
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
                result_cnt += len(tmp_tmresultlist)
                if len(tmp_tmresultlist) >= BUFFER:
                    async with AsyncSession(async_engine) as session:
                        await create_tmresultlist(session=session,tmresult_in=tmp_tmresultlist)
                        tmp_tmresultlist = []
                    
                    await asyncio.sleep(5) # 5초 대기
            
            # 결과 저장
            async with AsyncSession(async_engine) as session:
                if len(tmp_tmresultlist) > 0:
                    tmresultlist = await create_tmresultlist(session=session,tmresult_in=tmp_tmresultlist)
                comments = f"Data Extraction: {len(tmp_tmdatalist)}, Text Mining: {result_cnt}"
                print(comments)
                
                # Sybase 적재
                
                INSERT_BUFFER = 1000
                
                print("Sybase Insert Start")
                
                TMMASTER = await get_tmmasters(session=session)
                df_tmmaster = await to_dataframe(TMMASTER)
                print(f"TMMASTER: {len(df_tmmaster)}")
                
                print("TMMASTER Insert Start")
                #syb_db.truncate_table("TMMASTER")
                syb_db.bulk_insert(df_tmmaster, 'TMMASTER', chunksize=INSERT_BUFFER)
                await update_tmmasters(session=session)
                print("TMMASTER Insert End")
                
                TMTOPICS= await get_topics(session=session)
                df_tmtopics = await to_dataframe(TMTOPICS)
                print(f"TMTOPICS: {len(df_tmtopics)}")
                print("TMTOPICS Insert Start")
                #syb_db.truncate_table("TMTOPIC")
                syb_db.bulk_insert(df_tmtopics, 'TMTOPIC', chunksize=INSERT_BUFFER)
                await update_topics(session=session)
                print("TMTOPICS Insert End")
                
                TMEXECSET = await get_tmexecsets(session=session)
                df_tmexecset = await to_dataframe(TMEXECSET)
                print(f"TMEXECSET: {len(df_tmexecset)}")
                print("TMEXECSET Insert Start")
                #syb_db.truncate_table("TMEXECSET")
                syb_db.bulk_insert(df_tmexecset, 'TMEXECSET', chunksize=INSERT_BUFFER)
                await update_tmexecsets(session=session)
                print("TMEXECSET Insert End")
                
                TMINSTRUCT = await get_tminstructs_all(session=session)
                df_instruct = await to_dataframe(TMINSTRUCT)
                print(f"TMINSTRUCT: {len(df_instruct)}")
                print("TMINSTRUCT Insert Start")
                #syb_db.truncate_table("TMINSTRUCT")
                syb_db.bulk_insert(df_instruct, 'TMINSTRUCT', chunksize=INSERT_BUFFER)
                await update_tminstructs(session=session)
                print("TMINSTRUCT Insert End")
                
                TMDATA = await get_tmdata_all(session=session)
                df_tmdata = await to_dataframe(TMDATA)
                print(f"TMDATA: {len(df_tmdata)}")
                print("TMDATA Insert Start")
                #syb_db.truncate_table("TMDATA")
                syb_db.bulk_insert(df_tmdata, 'TMDATA', chunksize=INSERT_BUFFER)
                await update_tmdata(session=session)
                print("TMDATA Insert End")
                
                TMRESULT = await get_tmresults_all(session=session)
                df_tmresult = await to_dataframe(TMRESULT)
                print(f"TMRESULT: {len(df_tmresult)}")
                print("TMRESULT Insert Start")
                #syb_db.truncate_table("TMRESULT")
                syb_db.bulk_insert(df_tmresult, 'TMRESULT', chunksize=INSERT_BUFFER)
                await update_tmresults(session=session)
                print("TMRESULT Insert End")
                
                # Sybase 연결 종료
                syb_db.close()
                tmmaster_update_in = textmining_schema.UpdateTmMaster(id=MASTER_ID,exec_set_id=exec_set_id,status='C',end_date=datetime.now(),comments=comments)
                await update_tmmaster(session=session,tmmaster_in=tmmaster_update_in)
                
    except Exception as e:
        print(e)
        tmmaster_update_in = textmining_schema.UpdateTmMaster(id=MASTER_ID,exec_set_id=exec_set_id,status='E',end_date=datetime.now(),comments=str(e))
        await update_tmmaster(session=session,tmmaster_in=tmmaster_update_in)
        # Sybase 연결 종료
        syb_db.close()
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
        asyncio.run(run_multi(exec_set_id))
    else:
        print('Run Multi')
        asyncio.run(run_multi())
        
    print("End Mining...")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    