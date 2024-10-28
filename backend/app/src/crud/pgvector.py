from typing import List
import uuid
from app.src.schemas import pgvector as pgvector_schema
from sqlmodel import Session, select, union_all
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_postgres.vectorstores import _get_embedding_collection_store 


async def get_collection(*, session: AsyncSession,collection_id:uuid.UUID) -> pgvector_schema.get_collection:
    try:
        EmbeddingStore, CollectionStore = _get_embedding_collection_store()
        statement = select(CollectionStore).where(CollectionStore.uuid == collection_id)
        collection = await session.exec(statement)
        if not collection:
            return None
        else:
            return collection.first()
    except Exception as e:
        print(e)
        await session.rollback()
        raise e
        