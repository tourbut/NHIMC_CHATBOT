from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter 
from langchain.embeddings import CacheBackedEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_postgres.vectorstores import PGVector
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain.storage import LocalFileStore
from langchain_community.storage import SQLStore, RedisStore
from langchain.storage._lc_store import create_kv_docstore
from langchain.retrievers import ParentDocumentRetriever
from langchain_community.document_loaders import TextLoader, PDFMinerLoader, UnstructuredExcelLoader,UnstructuredPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from sqlmodel import Session
import chardet

from ....core.config import settings

async def load(file_ext:str,file_path: str):
    try :
        if file_ext in ['txt','md']:
            def detect_encoding(file_path: str) -> str:
                with open(file_path, 'rb') as f:
                    result = chardet.detect(f.read())
                return result['encoding']
            loader = TextLoader(file_path,encoding=detect_encoding(file_path))
        elif file_ext in ['pdf']:
            loader = PDFMinerLoader(file_path)
        elif file_ext in ['csv']:
            loader = CSVLoader(file_path)
        elif file_ext in ['xls','xlsx']:
            loader = UnstructuredExcelLoader(file_path)
        else:
            raise ValueError("File extension not supported")

        docs = loader.load()
    except Exception as e:
        print(e)
        raise ValueError("Document loading failed")
    
    return docs

async def load_and_split(file_ext:str,file_path: str,
                         splitter_options:dict={"separators":["\n\n"],"chunk_size":2000,"chunk_overlap":500}):
    
    character_text_splitter = RecursiveCharacterTextSplitter(
    separators=splitter_options["separators"],
    chunk_size=splitter_options["chunk_size"],
    chunk_overlap=splitter_options["chunk_overlap"],
    )
    try :
        if file_ext in ['txt','md']:
            def detect_encoding(file_path: str) -> str:
                with open(file_path, 'rb') as f:
                    result = chardet.detect(f.read())
                return result['encoding']
            loader = TextLoader(file_path,encoding=detect_encoding(file_path))
        elif file_ext in ['pdf']:
            loader = PDFMinerLoader(file_path)
        elif file_ext in ['csv']:
            loader = CSVLoader(file_path)
        elif file_ext in ['xls','xlsx']:
            loader = UnstructuredExcelLoader(file_path)
        else:
            raise ValueError("File extension not supported")

        docs = loader.load_and_split(text_splitter=character_text_splitter)
    except Exception as e:
        print(e)
        raise ValueError("Document loading failed")
    
    return docs


async def embedding_and_store(docs, connection, 
                        collection_name:str, 
                        api_key:str=settings.GLOBAL_EMBEDDING_API, 
                        source:str=settings.GLOBAL_EMBEDDING_SOURCE,
                        model:str=settings.GLOBAL_EMBEDDING_MODEL,
                        base_url:str=settings.GLOBAL_EMBEDDING_URL,
                        cache_dir:str='./.cache',
                        collection_metadata:dict={}):
    
    def num_tokens_from_text(text: str, encoding_name: str = "cl100k_base") :
        try :
            from tiktoken import get_encoding
        except ImportError :
            return "Please install tiktoken package"
        
        encoding = get_encoding(encoding_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens

    def check_cache_status(store):
        cached_keys = list(store.yield_keys())
        return set(cached_keys)
    
    if source == 'openai':
        embeddings = OpenAIEmbeddings(model=model,api_key=api_key)
    elif source == 'ollama':
        embeddings = OllamaEmbeddings(model=model,base_url=base_url)
        
    cache_store = LocalFileStore(cache_dir)
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings,cache_store)
    
    if type(connection) is Engine:
        async_mode=False
    elif type(connection) is AsyncEngine:
        async_mode=True
    else:
        raise ValueError("connection must be either Engine or AsyncEngine")
        
    vectorstore = PGVector(embeddings=cached_embeddings,
                           collection_name=collection_name,
                           connection=connection,
                           use_jsonb=True,
                           async_mode=async_mode,
                           collection_metadata=collection_metadata
                           )
    
    before_keys = check_cache_status(cache_store)
    
    if async_mode:
        await vectorstore.aadd_documents(documents=docs)
    else:
        vectorstore.add_documents(documents=docs)
        
    after_keys = check_cache_status(cache_store)
    
    new_embeddings = after_keys - before_keys
    
    total_tokens = 0
    
    if len(new_embeddings) > 0:
        total_tokens = sum(num_tokens_from_text(text = doc.page_content,encoding_name = "cl100k_base") for doc in docs)
        
    with Session(connection) as session:
        collection = vectorstore.get_collection(session=session)
    
    return collection, total_tokens


