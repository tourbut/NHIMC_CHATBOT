from typing import List
from sqlmodel import SQLModel
from datetime import datetime
import uuid

class CreateTopic(SQLModel):
    topic_name: str
    contents: str
    sql: str| None = None

class Create_Out_Topic(SQLModel):
    id : uuid.UUID
    topic_name: str
    contents: str
    sql: str | None = None
    
class Get_Out_Topic(SQLModel):
    id : uuid.UUID
    topic_name: str
    contents: str
    sql: str| None = None

class UpdateTopic(SQLModel):
    id: uuid.UUID
    topic_name: str
    contents: str
    sql: str| None = None
    
class CreateTmLLM(SQLModel):
    llm_id : uuid.UUID
    active_yn:bool
    
class Get_Out_TmLLM(SQLModel):
    id : uuid.UUID
    llm_id:uuid.UUID  | None  = None
    source: str
    type: str
    name: str
    description: str
    url:str  | None  = None
    active_yn:bool
    
class CreateTmChat(SQLModel):
    title: str
    description : str | None = None
    instruct_id : uuid.UUID | None = None

class Create_Out_TmChat(SQLModel):
    id : uuid.UUID
    title : str

class UpdateTmChat(SQLModel):
    id: uuid.UUID
    title: str  | None = None
    description : str | None = None
    instruct_id : uuid.UUID | None = None

class Get_Out_TmChat(SQLModel):
    id : uuid.UUID
    title: str
    instruct_id : uuid.UUID | None = None
    instruct_title : str | None = None
    topic_id : uuid.UUID | None = None
    topic_name : str | None = None

class CreateTmOutputSchemaAttr(SQLModel):
    attr_name : str
    attr_desc : str
    attr_type : str
    
class Create_Out_TmOutputSchemaAttr(SQLModel):
    id : uuid.UUID
    attr_name : str
    attr_desc : str
    attr_type : str

class UpdateTmOutputSchemaAttr(SQLModel):
    id : uuid.UUID | None = None
    attr_name : str | None = None
    attr_desc : str | None = None
    attr_type : str | None = None
    delete_yn : bool | None = None

class Get_Out_TmOutputSchemaAttr(SQLModel):
    id : uuid.UUID
    attr_name : str
    attr_desc : str
    attr_type : str
    
class CreateTmOutputSchema(SQLModel):
    schema_name : str
    schema_desc : str
    schema_version : str
    topic_id : uuid.UUID
    attr : List[CreateTmOutputSchemaAttr]

class Create_Out_TmOutputSchema(SQLModel):
    id : uuid.UUID
    schema_name : str
    schema_desc : str
    schema_version : str
    topic_id : uuid.UUID
    attr : List[Create_Out_TmOutputSchemaAttr]

class UpdateTmOutputSchema(SQLModel):
    id : uuid.UUID | None = None
    schema_name : str | None = None
    schema_desc : str | None = None
    schema_version : str | None = None
    topic_id : uuid.UUID | None = None
    attr : List[UpdateTmOutputSchemaAttr] | None = None

class Get_Out_TmOutputSchema(SQLModel):
    id : uuid.UUID
    schema_name : str
    schema_desc : str
    schema_version : str
    topic_id : uuid.UUID
    attr : List[Get_Out_TmOutputSchemaAttr] | None = None
    
class CreateUserPrompt(SQLModel):
    instruct_prompt: str
    response_prompt: str

class Get_Out_UserPrompt(SQLModel):
    id : uuid.UUID
    instruct_prompt: str
    response_prompt: str

class UpdateUserPrompt(SQLModel):
    id: uuid.UUID
    instruct_prompt: str | None = None
    response_prompt: str | None = None
    
class CreateTmInstruct(SQLModel):
    title: str
    memo: str
    topic_id: uuid.UUID
    mining_llm_id: uuid.UUID
    instruct_prompt: str
    response_prompt: str
    output_schema_id: uuid.UUID
    chat_id: uuid.UUID

class UpdateTmInstruct(SQLModel):
    id: uuid.UUID
    title: str | None = None
    memo: str | None = None
    topic_id: uuid.UUID | None = None
    mining_llm_id: uuid.UUID | None = None
    instruct_prompt: str | None = None
    response_prompt: str | None = None
    output_schema_id: uuid.UUID | None = None

class Create_Out_TmInstruct(SQLModel):
    instruct_id : uuid.UUID

class Get_Out_TmInstruct(SQLModel):
    id : uuid.UUID
    title: str
    memo: str
    topic_id: uuid.UUID
    mining_llm_id: uuid.UUID
    instruct_prompt: str
    response_prompt: str
    output_schema_id: uuid.UUID
    
class Get_Out_TmInstructDetail(SQLModel):
    id : uuid.UUID
    title: str
    memo: str
    topic_id: uuid.UUID
    topic_name : str
    mining_llm_id: uuid.UUID
    mining_llm_name : str
    mining_llm_url : str
    instruct_prompt: str
    response_prompt: str
    output_schema_id: uuid.UUID
    output_schema_name : str
    output_schema_desc : str
    output_schema_attr : List[Get_Out_TmOutputSchemaAttr]
    
class CreateTmChats(SQLModel):
    title: str
    instruct_id : uuid.UUID

class Get_Out_TmChats(SQLModel):
    id : uuid.UUID
    title: str
    instruct_id : uuid.UUID

class SendMessage(SQLModel):
    chat_id: uuid.UUID
    instruct_id : uuid.UUID
    input: str

class OutMessage(SQLModel):
    content: str
    full_prompt: str | None = None
    input_token: int | None = None
    output_token: int | None = None
    create_date: datetime = datetime.now()
    is_done: bool = False

class CreateTmMessages(SQLModel):
    chat_id: uuid.UUID
    name:str
    content: str
    full_prompt: str | None = None
    is_user: bool

class Get_Out_TmMessages(SQLModel):
    id : uuid.UUID
    chat_id: uuid.UUID
    name:str
    content: str
    full_prompt: str | None = None
    is_user: bool
    create_date : datetime
    
class CreateTmExecSet(SQLModel):
    instruct_id: uuid.UUID

class Get_Out_TmExecSet(SQLModel):
    id : uuid.UUID
    instruct_id: uuid.UUID

class CreateTmMaster(SQLModel):
    exec_set_id: uuid.UUID
    status : str
    start_date : datetime | None = None
    end_date : datetime | None = None

class Get_Out_TmMaster(SQLModel):
    id : uuid.UUID
    exec_set_id: uuid.UUID
    status : str
    start_date : datetime
    end_date : datetime
    
class CreateTmData(SQLModel):
    master_id : uuid.UUID
    origin_text : str

class Get_Out_TmData(SQLModel):
    id : uuid.UUID
    master_id : uuid.UUID
    origin_text : str
    
class CreateTmResult(SQLModel):
    master_id : uuid.UUID
    data_id : uuid.UUID
    seq : int
    item_nm : str
    item_value : str

class Get_Out_TmResult(SQLModel):
    master_id : uuid.UUID
    data_id : uuid.UUID
    seq : int
    item_nm : str
    item_value : str
    
class Usage(SQLModel):
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    tm_llm_id: uuid.UUID | None = None
    input_token:int 
    output_token:int