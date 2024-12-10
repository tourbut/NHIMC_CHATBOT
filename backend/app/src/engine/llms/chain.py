from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough,RunnableParallel
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager

from operator import itemgetter

from .prompt import (
    get_translate_prompt, 
    get_summary_prompt,
    get_chatbot_prompt,
    get_chatbot_prompt_with_history,
    get_chatbot_prompt_with_memory,
    get_thinking_prompt,
    get_thinking_chatbot)

from .parser import strparser,think_parser

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache, SQLAlchemyCache
#from ...deps import engine
#set_llm_cache(SQLAlchemyCache(engine))

import langchain

from ....core.config import settings
langchain.debug = settings.DEBUG

set_llm_cache(SQLiteCache(database_path=".cache.db"))


def translate_chain(api_key:str,
                    model:str='gpt-4o-mini',
                    temperature:float=0.7):
    
    prompt = get_translate_prompt()

    if model.startswith('gpt'):
        llm = ChatOpenAI(model=model,
                        temperature=temperature,
                        api_key=api_key)
    elif model.startswith('claude'):
        llm = ChatAnthropic(model=model,
                            temperature=temperature,
                            api_key=api_key)
    else:
        raise ValueError(f"Invalid model name: {model}")
    
    chain = prompt|llm
    return chain

def summarize_chain(api_key:str,
                    model:str='gpt-4o-mini',
                    temperature:float=0.7):
    
    prompt = get_summary_prompt()

    if model.startswith('gpt'):
        llm = ChatOpenAI(model=model,
                        temperature=temperature,
                        api_key=api_key)
    elif model.startswith('claude'):
        llm = ChatAnthropic(model=model,
                            temperature=temperature,
                            api_key=api_key)
    else:
        raise ValueError(f"Invalid model name: {model}")
    
    chain = prompt|llm
    return chain

def chatbot_chain(api_key:str,
                  model:str='gpt-4o-mini',
                  temperature:float=0.7,
                  callback_manager=None,
                  get_redis_history=None,
                  memory=None):
    
    if model.startswith('gpt'):
        llm = ChatOpenAI(model=model,
                        temperature=temperature,
                        api_key=api_key,
                        callback_manager=callback_manager,
                        stream_usage=True)
        
    elif model.startswith('claude'):
        llm = ChatAnthropic(model=model,
                            temperature=temperature,
                            api_key=api_key,
                            callback_manager=callback_manager)
    elif model.startswith('ollama'):
        llm = ChatOllama(model=model,
                         base_url= settings.OLLAMA_URL,
                         temperature=temperature,
                         callback_manager=callback_manager)
    else:
        raise ValueError(f"Invalid model name: {model}")
    
    if get_redis_history:
        prompt = get_chatbot_prompt_with_history()
        chain = prompt|llm
        # Create a runnable with message history
        chain_with_history = RunnableWithMessageHistory(
        chain, get_redis_history, input_messages_key="input", history_messages_key="history"
        )    
        return chain_with_history
    
    elif memory:
        runnable = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory.load_memory_variables)
        | itemgetter("chat_history")  # memory_key 와 동일하게 입력합니다.
        )
        prompt = get_chatbot_prompt_with_memory()
        return runnable|prompt|llm
    else:
        prompt = get_chatbot_prompt()
        chain = prompt|llm
        return chain

def map_rerank_chain(llm):
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field
    class AnswerWithScore(BaseModel):
        '''
        The user's question and the score and reasons for scoring the answer.
        '''
        score: float = Field( ..., title="Score from 1.0 - 10.0. 10.0 is the best score.")
        Reasons_for_scoring: str = Field( ..., title="Reasons for scoring.")
        
    
    parser = PydanticOutputParser(pydantic_object=AnswerWithScore)
    
    prompt_template = """
    <INSTRUCTION>
    Using ONLY the following context answer the user's question. If you can't just say you don't know, don't make anything up.
    If the answer answers the user question the score should be high, else it should be low.
    On a scale of 1.0 to 10.0, write whether you have enough context to answer the user's question.
    </INSTRUCTION>
    <QUESTION>
    {input} 
    </QUESTION>
    <CONTEXT> 
    {context}
    </CONTEXT>
    <FORMAT>
    {format_instructions}
    </FORMAT>
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    map_chain = prompt | llm | parser
    return map_chain
                        

def thinking_chatbot_chain(api_key:str,
                           source:str,
                           model:str='gpt-4o-mini',
                           temperature:float=0.1,
                           callback_manager=None,
                           memory=None,
                           document_meta=None,
                           retriever=None,
                           ):
    
    callback_manager = CallbackManager([StdOutCallbackHandler()])
    
    if model.startswith('gpt'):
        llm = ChatOpenAI(model=model,
                        temperature=temperature,
                        api_key=api_key,
                        callback_manager=callback_manager,
                        stream_usage=True)
        
    elif model.startswith('claude'):
        llm = ChatAnthropic(model=model,
                            temperature=temperature,
                            api_key=api_key,
                            callback_manager=callback_manager)
    elif source == 'ollama':
        llm = ChatOllama(model=model,
                         base_url= settings.OLLAMA_URL,
                         temperature=temperature,
                         callback_manager=callback_manager,
                         #format="json",
                         #num_gpu=4,
                         #num_ctx=1024*4,
                         #num_predict=512,
                         #num_thread=16,
                         )
    else:
        raise ValueError(f"Invalid model name: {model}")
    
    runnable = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory.load_memory_variables)| itemgetter("chat_history")  # memory_key 와 동일하게 입력합니다.
        )
    
    think_prompt = get_thinking_prompt(think_parser,document_meta)
    prompt = get_thinking_chatbot()
    
    think_chain = runnable|think_prompt|llm|think_parser
    answer_chain = prompt|llm
    rerank_chain = map_rerank_chain(llm)
    
    def get_thought(output):
        return output["thought"].THOUGHT
    
    def get_context(output):
        if retriever:
            docs = retriever.invoke(output["thought"].search_msg)
            inputs = []
            for doc in docs:
                inputs.append({"input":output["thought"].search_msg,"context": doc.page_content})
            
            results = rerank_chain.batch(inputs,
                                         config={"max_concurrency": 3},)
            idx_max = results.index(max(results,key=lambda x:x.score))
            
            result = results[idx_max]
            
            if result.score <= 6:
                return "해당 문서 없음"
            else :
                
                rtn = f"""검색어 : {output["thought"].search_msg}
                검색 문서 Score: {results[idx_max].score}점(10점 만점)
                Score 측정 사유:{results[idx_max].Reasons_for_scoring}
                검색결과
                """
                rtn = rtn + "\n\n-------- page : "+str(idx_max)+" --------\n\n" + docs[idx_max].page_content
            
            return rtn
        else:
            return ""
        
    def output_formatter(output):
        print(output)
        return {
            "thought": output["thought"],
            "answer": output["answer"],
        }
        
    final_chain = (
        RunnableParallel(
            thought = think_chain,
            input = RunnablePassthrough()
        )
        |{
            "thought":RunnableLambda(get_thought),
            "context":RunnableLambda(get_context),
            "input" : RunnablePassthrough()
        }|
        {
            "thought":RunnablePassthrough(),
            "context":RunnablePassthrough(),
            "answer":answer_chain
        }
        |RunnableLambda(output_formatter)
        )
    
    
    return final_chain