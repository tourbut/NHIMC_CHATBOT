from sqlmodel import Field, SQLModel, desc
from pydantic import EmailStr
import uuid
from datetime import datetime
from typing import Optional

from datetime import datetime


class CommonBase(SQLModel):
    create_date: datetime = Field(default=datetime.now())
    update_date: datetime = Field(default=datetime.now())
    delete_yn: bool = Field(default=False)

class User(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    empl_no: str = Field(unique=True, nullable=False, description="사번")
    password: str = Field(nullable=False, description="비밀번호")
    name: str = Field(nullable=False,description="이름")
    is_active: bool = Field(default=True,description="활성화여부")
    is_admin: bool = Field(default=False,description="관리자여부")

class Dept(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    dept_cd: str = Field(nullable=False, description="부서코드")
    dept_nm: str = Field(nullable=False, description="부서명")
    is_active: bool = Field(default=True, description="활성화여부")

class UserDept(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    dept_id: uuid.UUID = Field(foreign_key="dept.id")
    is_active: bool = Field(default=True, description="활성화여부")

class LLM(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    source: str = Field(nullable=False)
    type: str = Field(nullable=False)
    name: str = Field(nullable=False)
    description: str | None = Field(nullable=True)
    input_price: float = Field(nullable=False)
    output_price: float = Field(nullable=False)
    is_active: bool = Field(default=True)
    url: Optional[str] = Field(nullable=True)

class DeptAPIKey(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    dept_id: uuid.UUID = Field(foreign_key="dept.id")
    api_name:str = Field(nullable=False)
    api_key:str = Field(nullable=False)
    active_yn:bool = Field(default=True)

class DeptLLM(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    dept_id: uuid.UUID = Field(foreign_key="dept.id")
    llm_id: uuid.UUID = Field(foreign_key="llm.id")
    api_id: uuid.UUID = Field(foreign_key="deptapikey.id")
    active_yn:bool = Field(default=True)
        
class UserAPIKey(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    api_name:str = Field(nullable=False)
    api_key:str = Field(nullable=False)
    active_yn:bool = Field(default=True)

class UserLLM(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    llm_id: uuid.UUID = Field(foreign_key="llm.id")
    api_id: uuid.UUID = Field(foreign_key="userapikey.id")
    active_yn:bool = Field(default=True)

class UserUsage(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_llm_id: uuid.UUID | None = Field(foreign_key="userllm.id",nullable=True, description="유저LLMID")
    dept_llm_id: uuid.UUID | None = Field(foreign_key="deptllm.id",nullable=True, description="부서LLMID")
    tm_llm_id: uuid.UUID | None = Field(foreign_key="tmllm.id",nullable=True, description="텍스트마이닝LLMID")
    usage_date:datetime = Field(default=datetime.now())
    input_token:int = Field(nullable=False)
    output_token:int = Field(nullable=False)

class UserFiles(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    file_name:str = Field(nullable=False,description="파일명")
    file_path:str = Field(nullable=False,description="파일경로")
    file_size:int = Field(nullable=False,description="파일크기")
    file_type:str = Field(nullable=False,description="파일타입")
    file_ext:str = Field(nullable=False,description="파일확장자")
    file_desc:str | None = Field(nullable=True,description="파일설명")
    embedding_yn:bool = Field(default=False,nullable=True,description="임베딩여부")
    embedding_user_llm_id:Optional[uuid.UUID] = Field(foreign_key="userllm.id",nullable=True,description="임베딩유저모델ID")
    collection_id:Optional[uuid.UUID] = Field(nullable=True,description="컬렉션ID")

class Chats(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID  = Field(foreign_key="user.id", description="유저ID")
    title: str = Field(nullable=False, description="채팅명")
    user_llm_id: uuid.UUID | None = Field(foreign_key="userllm.id",nullable=True, description="유저LLMID")
    dept_llm_id: uuid.UUID | None = Field(foreign_key="deptllm.id",nullable=True, description="부서LLMID")
    user_file_id: uuid.UUID | None = Field(foreign_key="userfiles.id",nullable=True, description="유저파일ID")
    chatbot_id: uuid.UUID | None = Field(foreign_key="chatbot.id",nullable=True, description="챗봇ID")

class Messages(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    chat_id: Optional[uuid.UUID] = Field(foreign_key="chats.id", description="채팅ID")
    chatbot_id: Optional[uuid.UUID] = Field(foreign_key="chatbot.id", description="챗봇ID")
    user_id: uuid.UUID  = Field(foreign_key="user.id", description="유저ID")
    name:str = Field(nullable=False, description="이름")
    content: str = Field(nullable=False, description="내용")
    is_user: bool = Field(nullable=False, description="유저여부")
    thought: str | None = Field(nullable=True, description="생각")
    tools: str | None = Field(nullable=True, description="도구사용내용")

class UserPrompt(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    instruct_prompt: str | None = Field(nullable=True)
    response_prompt: str | None = Field(nullable=True)

class SystemPrompt(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID = Field(foreign_key="user.id", description="유저ID")
    work_cd: str = Field(nullable=False, description="작업코드")
    description: str | None = Field(nullable=True, description="설명")
    instruct_prompt: str | None = Field(nullable=True, description="지시 프롬프트")
    response_prompt: str | None = Field(nullable=True, description="응답 프롬프트")

class ClsfCode(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    clsf_cd: str = Field(nullable=False, description="분류코드")
    clsf_nm: str = Field(nullable=False, description="분류명")
    clsf_desc: str | None = Field(nullable=True, description="분류설명")

class CommonCode(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    clsf_cd: str = Field(nullable=False, description="분류코드")
    code: str = Field(nullable=False, description="코드")
    code_nm: str = Field(nullable=False, description="코드명")
    code_desc: str | None = Field(nullable=True, description="코드설명")

#ChatBot

class Tools(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    tool_name: str = Field(nullable=False, description="이름")
    description: Optional[str] = Field(nullable=True, description="설명")
    api_url: Optional[str] = Field(nullable=True,description="API URL")
    api_key: Optional[str] = Field(nullable=True,description="API KEY")
    parameters : Optional[str] = Field(nullable=True,description="파라미터")    
    user_id: uuid.UUID = Field(foreign_key="user.id", description="유저ID")

class BotTools(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    chatbot_id: uuid.UUID = Field(foreign_key="chatbot.id", description="챗봇ID")
    tools_id: uuid.UUID = Field(foreign_key="tools.id", description="도구ID")

class BotDocuments(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    userfile_id: uuid.UUID = Field(foreign_key="userfiles.id", description="유저파일ID")
    request_dept_id : uuid.UUID = Field(foreign_key="dept.id", description="요청부서ID")
    is_active: bool = Field(default=True, description="활성화여부")
    user_id : uuid.UUID = Field(foreign_key="user.id", description="유저ID")
    
class ChatBot(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    bot_name : str = Field(nullable=False, description="챗봇명")
    description : Optional[str] = Field(nullable=True,description="설명")
    instruct_prompt: Optional[str] = Field(nullable=True,default=None,description="지시 프롬프트")
    thought_prompt: Optional[str] = Field(nullable=True,default=None,description="생각 프롬프트")
    user_llm_id: Optional[uuid.UUID] = Field(foreign_key="userllm.id",nullable=True,default=None, description="유저LLMID")
    dept_llm_id: Optional[uuid.UUID] = Field(foreign_key="deptllm.id",nullable=True,default=None, description="부서LLMID")
    user_file_id: Optional[uuid.UUID] = Field(foreign_key="userfiles.id",nullable=True,default=None, description="유저파일ID")
    bottools_id : Optional[uuid.UUID] = Field(foreign_key="bottools.id",nullable=True,default=None, description="도구ID")
    is_public: bool = Field(default=False, description="공개여부")
    temperature: Optional[float] = Field(nullable=True,default=None, description="창의성온도")
    search_kwargs: Optional[str] = Field(nullable=True,default=None, description="문서검색 파라미터")
    user_id: uuid.UUID = Field(foreign_key="user.id", description="생성자ID")
    is_agent: Optional[bool] = Field(default=False, description="에이전트여부")
    
#Mining Models

class TmLLM(CommonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    llm_id: uuid.UUID = Field(foreign_key="llm.id", description="LLMID")
    active_yn:bool = Field(default=True, description="활성화여부")

class TmOutputSchema(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    schema_name : str = Field(nullable=False, description="스키마명")
    schema_desc : str = Field(nullable=False, description="스키마설명")
    schema_version : str = Field(nullable=False, description="스키마버전")
    topic_id : uuid.UUID = Field(foreign_key="tmtopic.id", description="토픽ID")
    user_id : uuid.UUID = Field(foreign_key="user.id", description="유저ID")

class TmOutputSchemaAttr(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    schema_id : uuid.UUID = Field(foreign_key="tmoutputschema.id", description="스키마ID")
    attr_name : str = Field(nullable=False, description="속성명")
    attr_desc : str = Field(nullable=False, description="속성설명")
    attr_type : str = Field(nullable=False, description="속성타입")
    user_id : uuid.UUID = Field(foreign_key="user.id", description="유저ID")
    
class TmMessages(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    chat_id: uuid.UUID = Field(foreign_key="tmchats.id", description="채팅ID")
    user_id: uuid.UUID = Field(foreign_key="user.id", description="유저ID")
    name:str = Field(nullable=False, description="이름")
    content: str = Field(nullable=False, description="내용")
    full_prompt: Optional[str] = Field(nullable=True, description="풀프롬프트")
    is_user: bool = Field(nullable=False, description="유저여부")

class TmChats(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    title: str = Field(nullable=False, description="제목")
    description: Optional[str] = Field(nullable=True, description="설명")
    user_id: uuid.UUID = Field(foreign_key="user.id", description="유저ID")
    instruct_id: Optional[uuid.UUID] = Field(foreign_key="tminstruct.id",nullable=True, description="인스트럭션ID")
    
class TmInstruct(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID = Field(foreign_key="user.id", description="유저ID")
    title: str = Field(nullable=False, description="제목")
    memo: str = Field(nullable=False, description="메모")
    topic_id: uuid.UUID = Field(foreign_key="tmtopic.id", description="토픽ID")
    userprompt_id : uuid.UUID = Field(foreign_key="userprompt.id", description="유저프롬프트ID")
    mining_llm_id: uuid.UUID = Field(foreign_key="tmllm.id", description="마이닝LLMID")
    output_schema_id: uuid.UUID = Field(foreign_key="tmoutputschema.id", description="아웃풋스키마ID")
    is_final: bool = Field(default=False,nullable=True, description="최종 등록여부")
    load_cplt_yn : Optional[str] = Field(default='N',nullable=True,description="로드 완료 여부")
    
class TmExecSet(CommonBase,table=True):
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    instruct_id: uuid.UUID = Field(foreign_key="tminstruct.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    load_cplt_yn : Optional[str] = Field(default='N',nullable=True,description="로드 완료 여부")

class TmTopic(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    topic_name : str = Field(nullable=False, description="토픽명")
    contents    : str = Field(nullable=False, description="내용")
    sql: Optional[str] = Field(nullable=True, description="SQL")
    user_id    : uuid.UUID = Field(foreign_key="user.id", description="유저ID")
    load_cplt_yn : Optional[str] = Field(default='N',nullable=True,description="로드 완료 여부")
    
class TmMaster(CommonBase,table=True):
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    exec_set_id: uuid.UUID = Field(foreign_key="tmexecset.id")
    status : str = Field(nullable=False, description="상태")
    start_date : datetime = Field(nullable=False, description="시작일시")
    end_date : Optional[datetime] = Field(nullable=True, description="종료일시")
    comments : Optional[str] = Field(nullable=True, description="코멘트")
    load_cplt_yn : Optional[str] = Field(default='N',nullable=True,description="로드 완료 여부")

class TmData(CommonBase,table=True):
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    master_id : uuid.UUID = Field(foreign_key="tmmaster.id")
    origin_key : str = Field(nullable=False, description="원본 Key")
    origin_text : Optional[str] = Field(nullable=True, description="원문")
    load_cplt_yn : Optional[str] = Field(default='N',nullable=True,description="로드 완료 여부")

class TmResult(CommonBase,table=True):
    master_id : uuid.UUID = Field(foreign_key="tmmaster.id", primary_key=True)
    data_id : uuid.UUID = Field(foreign_key="tmdata.id", primary_key=True)
    seq : int = Field(primary_key=True)
    item_seq : int = Field(primary_key=True)
    item_nm : str = Field(nullable=False, description="항목명")
    item_value : Optional[str] = Field(nullable=True, description="항목값")
    load_cplt_yn : Optional[str] = Field(default='N',nullable=True,description="로드 완료 여부")
    
    