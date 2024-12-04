

from langchain_core.output_parsers import StrOutputParser
strparser = StrOutputParser()

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any

class AIThink(BaseModel):
    '''모델 추론 결과
    Respond to Korean.
    '''
    THOUGHT: str = Field(..., title="사용자의 질문에 처음 모델이 생각한 내용")
    search_msg: str = Field(..., title="제공된 문서에서 검색하려는 내용")
    
think_parser = PydanticOutputParser(pydantic_object=AIThink)