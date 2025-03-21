from typing import List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatPerplexity

from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda, RunnablePassthrough,RunnableParallel
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from operator import itemgetter

from .prompt import (
    create_chatbot_prompt,
    create_thinking_prompt,
    create_thinking_chatbot_prompt,
    get_thinking_prompt,
    get_thinking_chatbot,
    get_thinking_NoDoc_prompt,
    get_thinking_NoDoc_chatbot)

from ..common.parser import strparser,think_parser

import langchain

from ....core.config import settings
langchain.debug = settings.DEBUG

if settings.LLM_CACHE:
    from ...deps import engine
    from langchain.globals import set_llm_cache
    from langchain_community.cache import SQLiteCache, SQLAlchemyCache
    set_llm_cache(SQLAlchemyCache(engine))
    print("Using LLM Cache")

def create_llm(source:str,
               api_key:str,
               model:str='gpt-4o-mini',
               base_url:str='http://localhost:11434',
               temperature:float=0.7,
               callback_manager=None):
    
    if source == 'openai':
        llm = ChatOpenAI(model=model,
                        temperature=temperature,
                        api_key=api_key,
                        callback_manager=callback_manager,
                        stream_usage=True)
        
    elif source == 'claude':
        llm = ChatAnthropic(model=model,
                            temperature=temperature,
                            api_key=api_key,
                            callback_manager=callback_manager)
    elif source == 'ollama':
        llm = ChatOllama(model=model,
                         base_url= base_url,
                         temperature=temperature,
                         callback_manager=callback_manager,
                         )
    elif source == 'perplexity':
        llm = ChatPerplexity(model=model,
                             temperature=temperature,
                             api_key=api_key,
                             callback_manager=callback_manager)
    else:
        raise ValueError(f"Invalid model name: {model}")
    
    return llm