async def create_ParentDocument(docs,
                                connection, 
                                collection_name:str, 
                                api_key:str=settings.GLOBAL_EMBEDDING_API, 
                                source:str=settings.GLOBAL_EMBEDDING_SOURCE,
                                model:str=settings.GLOBAL_EMBEDDING_MODEL,
                                base_url:str=settings.GLOBAL_EMBEDDING_URL,
                                cache_dir:str='./.cache',
                                collection_metadata:dict={},
                                splitter_options:dict={"separators":["\n\n"],"chunk_size":2000,"chunk_overlap":500,
                                                       "child_chunk_size":200,"child_chunk_overlap":50}):
    
    def num_tokens_from_text(text: str, encoding_name: str = "cl100k_base") :
        try :
            from tiktoken import get_encoding
        except ImportError :
            return "Please install tiktoken package"
        
        encoding = get_encoding(encoding_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens

    def check_cache_status(store):
        cached_keys = list(store.yield_keys())
        return set(cached_keys)
    
    if source == 'openai':
        embeddings = OpenAIEmbeddings(model=model,api_key=api_key)
    elif source == 'ollama':
        embeddings = OllamaEmbeddings(model=model,base_url=base_url)
        
    cache_store = LocalFileStore(cache_dir)
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings,cache_store)
    
    if type(connection) is Engine:
        async_mode=False
    elif type(connection) is AsyncEngine:
        async_mode=True
    else:
        raise ValueError("connection must be either Engine or AsyncEngine")
        
    vectorstore = PGVector(embeddings=cached_embeddings,
                           collection_name=collection_name,
                           connection=connection,
                           use_jsonb=True,
                           async_mode=async_mode,
                           collection_metadata=collection_metadata
                           )
    
    before_keys = check_cache_status(cache_store)
    
    postgre = SQLStore(namespace=collection_name, engine=connection)
    
    def check_table_exists(engine, table_name):
        from sqlmodel import inspect
        inspector = inspect(engine)
        return inspector.has_table(table_name)
    
    if not check_table_exists(connection, "langchain_key_value_stores"):
        print("Creating schema")
        postgre.create_schema()
        
    store = create_kv_docstore(postgre)
    
    parent_splitter = RecursiveCharacterTextSplitter(
    separators=splitter_options['separators'],
    chunk_size=splitter_options['chunk_size'],
    chunk_overlap=splitter_options['chunk_overlap'],
    length_function=len,
    )
    
    child_splitter = RecursiveCharacterTextSplitter(
    #separators=splitter_options['separators'],
    chunk_size=splitter_options['child_chunk_size'],
    chunk_overlap=splitter_options['child_chunk_overlap'],
    length_function=len,
    )
    
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        parent_splitter=parent_splitter,
        child_splitter=child_splitter,
    )
    
    if async_mode:
        await retriever.aadd_documents(docs, ids=None, add_to_docstore=True)
    else:
        retriever.add_documents(docs, ids=None, add_to_docstore=True)
        
    after_keys = check_cache_status(cache_store)
    
    new_embeddings = after_keys - before_keys
    
    total_tokens = 0
    
    if len(new_embeddings) > 0:
        total_tokens = sum(num_tokens_from_text(text = doc.page_content,encoding_name = "cl100k_base") for doc in docs)
        
    with Session(connection) as session:
        collection = vectorstore.get_collection(session=session)
    
    return collection, total_tokens
