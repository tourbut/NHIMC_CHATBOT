from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import PydanticOutputParser,JsonOutputParser

from pydantic import BaseModel, Field, create_model
from typing import Dict, Any, Optional

strparser = StrOutputParser()

class AIThink(BaseModel):
    '''모델 추론 결과
    Respond to Korean.
    '''
    THOUGHT: str = Field(..., title="사용자의 질문에 처음 모델이 생각한 내용")
    search_msg: str = Field(..., title="제공된 문서에서 검색하려는 내용")
    
think_parser = PydanticOutputParser(pydantic_object=AIThink)

def create_dynamic_schema(schema_name: str,schema_description: str, schema_attr: dict):
    fields = schema_attr
    pydantic_fields = {name: (Optional[field_type], Field(description=default_value)) for name, (field_type, default_value) in fields.items()}
    model = create_model(schema_name, **pydantic_fields)
    model.__doc__ = schema_description
    return model

def create_parser(pydantic_object:BaseModel, output_type:str="pydantic"):
    if output_type == "json":
        return JsonOutputParser(pydantic_object=pydantic_object)
    elif output_type == "pydantic":
        return PydanticOutputParser(pydantic_object=pydantic_object)