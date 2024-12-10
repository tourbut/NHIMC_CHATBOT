from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.memory import VectorStoreRetrieverMemory
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter 
from langchain.storage._lc_store import create_kv_docstore
from langchain_community.storage import SQLStore, RedisStore
from ....core.config import settings

def pg_vetorstore(connection,
                  collection_name:str,
                  api_key:str,
                  source:str,
                  model:str='text-embedding-3-large',
                  async_mode=False):

    if source == 'openai':
        embeddings = OpenAIEmbeddings(model=model,
                                    api_key=api_key)
    elif source == 'ollama':
        embeddings = OllamaEmbeddings(model=model,base_url=settings.OLLAMA_URL)
        
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
                  async_mode=False,
                  splitter_options:dict={"separators":["\n\n"],"chunk_size":2000,"chunk_overlap":500,
                                                       "child_chunk_size":200,"child_chunk_overlap":50}):
    
    vectorstore = pg_vetorstore(connection=connection,
                                collection_name=collection_name,
                                api_key=api_key,
                                source=source,
                                model=model,
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
        search_kwargs={"k": 3, "lambda": 0.3}
    )
    
    return retriever

def pg_vetorstore_with_memory(connection,
                  collection_name:str,
                  api_key:str,
                  source:str='openai',
                  model:str='text-embedding-3-large',
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
                                async_mode=async_mode
                                )
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    memory = VectorStoreRetrieverMemory(retriever=retriever,
                                        memory_key="chat_history",
                                        return_messages=True,
                                        return_docs=False,)
    
    return memory