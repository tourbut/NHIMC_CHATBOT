from typing import AsyncIterable, AsyncIterator, Dict, Iterator, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatPerplexity

from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda, RunnablePassthrough,RunnableParallel,RunnableGenerator
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from operator import itemgetter

from ..common.prompt import (
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
               format:str='',
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
                         format = format,
                         #num_thread=8, # CPU 스레드 수 지정 
                         )
    elif source == 'perplexity':
        llm = ChatPerplexity(model=model,
                             temperature=temperature,
                             api_key=api_key,
                             callback_manager=callback_manager)
    else:
        raise ValueError(f"Invalid model name: {model}")
    
    return llm

def map_rerank_chain(llm,document_meta=None):
    
    class AnswerEvaluation(BaseModel):
        """Model for evaluating search result quality"""
        
        score: float = Field(
            ..., 
            title="Score",
            description="Quality score of search results (1.0-10.0)",
            ge=1.0,
            le=10.0
        )
        
        evaluation_reasons: str = Field(
            ...,
            title="Evaluation Reasons",
            description="Detailed breakdown of scoring components (e.g., +4 for keywords, -1 for irrelevant content).",
        )
    
    parser = PydanticOutputParser(pydantic_object=AnswerEvaluation)

    prompt_template = """
<SYSTEM>
You are an expert evaluator tasked with assessing how well the provided context answers the given question.
Your evaluation must be objective and based on the criteria below:

9.0~10.0: Fully answers the question with comprehensive and rich supporting data.
7.0~8.9: Provides a core answer but lacks additional supporting information.
5.0~6.9: Relevant but incomplete answer.
3.0~4.9: Contains only indirect relevance.
1.0~2.9: Completely irrelevant or incorrect.

Respond to Korean.
</SYSTEM>

<DOCUMENT_META>
{document_meta}
</DOCUMENT_META>

<CONTEXT>
{context}
</CONTEXT>

<QUESTION>
{input}
</QUESTION>

<OUTPUT FORMAT>
{format_instructions}
</OUTPUT FORMAT>

<EVALUATION RULES>
1. Begin scoring at a base of 5.0 if the context contains any relevant information.
2. Add up to +4 points for keyword matches between the context and the question.
3. Add +2 points for specific examples or detailed data provided in the context.
4. Deduct -1 point for irrelevant content or minor inconsistencies.
5. Deduct -2 points for major logical errors or lack of structure.

Provide a detailed breakdown of how each scoring component contributed to the final score (e.g., "+4 for keywords, -1 for irrelevant content").
</EVALUATION RULES>
"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions(),
                           "document_meta": document_meta},
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
                  callbacks=None,
                  memory=None,
                  document_meta=None,
                  retriever=None,
                  retriever_score:float=7,
                  allow_doc_num:int=3,
                  ):
    
    if callbacks is None:
        callback_manager = CallbackManager([StdOutCallbackHandler()])
    else:
        callback_manager = CallbackManager(callbacks)
    
    llm = create_llm(source=source,
                     api_key=api_key,
                     model=model,
                     base_url=base_url,
                     temperature=temperature,
                     callback_manager=callback_manager)
    rerank_llm = create_llm(source='ollama',
                        model=settings.GLOBAL_LLM,
                        api_key=settings.GLOBAL_LLM_API,
                        base_url=settings.GLOBAL_LLM_URL,
                        temperature=0.2,
                        )
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
    rerank_chain = map_rerank_chain(rerank_llm,document_meta)
    
    def get_thought(output):
        try :
            return output.get("thought").THOUGHT
        except Exception as e:
            print(e)
            return "사고 과정 오류"
    
    async def search_docs(output):
        if retriever:
            try :
                if output.get("thought"):
                    search_msg  = output.get("thought").search_msg
                else:
                    search_msg  = output.get("input")
                                    
                docs = retriever.invoke(search_msg)
                return docs
            except Exception as e:
                print(e)
                return "**문서 검색오류**"
        else:
            return "해당 문서 없음"
    
    async def rerank_document(input: AsyncIterator[Dict]) -> AsyncIterator[str]:
        search_msg =  ""
        docs = []
        
        async for chunk in input:
            search_msg =  chunk.get("search_msg",search_msg)
            docs = chunk.get('docs',docs)
            
        result_message = f"**검색어: {search_msg}**\n"
        
        if docs != "해당 문서 없음" and len(docs) > 0 and search_msg != "": 
            try:
                results = []
                for idx, doc in enumerate(docs):
                    tmp_result_message = f"## 검색 문서 평가 중 (문서 순번:{idx})\n"
                    tmp_result_message += f"```검색결과\n{doc.page_content}```\n" 
                    yield tmp_result_message
                    
                    result = rerank_chain.invoke({"input": search_msg, "context": doc.page_content})
                    #중간 결과 출력
                    tmp_result_message += f"**검색어**: {search_msg}\n"
                    tmp_result_message += f"**검색 문서 적합 점수(10점 만점)**: {result.score}점\n"
                    tmp_result_message += f"**측정 사유**: {result.evaluation_reasons}\n"
                    tmp_result_message += f"```검색결과\n{doc.page_content}```\n" 
                    yield tmp_result_message
                    
                    results.append(result)
                    
                valid_indices = [i for i, result in enumerate(results) if result.score >= retriever_score]

                if not valid_indices:
                    result_message += "해당 문서 없음"
                    yield result_message
                else:
                    top_documents = get_top_documents(results, valid_indices, docs, allow_doc_num)
                    result_message += format_documents(top_documents, len(docs))
                    yield result_message
            except Exception as e:
                yield f"문서 평가 중 오류 발생: {e}"
        elif docs == "해당 문서 없음":
            result_message += docs
            yield result_message
        else:
            yield result_message + "해당 문서 없음"

    def get_top_documents(results, valid_indices, docs, allow_doc_num):
        final_docs = [
            {
                "score": results[idx].score,
                "content": f"--------------------------------------------\n"
                        f"**검색 문서 적합 점수(10점 만점)**: {results[idx].score}점\n"
                        f"**측정 사유**: {results[idx].evaluation_reasons}\n"
                        f"```검색결과\n{docs[idx].page_content}```\n"
            }
            for idx in valid_indices
        ]
        return sorted(final_docs, key=lambda x: x["score"], reverse=True)[:allow_doc_num]

    def format_documents(top_documents, total_docs):
        result_message = f"**문서 수**: {len(top_documents)} (총 검색문서: {total_docs})\n"
        for i, doc in enumerate(top_documents, start=1):
            result_message += f"---------*Doc No.{i}*---------\n{doc['content']}"
        return result_message                
    
    runnable_document = RunnableGenerator(rerank_document)
        
    def output_formatter(output):
        return {
            "params": output.get("params"),
            "answer": output.get("answer"),
        }
        
    final_chain = (
        RunnableParallel(
            input = RunnablePassthrough(),
            chat_history= runnable,
        )
        |{
            "input": lambda x: x["input"],
            "long_term": lambda x: x["chat_history"]["memory_vars"].get("long_term"),
            "recent_chat": lambda x: x["chat_history"]["memory_vars"].get("recent_chat"),
        }|{
            "input" : RunnablePassthrough(),
            "thought" : think_chain
        }
        |{
            "thought":RunnableLambda(get_thought),
            "docs":search_docs,
            "input" : RunnablePassthrough(),
            "search_msg" : lambda x: x["thought"].search_msg
        }|
        {
            "thought": lambda x: x["thought"],
            "document":runnable_document,
            "input" : lambda x: x["input"]
        }|
        {
            "params":RunnablePassthrough(),
            "answer":answer_chain
        }
        )
    
    return final_chain

def chatbot_chain(instruct_prompt:str,
                  api_key:str,
                  source:str,
                  model:str='gpt-4o-mini',
                  base_url:str='http://localhost:11434',
                  temperature:float=0.1,
                  callbacks=None,
                  memory=None,
                  document_meta=None,
                  retriever=None,
                  retriever_score:float=7,
                  allow_doc_num:int=3,
                  ):
    if callbacks is None:
        callback_manager = CallbackManager([StdOutCallbackHandler()])
    else:
        callback_manager = CallbackManager(callbacks)
    llm = create_llm(source=source,
                     api_key=api_key,
                     model=model,
                     base_url=base_url,
                     temperature=temperature,
                     callback_manager=callback_manager)
    
    rerank_llm = create_llm(source='ollama',
                         model=settings.GLOBAL_LLM,
                         api_key=settings.GLOBAL_LLM_API,
                         base_url=settings.GLOBAL_LLM_URL,
                         temperature=0.2,
                         )
    
    runnable = RunnablePassthrough.assign(
        memory_vars=RunnableLambda(memory.load_memory_variables)
    ).assign(
        long_term=lambda x: x["memory_vars"]["long_term"],
        recent_chat=lambda x: x["memory_vars"]["recent_chat"]
    )
    
    prompt = create_chatbot_prompt(instruct_prompt=instruct_prompt)
    
    answer_chain = prompt|llm
    rerank_chain = map_rerank_chain(rerank_llm,document_meta)
        
    async def search_docs(output):
        if retriever:
            try :
                if output.get("thought"):
                    search_msg  = output.get("thought").search_msg
                else:
                    search_msg  = output.get("input")
                                    
                docs = retriever.invoke(search_msg)
                return docs
            except Exception as e:
                print(e)
                return "**문서 검색오류**"
        else:
            return "해당 문서 없음"
    
    async def rerank_document(input: AsyncIterator[Dict]) -> AsyncIterator[str]:
        search_msg =  ""
        docs = []
        
        async for chunk in input:
            search_msg =  chunk.get("search_msg",search_msg)
            docs = chunk.get('docs',docs)
            
        result_message = f"**검색어: {search_msg}**\n"
        
        if docs != "해당 문서 없음" and len(docs) > 0 and search_msg != "": 
            try:
                results = []
                
                for idx, doc in enumerate(docs):
                    tmp_result_message = f"## 검색 문서 평가 중 (문서 순번:{idx})\n"
                    tmp_result_message += f"```검색결과\n{doc.page_content}```\n" 
                    yield tmp_result_message
                    
                    result = rerank_chain.invoke({"input": search_msg, "context": doc.page_content})
                    #중간 결과 출력
                    tmp_result_message = f"## 검색 문서 평가 중 (문서 순번:{idx})\n"
                    tmp_result_message += f"**검색어**: {search_msg}\n"
                    tmp_result_message += f"**검색 문서 적합 점수(10점 만점)**: {result.score}점\n"
                    tmp_result_message += f"**측정 사유**: {result.evaluation_reasons}\n"
                    tmp_result_message += f"```검색결과\n{doc.page_content}```\n" 
                    yield tmp_result_message
                    
                    results.append(result)
                    
                valid_indices = [i for i, result in enumerate(results) if result.score >= retriever_score]

                if not valid_indices:
                    result_message += "최종 해당 문서 없음"
                    yield result_message
                else:
                    top_documents = get_top_documents(results, valid_indices, docs, allow_doc_num)
                    result_message += format_documents(top_documents, len(docs))
                    yield result_message
            except Exception as e:
                yield f"문서 평가 중 오류 발생: {e}"
        elif docs == "해당 문서 없음":
            result_message += docs
            yield result_message
        else:
            yield result_message + "해당 문서 없음"

    def get_top_documents(results, valid_indices, docs, allow_doc_num):
        final_docs = [
            {
                "score": results[idx].score,
                "content": f"--------------------------------------------\n"
                        f"**검색 문서 적합 점수(10점 만점)**: {results[idx].score}점\n"
                        f"**측정 사유**: {results[idx].evaluation_reasons}\n"
                        f"```검색결과\n{docs[idx].page_content}```\n"
            }
            for idx in valid_indices
        ]
        return sorted(final_docs, key=lambda x: x["score"], reverse=True)[:allow_doc_num]

    def format_documents(top_documents, total_docs):
        result_message = f"**문서 수**: {len(top_documents)} (총 검색문서: {total_docs})\n"
        for i, doc in enumerate(top_documents, start=1):
            result_message += f"---------*Doc No.{i}*---------\n{doc['content']}"
        return result_message                
    
    runnable_document = RunnableGenerator(rerank_document)
                

    final_chain = (
        RunnableParallel(
            input = RunnablePassthrough(),
            chat_history= runnable,
            docs=search_docs,
            search_msg = lambda x: x["input"]
        )
        |{
            "input": lambda x: x["input"],
            "long_term": lambda x: x["chat_history"]["memory_vars"].get("long_term"),
            "recent_chat": lambda x: x["chat_history"]["memory_vars"].get("recent_chat"),
            "document":runnable_document
        }
        |{
            "params":RunnablePassthrough(),
            "answer":answer_chain
        }
        )
    
    return final_chain