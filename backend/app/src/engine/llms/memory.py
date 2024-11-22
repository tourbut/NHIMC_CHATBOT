from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.memory import VectorStoreRetrieverMemory
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
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