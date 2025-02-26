from sqlmodel import SQLModel
import uuid
from typing import List
from fastapi import UploadFile
class Usage(SQLModel):
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    tm_llm_id: uuid.UUID | None = None
    input_token:int 
    output_token:int
    
class GetUserLLM(SQLModel):
    id: uuid.UUID 
    source: str
    name: str
    api_key: str
    url: str
    llm_id: uuid.UUID

class DeleteFile(SQLModel):
    id: uuid.UUID

class FileUpload(SQLModel):
    file_name:str
    file_path:str
    file_size:int
    file_type:str
    file_ext:str
    file_desc:str | None = None
    embedding_yn:bool = False
    embedding_user_llm_id:uuid.UUID | None = None
    collection_id:uuid.UUID | None = None

class FileDetail(SQLModel):
    file_name:str
    file_desc:str | None = None
    separators:List[str] | None = None
    chunk_size:int | None = None
    chunk_overlap:int | None = None
    child_chunk_size:int | None = None
    child_chunk_overlap:int | None = None

class ResponseFile(SQLModel):
    id: uuid.UUID
    file_name:str
    file_size:int
    file_ext:str
    file_desc:str | None = None
    contents:List[str] = []
    
class CreateBotDocument(SQLModel):
    userfile_id:uuid.UUID 
    request_dept_id: uuid.UUID 
    is_active: bool = True

class GetFileList(SQLModel):
    id: uuid.UUID
    file_name:str
    file_size:int
    file_ext:str
    file_desc:str | None = None
    embedding_yn:bool = False
    