def map_rerank_chain(llm):
    
    class AnswerEvaluation(BaseModel):
        """Model for evaluating search result quality"""
        
        score: float = Field(
            ..., 
            title="Overall Score",
            description="Quality score of search results (1.0-10.0)",
            ge=1.0,
            le=10.0
        )
        
        evaluation_reasons: str = Field(
            ...,
            title="Evaluation Reasons",
            description="Specific reasons for each score given"
        )
        
    
    parser = PydanticOutputParser(pydantic_object=AnswerEvaluation)
    
    prompt_template = """
<SYSTEM>
You are an expert evaluator. Rate how well the context answers the question on a scale of 1.0-10.0:
1.0~2.9: Completely irrelevant or incorrect
3.0~4.9: Partially relevant but insufficient
5.0~6.9: Adequately answers the question
7.0~8.9: Good answer with minor gaps
9.0~10.0: Perfect and comprehensive answer
Respond to Korean.
</SYSTEM>

<QUESTION>
{input}
</QUESTION>

<CONTEXT>
{context}
</CONTEXT>

<OUTPUT FORMAT>
{format_instructions}
</OUTPUT FORMAT>
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
                           base_url:str='http://localhost:11434',
                           temperature:float=0.1,
                           callback_manager=None,
                           memory=None,
                           document_meta=None,
                           retriever=None,
                           ):
    
    callback_manager = CallbackManager([StdOutCallbackHandler()])
    
    llm = create_llm(source=source,
                     api_key=api_key,
                     model=model,
                     base_url=base_url,
                     temperature=temperature,
                     callback_manager=callback_manager)
    
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
            rtn = f"""검색어 : {output["thought"].search_msg}
            """
            
            docs = retriever.invoke(output["thought"].search_msg)
            inputs = []
            for doc in docs:
                inputs.append({"input":output["thought"].search_msg,"context": doc.page_content})
            
            results = rerank_chain.batch(inputs,
                                         config={"max_concurrency": 3},)

            final_idx=[]
            for result in results:
                if result.score >= 7:
                    final_idx.append(results.index(result))
            
            if len(final_idx) == 0:
                rtn += "해당 문서 없음"
                return rtn
            else :
                rtn += f"""총 문서 수: {len(docs)}"""
                for idx in final_idx:
                    rtn+=f"""
                    ---------Doc No.{idx}---------
                    검색 문서 적합 점수(10점 만점): {results[idx].score}점
                    측정 사유:{results[idx].evaluation_reasons}
                    ---------검색결과---------
                    """
                    rtn = rtn + docs[idx].page_content
            
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

def thinking_chatbot_NoDoc_chain(api_key:str,
                           source:str,
                           model:str='gpt-4o-mini',
                           base_url:str='http://localhost:11434',
                           temperature:float=0.1,
                           callback_manager=None,
                           memory=None,
                           ):
    
    callback_manager = CallbackManager([StdOutCallbackHandler()])
    
    llm = create_llm(source=source,
                     api_key=api_key,
                     model=model,
                     base_url=base_url,
                     temperature=temperature,
                     callback_manager=callback_manager)
    
    runnable = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory.load_memory_variables)| itemgetter("chat_history")  # memory_key 와 동일하게 입력합니다.
        )
    
    class AIThink(BaseModel):
        '''모델 추론 결과
        Respond to Korean.
        '''
        THOUGHT: str = Field(..., title="사용자의 질문에 처음 모델이 생각한 내용")
    parser = PydanticOutputParser(pydantic_object=AIThink)
    
    think_prompt = get_thinking_NoDoc_prompt(parser)
    prompt = get_thinking_NoDoc_chatbot()
    
    think_chain = runnable|think_prompt|llm|parser
    answer_chain = prompt|llm
    
    def get_thought(output):
        return output["thought"].THOUGHT
    
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
            "input" : RunnablePassthrough()
        }|
        {
            "thought":RunnablePassthrough(),
            "answer":answer_chain
        }
        |RunnableLambda(output_formatter)
        )
    
    return final_chain

def thought_chatbot_chain(instruct_prompt:str,
                  thought_prompt:str,
                  api_key:str,
                  source:str,
                  model:str='gpt-4o-mini',
                  base_url:str='http://localhost:11434',
                  temperature:float=0.1,
                  callback_manager=None,
                  memory=None,
                  document_meta=None,
                  retriever=None,
                  ):
    
    callback_manager = CallbackManager([StdOutCallbackHandler()])
    
    llm = create_llm(source=source,
                     api_key=api_key,
                     model=model,
                     base_url=base_url,
                     temperature=temperature,
                     callback_manager=callback_manager)
    
    runnable = RunnablePassthrough.assign(
        memory_vars=RunnableLambda(memory.load_memory_variables)
    ).assign(
        long_term=lambda x: x["memory_vars"]["long_term"],
        recent_chat=lambda x: x["memory_vars"]["recent_chat"]
    )
    
    think_prompt = create_thinking_prompt(thought_prompt=thought_prompt,
                                          document_meta=document_meta,
                                          pydantic_parser=think_parser)
    prompt = create_thinking_chatbot_prompt(instruct_prompt=instruct_prompt)
    
    think_chain = think_prompt|llm|think_parser
    answer_chain = prompt|llm
    rerank_chain = map_rerank_chain(llm)
    
    def get_thought(output):
        try :
            return output.get("thought").THOUGHT
        except Exception as e:
            print(e)
            return "사고 과정 오류"
    
    def get_document(output):
        if retriever:
            try :
                thought = output.get("thought")
                rtn = f"**검색어: {thought.search_msg}**\n"
                
                docs = retriever.invoke(thought.search_msg)
                inputs = []
                for doc in docs:
                    inputs.append({"input":thought.search_msg,"context": doc.page_content})
                
                results = rerank_chain.batch(inputs,
                                            config={"max_concurrency": 3},)

                final_idx=[]
                for result in results:
                    if result.score >= 8:
                        final_idx.append(results.index(result))
                
                if len(final_idx) == 0:
                    rtn += "해당 문서 없음"
                    return rtn
                else :
                    rtn += f"**총 문서 수**: {len(final_idx)}\n"
                    for idx in final_idx:
                        rtn+=f"---------*Doc No.{idx}*---------\n"
                        rtn+=f"**검색 문서 적합 점수(10점 만점)**: {results[idx].score}점\n"
                        rtn+=f"**측정 사유**:{results[idx].evaluation_reasons}\n"
                        rtn+=f"```검색결과\n"
                        rtn+=docs[idx].page_content + "\n"
                        rtn+=f"```\n"
                
                return rtn
            except Exception as e:
                print(e)
                return "**문서 검색오류**"
        else:
            return ""
        
    def output_formatter(output):
        return {
            "params": output.get("params"),
            "answer": output.get("answer"),
        }
        
    final_chain = (
        RunnableParallel(
            input = RunnablePassthrough(),
            chat_history= runnable,
            document = RunnableLambda(get_document),
        )
        |{
            "input": lambda x: x["input"],
            "long_term": lambda x: x["chat_history"]["memory_vars"].get("long_term"),
            "recent_chat": lambda x: x["chat_history"]["memory_vars"].get("recent_chat"),
            "document": lambda x: x["document"]
        }|{
            "input" : RunnablePassthrough(),
            "thought" : think_chain
        }
        |{
            "thought":RunnableLambda(get_thought),
            "document":RunnableLambda(get_document),
            "input" : RunnablePassthrough()
        }|
        {
            "params":RunnablePassthrough(),
            "answer":answer_chain
        }
        |RunnableLambda(output_formatter)
        )
    
    return final_chain

def chatbot_chain(instruct_prompt:str,
                  api_key:str,
                  source:str,
                  model:str='gpt-4o-mini',
                  base_url:str='http://localhost:11434',
                  temperature:float=0.1,
                  retriever_score:float=7,
                  callbacks=None,
                  memory=None,
                  retriever=None,
                  ):
    
    callback_manager = CallbackManager(callbacks)
    llm = create_llm(source=source,
                     api_key=api_key,
                     model=model,
                     base_url=base_url,
                     temperature=temperature,
                     callback_manager=callback_manager)
    
    runnable = RunnablePassthrough.assign(
        memory_vars=RunnableLambda(memory.load_memory_variables)
    ).assign(
        long_term=lambda x: x["memory_vars"]["long_term"],
        recent_chat=lambda x: x["memory_vars"]["recent_chat"]
    )
    
    prompt = create_chatbot_prompt(instruct_prompt=instruct_prompt)
    
    answer_chain = prompt|llm
    rerank_chain = map_rerank_chain(llm)
    
    def get_document(output):
        if retriever:
            try :
                search_msg  = output.get("thought",output.get("input"))
                rtn = f"**검색어: {search_msg}**\n"
                
                docs = retriever.invoke(search_msg)
                inputs = []
                for doc in docs:
                    inputs.append({"input":search_msg,"context": doc.page_content})
                
                results = rerank_chain.batch(inputs,
                                            config={"max_concurrency": 3},)

                final_idx=[]
                for result in results:
                    if result.score >= retriever_score:
                        final_idx.append(results.index(result))
                
                if len(final_idx) == 0:
                    rtn += "해당 문서 없음"
                    return rtn
                else :
                    rtn += f"**총 문서 수**: {len(final_idx)}\n"
                    for idx in final_idx:
                        rtn+=f"---------*Doc No.{idx}*---------\n"
                        rtn+=f"**검색 문서 적합 점수(10점 만점)**: {results[idx].score}점\n"
                        rtn+=f"**측정 사유**:{results[idx].evaluation_reasons}\n"
                        rtn+=f"```검색결과\n"
                        rtn+=docs[idx].page_content + "\n"
                        rtn+=f"```\n"
                
                return rtn
            except Exception as e:
                print(e)
                return "**문서 검색오류**"
        else:
            return ""
        
    def output_formatter(output):
        return {
            "answer": output.get("answer"),
            "params": output.get("params"),
        }
        
    def debug(output):
        print(output)
        return output
        
    final_chain = (
        RunnableParallel(
            input = RunnablePassthrough(),
            chat_history= runnable,
            document = RunnableLambda(get_document)
        )
        |{
            "input": lambda x: x["input"],
            "long_term": lambda x: x["chat_history"]["memory_vars"].get("long_term"),
            "recent_chat": lambda x: x["chat_history"]["memory_vars"].get("recent_chat"),
            "document": lambda x: x["document"]
        }
        |{
            "params":RunnablePassthrough(),
            "answer":answer_chain
        }
        # |RunnableLambda(output_formatter)
        )
    
    return final_chain