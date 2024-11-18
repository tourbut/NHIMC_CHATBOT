from numpy import source
from app.models import *
from sqlmodel import SQLModel
from datetime import datetime
import uuid

class Get_LLM(SQLModel):
    id:uuid.UUID 
    source: str
    type: str
    name: str
    description: str
    input_price: float
    output_price: float

class Create_Apikey(SQLModel):
    api_name:str
    api_key:str 
    active_yn:bool 
    
class Get_Apikey(SQLModel):
    id:uuid.UUID 
    api_name:str
    api_key:str 
    active_yn:bool 
    
class Get_UserLLM(SQLModel):
    id:uuid.UUID 
    source:str
    name:str
    api_key:str
    active_yn:bool

class Create_UserLLM(SQLModel):
    llm_id:uuid.UUID 
    api_id:uuid.UUID 
    active_yn:bool

class Update_UserLLM(SQLModel):
    id:uuid.UUID 
    llm_id:uuid.UUID 
    api_id:uuid.UUID 
    active_yn:bool

class Delete_UserLLM(SQLModel):
    id:uuid.UUID 

class Get_UserUsage(SQLModel):
    source:str
    name:str
    usage_date:datetime
    input_token:int
    output_token:int
    cost:float