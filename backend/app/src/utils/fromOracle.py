import oracledb
from app.core.config import settings

async def get_isis_user(empl_no: str):
    
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