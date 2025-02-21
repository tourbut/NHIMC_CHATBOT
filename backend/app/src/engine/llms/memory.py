from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.memory import VectorStoreRetrieverMemory,CombinedMemory,ConversationBufferWindowMemory
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter 
from langchain.storage._lc_store import create_kv_docstore
from langchain_community.storage import SQLStore, RedisStore

def pg_vetorstore(connection,
                  collection_name:str,
                  api_key:str,
                  source:str,
                  model:str='text-embedding-3-large',
                  base_url:str='http://localhost:11434',
                  async_mode=False):

    if source == 'openai':
        embeddings = OpenAIEmbeddings(model=model,
                                    api_key=api_key)
    elif source == 'ollama':
        embeddings = OllamaEmbeddings(model=model,
                                      base_url=base_url)
        
    vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
    async_mode=async_mode,
    )
    
    return vectorstore

def pg_ParentDocumentRetriever(connection,
                  collection_name:str,
                  api_key:str,
                  source:str,
                  model:str='text-embedding-3-large',
                  base_url:str='http://localhost:11434',
                  async_mode=False,
                  splitter_options:dict={"separators":["\n\n"],"chunk_size":2000,"chunk_overlap":500,
                                                       "child_chunk_size":200,"child_chunk_overlap":50}):
    
    vectorstore = pg_vetorstore(connection=connection,
                                collection_name=collection_name,
                                api_key=api_key,
                                source=source,
                                model=model,
                                base_url=base_url,
                                async_mode=async_mode
                                )
    postgre = SQLStore(namespace=collection_name, engine=connection)
    store = create_kv_docstore(postgre)
    
    parent_splitter = RecursiveCharacterTextSplitter(
    separators=splitter_options['separators'],
    chunk_size=splitter_options['chunk_size'],
    chunk_overlap=splitter_options['chunk_overlap'],
    length_function=len,
    )
    
    child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=splitter_options['child_chunk_size'],
    chunk_overlap=splitter_options['child_chunk_overlap'],
    length_function=len,
    )
    
    # Retriever 를 생성합니다.
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        parent_splitter=parent_splitter,
        child_splitter=child_splitter,
        #search_type="similarity_score_threshold",
        #search_kwargs={"score_threshold": 0.6}
        search_type="mmr",
        search_kwargs={"k": 6, "lambda": 0.2}
    )
    
    return retriever

from typing import Dict, Any

class FilteredCombinedMemory(CombinedMemory):
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # 기본 메모리 변수 로드
        memory_data = super().load_memory_variables(inputs)
        
        # 벡터 스토어에서 가져온 기록
        vector_history = memory_data.get("long_term", "")
        # 최근 대화 기록
        recent_chat = memory_data.get("recent_chat", "")
        
        # 벡터 스토어 결과에서 최근 대화 내용 제거
        for chat in recent_chat.split('\n'):
            if chat in vector_history:
                vector_history = vector_history.replace(chat, "")
                
        memory_data["long_term"] = vector_history.strip()
        return memory_data

class CustomBufferWindowMemory(ConversationBufferWindowMemory):
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Override save_context to skip adding to chat_memory"""
        # chat_memory에 저장하지 않고 내부 버퍼만 업데이트
        return None

def pg_vetorstore_with_memory(connection,
                  collection_name:str,
                  api_key:str,
                  chat_memory = None,
                  source:str='openai',
                  model:str='text-embedding-3-large',
                  base_url:str='http://localhost:11434',
                  search_kwargs={"k": 3},
                  ):
    
    if type(connection) is Engine:
        async_mode=False
    elif type(connection) is AsyncEngine:
        async_mode=True
    
    vectorstore = pg_vetorstore(connection=connection,
                                collection_name=collection_name,
                                api_key=api_key,
                                source=source,
                                model=model,
                                base_url=base_url,
                                async_mode=async_mode
                                )
    
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    vector_memory = VectorStoreRetrieverMemory(retriever=retriever,
                                        memory_key="long_term",
                                        return_messages=True,
                                        return_docs=False,)
    # 최근 대화 버퍼 메모리 설정
    buffer_memory = CustomBufferWindowMemory(
        k=3,  # 최근 3개의 대화 유지
        memory_key="recent_chat",
        chat_memory=chat_memory,
    )
    
    combined_memory = FilteredCombinedMemory(
    memories=[vector_memory, buffer_memory]
    )
    
    return combined_memory

def clear_memory(connection,
                  collection_name:str,
                  api_key:str,
                  source:str='openai',
                  model:str='text-embedding-3-large',
                  base_url:str='http://localhost:11434',):
    
    try:
    
        if type(connection) is Engine:
            async_mode=False
        elif type(connection) is AsyncEngine:
            async_mode=True
            
        vectorstore = pg_vetorstore(connection=connection,
                                    collection_name=collection_name,
                                    api_key=api_key,
                                    source=source,
                                    model=model,
                                    base_url=base_url,
                                    async_mode=async_mode
                                    )
        
        vectorstore.delete_collection()[1]
        
        return True
    
    except Exception as e:
        print(e)
        return False