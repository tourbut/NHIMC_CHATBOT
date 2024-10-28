from langchain_core.output_parsers import StrOutputParser
strparser = StrOutputParser()

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any

class AIThink(BaseModel):
    THOUGHT: str = Field(..., title="모델이 생각하는 내용")
    search_msg: str = Field(..., title="문서에서 검색하려는 내용")
    
pydantic_parser = PydanticOutputParser(pydantic_object=AIThink)