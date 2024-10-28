import uuid
from sqlmodel import SQLModel

class get_collection(SQLModel):
    uuid: uuid.UUID
    name: str