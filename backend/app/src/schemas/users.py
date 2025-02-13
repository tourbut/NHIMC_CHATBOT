from app.models import *
from sqlmodel import SQLModel
import uuid

class UserCreate(SQLModel):
    empl_no: str
    password: str
    name: str 

class UserDetail(SQLModel):
    name: str 
    dept_cd: str

class UserPublic(SQLModel):
    id: uuid.UUID 
    name:str
    is_active: bool
    
class Token(SQLModel):
    id : uuid.UUID
    name: str
    is_admin: bool = False
    is_active : bool = True
    access_token: str
    token_type: str = "bearer"
    dept_cd: str
    dept_nm: str

class TokenPayload(SQLModel):
    sub: uuid.UUID | None = None

class GetUserAndDept(SQLModel):
    id: uuid.UUID 
    empl_no: str 
    password: str
    name: str 
    is_active: bool 
    is_admin: bool
    dept_cd: str
    dept_nm: str