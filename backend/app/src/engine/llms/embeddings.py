from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import CacheBackedEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import TextLoader, PDFMinerLoader, UnstructuredExcelLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from sqlmodel import Session

async def load_and_split(file_ext:str,file_path: str,
                         splitter_options:dict={"separator":"\n","chunk_size":600,"chunk_overlap":100}):
    character_text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    separator=splitter_options["separator"],
    chunk_size=splitter_options["chunk_size"],
    chunk_overlap=splitter_options["chunk_size"],
    )
    
    if file_ext in ['txt','md']:
        loader = TextLoader(file_path)
    elif file_ext in ['pdf']:
        loader = PDFMinerLoader(file_path)
    elif file_ext in ['csv']:
        loader = CSVLoader(file_path)
    elif file_ext in ['xls','xlsx']:
        loader = UnstructuredExcelLoader(file_path)
    else:
        raise ValueError("File extension not supported")
        
    docs = loader.load_and_split(text_splitter=character_text_splitter)
    return docs


async def embedding_and_store(docs, connection, 
                        collection_name:str, 
                        api_key:str, 
                        model:str='text-embedding-3-large',
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
    
    embeddings = OpenAIEmbeddings(model=model,api_key=api_key)
    
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