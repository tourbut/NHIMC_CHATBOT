import uuid
from sqlmodel import SQLModel
from datetime import datetime

class SendMessage(SQLModel):
    chat_id: uuid.UUID 
    user_llm_id: uuid.UUID
    document_id: uuid.UUID | None = None
    input: str
    
class Usage(SQLModel):
    user_llm_id: uuid.UUID  
    input_token:int 
    output_token:int

class OutMessage(SQLModel):
    content: str
    thought : str = None
    tools : dict = None
    input_token: int | None = None
    output_token: int | None = None
    create_date: datetime = datetime.now()
    is_done: bool = False
    
class GetUserLLM(SQLModel):
    id: uuid.UUID 
    source: str
    name: str
    api_key: str

class GetDeptLLM(SQLModel):
    id: uuid.UUID 
    source: str
    name: str
    api_key: str

class CreateChat(SQLModel):
    title: str
    user_llm_id: uuid.UUID
    userdocument_id: uuid.UUID

class ResponseChat(SQLModel):
    id: uuid.UUID
    title: str
    user_llm_id: uuid.UUID
    user_file_id: uuid.UUID
    
class GetChat(SQLModel):
    category: str = "chat"
    id: uuid.UUID
    title: str
    user_llm_id: uuid.UUID
    user_file_id: uuid.UUID

class GetMessages(SQLModel):
    chat_id: str

class ReponseMessages(SQLModel):
    chat_id: uuid.UUID
    name:str
    content: str|None
    thought : str|None = None
    tools : str|None = None
    is_user: bool
    create_date: datetime

class CreateMessage(SQLModel):
    chat_id: uuid.UUID 
    user_id: uuid.UUID 
    name: str 
    content: str
    thought : str = None
    tools : str = None
    is_user: bool
    create_date: datetime= datetime.now()
    
    
class Chat(SQLModel):
    category: str
    language: str
    title: str 
    author: str 
    content: str 
    url : str 
    dom : str
    
class Update_Chat(SQLModel):
    id: uuid.UUID
    title: str|None = None
    delete_yn: bool|None = None
    
class Usage(SQLModel):
    user_llm_id: uuid.UUID  
    input_token:int 
    output_token:int

class GetDocument(SQLModel):
    title: str
    collection_id: uuid.UUID
    user_file_id:uuid.UUID