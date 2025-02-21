import uuid
from sqlmodel import SQLModel
from datetime import datetime


class SendMessage(SQLModel):
    chat_id: uuid.UUID 
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    input: str
    
class OutMessage(SQLModel):
    content: str
    thought : str | None = None
    tools : dict | None = None
    input_token: int | None = None
    output_token: int | None = None
    create_date: datetime = datetime.now()
    is_done: bool = False
    
class GetUserLLM(SQLModel):
    gubun: str
    llm_id: uuid.UUID 
    id: uuid.UUID 
    source: str
    name: str
    type: str
    api_key: str
    url:str | None

class GetDeptLLM(SQLModel):
    id: uuid.UUID 
    source: str
    name: str
    api_key: str
    url:str | None

class CreateChat(SQLModel):
    title: str
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None  = None
    user_file_id: uuid.UUID| None  = None
    chatbot_id: uuid.UUID| None  = None

class ResponseChat(SQLModel):
    id: uuid.UUID
    title: str
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    user_file_id: uuid.UUID | None = None
    chatbot_id: uuid.UUID| None  = None
    
class GetChat(SQLModel):
    category: str = "chat"
    id: uuid.UUID
    title: str
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    user_file_id: uuid.UUID | None = None
    chatbot_id: uuid.UUID| None  = None

class GetMessages(SQLModel):
    chat_id: str

class ReponseMessages(SQLModel):
    chat_id: uuid.UUID |None = None
    chatbot_id: uuid.UUID |None = None
    name:str
    content: str|None
    thought : str|None = None
    tools : dict|None = None
    is_user: bool
    create_date: datetime

class CreateMessage(SQLModel):
    chat_id: uuid.UUID |None = None
    chatbot_id: uuid.UUID |None = None
    user_id: uuid.UUID 
    name: str 
    content: str |None = None
    thought : str |None = None
    tools : str |None = None
    is_user: bool
    create_date: datetime = datetime.now()
    update_date: datetime = datetime.now()
    
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
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    tm_llm_id: uuid.UUID | None = None
    input_token:int 
    output_token:int

class GetDocument(SQLModel):
    title: str
    description: str | None = None
    collection_id: uuid.UUID
    user_file_id:uuid.UUID | None = None

class CreateTools(SQLModel):
    tool_name: str
    description: str
    api_url: str
    api_key: str
    parameters : str

class CreateBotTools(SQLModel):
    chatbot_id: uuid.UUID
    tools_id: uuid.UUID

class CreateChatBot(SQLModel):
    bot_name : str
    description : str | None = None

class Create_Out_ChatBot(SQLModel):
    id: uuid.UUID
    bot_name : str
    description : str | None = None
    instruct_prompt: str | None = None
    thought_prompt: str | None = None
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    user_file_id: uuid.UUID | None = None
    bottools_id : uuid.UUID | None = None
    is_public: bool = False
    user_id: uuid.UUID

class UpdateChatBot(SQLModel):
    id: uuid.UUID
    bot_name : str
    description : str | None = None
    instruct_prompt: str | None = None
    thought_prompt: str | None = None
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    user_file_id: uuid.UUID | None = None
    bottools_id : uuid.UUID | None = None
    is_public: bool = False

class Update_Out_ChatBot(SQLModel):
    id: uuid.UUID
    bot_name : str
    description : str | None = None
    instruct_prompt: str | None = None
    thought_prompt: str | None = None
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    user_file_id: uuid.UUID | None = None
    bottools_id : uuid.UUID | None = None
    is_public: bool = False

class Get_Out_ChatBot(SQLModel):
    id: uuid.UUID
    bot_name : str
    description : str | None = None
    instruct_prompt: str | None = None
    thought_prompt: str | None = None
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    user_file_id: uuid.UUID | None = None
    bottools_id : uuid.UUID | None = None
    is_public: bool = False
    user_id: uuid.UUID

class CreateUserPrompt(SQLModel):
    instruct_prompt: str | None = None
    response_prompt: str | None = None
    
class Get_Out_Document(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    collection_id: uuid.UUID
    user_file_id:uuid.UUID 
    request_dept_nm: str
    is_active: bool

class CreateBotDocument(SQLModel):
    userfile_id:uuid.UUID 
    request_dept_id: str
    is_active: bool = True

class Create_Out_Document(SQLModel):
    id: uuid.UUID
    
class SendMessageToChatbot(SQLModel):
    chat_id: uuid.UUID | None = None
    chatbot_id: uuid.UUID | None = None
    input: str
    
class GetChatbotAllData(SQLModel):
    id: uuid.UUID
    instruct_prompt: str | None = None
    thought_prompt: str | None = None
    user_llm_id: uuid.UUID | None = None
    dept_llm_id: uuid.UUID | None = None
    userllm_name: str | None = None
    userllm_id: str | None = None
    deptllm_name: str | None = None
    deptllm_id: str | None = None
    embedding_name: str | None = None
    embedding_id: str | None = None
    file_title: str | None = None
    file_description: str | None = None
    collection_id: uuid.UUID | None = None
    bottools_id: uuid.UUID | None = None
    
class ClearMessages(SQLModel):
    id: uuid.UUID | None = None