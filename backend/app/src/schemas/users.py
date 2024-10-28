from app.models import *
from sqlmodel import SQLModel
import uuid

class UserCreate(SQLModel):
    empl_no: str
    password: str
    name: str 
    dept_cd: str

class UserDetail(SQLModel):
    name: str 
    dept_cd: str

class UserPublic(SQLModel):
    id: uuid.UUID 
    name:str
    is_active: bool
    
class Token(SQLModel):
    name: str
    is_admin: bool = False
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: uuid.UUID | None = None
