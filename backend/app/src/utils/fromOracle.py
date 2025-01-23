import oracledb
from app.core.config import settings

async def get_isis_user(empl_no: str):
    
    try :
        async with oracledb.connect_async(user=settings.ISIS_DB_USER,
                                            password=settings.ISIS_DB_PASSWORD,
                                            dsn=settings.ISIS_DB_DSN) as conn:
        
            async with conn.cursor() as cursor:
                query = """-- 챗봇사용자 조회
                            SELECT 
                                USER_ID AS EMPL_NO
                                ,PW AS PASSWORD
                                ,USER_NM AS NAME
                                ,DEPT_CD AS DEPT_CD
                            FROM NHIMC_DBA.NV_CHATUSER
                            WHERE USER_ID=:EMPL_NO"""
                await cursor.execute(query, empl_no=empl_no)
                
                result = await cursor.fetchone()
                
                return result
    except Exception as e:
        print(e)
        return None
        
async def get_isis_dept():
    
    async with oracledb.connect_async(user=settings.ISIS_DB_USER,
                                        password=settings.ISIS_DB_PASSWORD,
                                        dsn=settings.ISIS_DB_DSN) as conn:
    
        async with conn.cursor() as cursor:
            query = """-- 부서 조회
                        SELECT 
                            A1.DEPT_CD AS DEPT_CD
                            ,A1.DEPT_NM AS DEPT_NM
                        FROM AZCMMDEPT A1
                        WHERE  1=1
                        AND TO_CHAR (SYSDATE, 'YYYYMMDD') BETWEEN A1.DEPT_STR_DY AND A1.DEPT_END_DY
                        AND DEPT_CD <>'%'
                        ORDER BY A1.DEPT_CD, A1.DEPT_NM"""
            await cursor.execute(query)
            
            result = await cursor.fetchall()
            
            return result