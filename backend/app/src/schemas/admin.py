from sqlmodel import SQLModel
from datetime import datetime
import uuid

class LLMCreate(SQLModel):
    source: str
    type: str
    name: str
    description: str
    input_price: float
    output_price: float
    is_active: bool = False

class Get_LLM(SQLModel):
    id: uuid.UUID 
    source: str
    type: str
    name: str
    description: str
    input_price: float
    output_price: float
    is_active: bool = False

class Get_Dept(SQLModel):
    id: uuid.UUID 
    dept_nm: str
    dept_cd: str

class Create_Apikey(SQLModel):
    dept_id:uuid.UUID
    api_name:str
    api_key:str 
    active_yn:bool 
    
class Get_Apikey(SQLModel):
    id:uuid.UUID 
    dept_id:uuid.UUID
    api_name:str
    api_key:str 
    active_yn:bool 

class Get_DeptLLM(SQLModel):
    id:uuid.UUID 
    dept_id:uuid.UUID
    llm_id:uuid.UUID
    api_id:uuid.UUID
    source:str
    name:str
    api_key:str
    active_yn:bool

class Create_DeptLLM(SQLModel):
    dept_id:uuid.UUID 
    llm_id:uuid.UUID 
    api_id:uuid.UUID
    active_yn:bool
    
class Update_DeptLLM(SQLModel):
    id:uuid.UUID 
    llm_id:uuid.UUID 
    api_id:uuid.UUID 
    active_yn:bool

class Delete_DeptLLM(SQLModel):
    id:uuid.UUID 
    
class Get_DeptUsage(SQLModel):
    dept_nm:str
    source:str
    name:str
    usage_date:datetime
    input_token:int
    output_token:int
    cost:float