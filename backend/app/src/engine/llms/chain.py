from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
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

from .parser import strparser,pydantic_parser

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache, SQLAlchemyCache
#from ...deps import engine
#set_llm_cache(SQLAlchemyCache(engine))

import langchain
langchain.debug = True

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
    
def thinking_chatbot_chain(api_key:str,
                           model:str='gpt-4o-mini',
                           temperature:float=0.7,
                           callback_manager=None,
                           memory=None,
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
    else:
        raise ValueError(f"Invalid model name: {model}")
    
    runnable = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory.load_memory_variables)
        | itemgetter("chat_history")  # memory_key 와 동일하게 입력합니다.
        )
    
    think_prompt = get_thinking_prompt(pydantic_parser)
    prompt = get_thinking_chatbot()
    
    
    think_chain = runnable|think_prompt|llm|pydantic_parser
    answer_chain = prompt|llm

    def get_thought(output):
        return output["thought"].THOUGHT
    
    def get_context(output):
        if retriever:
            docs = retriever.invoke(output["thought"].search_msg)
            rtn = ""
            for doc in docs:
                rtn += doc.page_content + "\n\n"
            return rtn
        else:
            return ""
    
    def output_formatter(output):
        return {
            "thought": output["thought"],
            "answer": output["answer"]
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