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
    embedding_model_id:Optional[uuid.UUID] = Field(foreign_key="llm.id",nullable=True,description="임베딩모델ID")
    collection_id:Optional[uuid.UUID] = Field(nullable=True,description="컬렉션ID")

class UserPrompt(CommonBase,table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
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

class Chats(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    user_id: uuid.UUID  = Field(foreign_key="user.id", description="유저ID")
    title: str = Field(nullable=False, description="채팅명")
    user_llm_id: uuid.UUID | None = Field(foreign_key="userllm.id",nullable=True, description="유저LLMID")
    dept_llm_id: uuid.UUID | None = Field(foreign_key="deptllm.id",nullable=True, description="부서LLMID")
    user_file_id: uuid.UUID  = Field(foreign_key="userfiles.id",nullable=False, description="유저파일ID")

class Messages(CommonBase,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="ID")
    chat_id: uuid.UUID = Field(foreign_key="chats.id", description="채팅ID")
    user_id: uuid.UUID  = Field(foreign_key="user.id", description="유저ID")
    name:str = Field(nullable=False, description="이름")
    content: str = Field(nullable=False, description="내용")
    is_user: bool = Field(nullable=False, description="유저여부")
    thought: str | None = Field(nullable=True, description="생각")
    tools: str | None = Field(nullable=True, description="도구사용내용")
