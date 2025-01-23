from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough,RunnableParallel
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field,create_model

from operator import itemgetter
from .parser import create_dynamic_schema, create_parser

from app.src.schemas import textmining as textmining_schema
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache, SQLAlchemyCache
from langchain_community.callbacks import get_openai_callback

import langchain

from ....core.config import settings
langchain.debug = settings.DEBUG
set_llm_cache(SQLiteCache(database_path=".cache.db"))

def create_chain(instruct_detail:textmining_schema.Get_Out_TmInstructDetail,
                 temperature:float=0.3,
                 callback_manager=None,
                 ):
    
    callback_manager = CallbackManager([StdOutCallbackHandler()])
    
    llm = ChatOllama(model=instruct_detail.mining_llm_name,
                     base_url=instruct_detail.mining_llm_url,
                     temperature=temperature,
                     callback_manager=callback_manager,
                     )
    
    dict_attr = {}
    for row in instruct_detail.output_schema_attr:
        dict_attr[row.attr_name] = (row.attr_type, row.attr_desc)
    
    schema = create_dynamic_schema(schema_name=instruct_detail.output_schema_name,
                                   schema_description=instruct_detail.output_schema_desc,
                                   schema_attr=dict_attr)
    
    class output_list(BaseModel):
        """information about a EMR Report."""
        
        Response: Optional[List[schema]]
    
    parser = create_parser(pydantic_object=output_list)
    
    template = """
    <INSTRUCTION>
    {instruct_prompt}
    </INSTRUCTION>
    <RESPONSE TEMPLATE>
    {response_prompt}
    </RESPONSE TEMPLATE>
    <OUTPUT FORMAT>
    {format_instructions}
    </OUTPUT FORMAT>
    <INPUT>
    {input}
    </INPUT>
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["input"],
        partial_variables={"format_instructions": parser.get_format_instructions(),
                           "instruct_prompt": instruct_detail.instruct_prompt,
                           "response_prompt": instruct_detail.response_prompt}
    )
    
    chain = prompt|llm|parser
    
    final_chain = RunnableParallel(
        output_prompt = prompt,
        textminig = chain
    )
    
    return final_chain
    
async def chain_astream(chain,input):
    chunks=[]
    input_token=0
    output_token=0
    
    
    response = chain.ainvoke({'input':input})
    
    callback_handler = get_openai_callback()
    with callback_handler as cb:
        async for chunk in chain.astream({'input':input}):
            inner_response = chunk.Response
            chunks.append(inner_response)
            yield textmining_schema.OutMessage(content=str(inner_response),
                                        input_token=None,
                                        output_token=None,
                                        is_done=False).model_dump_json()
        input_token = cb.prompt_tokens
        output_token = cb.completion_tokens
    
    response=chunks[0]
    
    for chunk in chunks[1:]:
        response+=chunk
    
    
    out_message = "```\n"
    
    for content in response:
        out_message += str(content)+"\n"
    
    out_message += "\n```"
    
    yield textmining_schema.OutMessage(content=out_message,
                    input_token=input_token,
                    output_token=output_token,
                    is_done=True).model_dump_json()
    
async def chain_invoke(chain,input):
    callback_handler = get_openai_callback()
    input_token=0
    output_token=0
    
    with callback_handler as cb:
        response = await chain.ainvoke({'input':input})
        input_token = cb.prompt_tokens
        output_token = cb.completion_tokens
        
    # Ensure response.Response is a list
    if isinstance(response['textminig'].Response, dict):
        response_list = [response['textminig'].Response]
    else:
        response_list = response['textminig'].Response
        
    return response_list,(input_token,output_token),response['output_prompt']