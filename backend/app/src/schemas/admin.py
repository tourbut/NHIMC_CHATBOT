from sqlmodel import SQLModel
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
