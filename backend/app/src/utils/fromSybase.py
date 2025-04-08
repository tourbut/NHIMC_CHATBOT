import jaydebeapi
import pandas as pd
import os
#.env에서 환경변수를 가져오기 위한 라이브러리
from app.core.config import settings

class Sybase:
    SYBASE_SERVER_IP = settings.SYBASE_SERVER_IP
    SYBASE_SERVER_PORT = settings.SYBASE_SERVER_PORT
    SYBASE_SERVER_NAME = settings.SYBASE_SERVER_NAME
    SYBASE_USER = settings.SYBASE_USER
    SYBASE_PASSWORD = settings.SYBASE_PASSWORD

    url = "jdbc:sybase:Tds:" + SYBASE_SERVER_IP + ":" + SYBASE_SERVER_PORT + "/" + SYBASE_SERVER_NAME

    def __init__(self):
        print("connection url: ",self.url)
        try:
            # jconn4.jar 파일의 절대 경로를 사용하세요.
            jar_file = os.path.abspath("/usr/local/lib/jconn4.jar")
            print("Using jar file: ", jar_file)
            self.conn = jaydebeapi.connect(jclassname= "com.sybase.jdbc4.jdbc.SybDriver",
                            url=self.url,
                            driver_args=[self.SYBASE_USER, self.SYBASE_PASSWORD],
                            jars =jar_file)
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn = None

    def execute(self, query):
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return self.cursor.fetchall()
    def truncate_table(self, table_name):
        query = f"TRUNCATE TABLE {table_name}"
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            
        
        
    def execute_pandas(self, query):
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(cursor.fetchall(), columns=columns)

    def pandas_to_db(self, df, table_name):
        try:
            with self.conn.cursor() as cursor:
                for index, row in df.iterrows():
                    sql = "INSERT INTO " + table_name + " (" + ", ".join(row.keys()) + ") VALUES (" + ", ".join(["?" for _ in range(len(row.keys()))]) + ")"
                    cursor.execute(sql, tuple(row.values))
                
                self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            
    def bulk_insert(self, df, table_name, chunksize=100):
        try:
            # NaN/INF 값 처리
            df = df.replace([float('inf'), float('-inf')], None).fillna(value='')

            with self.conn.cursor() as cursor:
                columns = ','.join(df.columns)
                placeholders = ','.join(['?'] * len(df.columns))

                for i in range(0, len(df), chunksize):
                    chunk = df.iloc[i:i+chunksize]
                    tuples = [tuple(x) for x in chunk.to_numpy()]
                    query = f"""
                    INSERT INTO {table_name} ({columns}) 
                    VALUES ({placeholders})
                    """
                    cursor.executemany(query, tuples)
                    self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
    
    def close(self):
        self.conn.close()