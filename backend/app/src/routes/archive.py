import uuid
import io
from typing import Any,List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse,StreamingResponse

from app.src.deps import SessionDep_async,CurrentUser,engine
from app.src.crud import archive as archive_crud
from app.src.schemas import archive as archive_schema

from app.core.config import settings
from app.src.engine.llms.chain import translate_chain,summarize_chain
from app.src.engine.llms.embeddings import load_and_split,embedding_and_store

from requests.exceptions import RequestException

from tempfile import NamedTemporaryFile
from typing import IO

from fastapi import FastAPI, File, UploadFile
import os

router = APIRouter()

async def save_file(file: IO,user_id:uuid.UUID) -> str:
    
    user_file_path = f"{settings.FILE_UPLOAD_DIR}/{str(user_id)}"
    
    if not os.path.exists(user_file_path):
        os.makedirs(user_file_path)
        
    with NamedTemporaryFile("wb", delete=False,dir=user_file_path) as tempfile:
        tempfile.write(file.read())
        return tempfile.name,user_file_path 

@router.post("/upload_flies/",response_model=archive_schema.ResponseFile)
async def upload_flies(*, session: SessionDep_async, current_user: CurrentUser,file: UploadFile):
    try:
        # Get userllm
        userllm = await archive_crud.get_userllm(session=session,user_id=current_user.id,llm_type='embedding')
        
        # Save file and load and split
        path,userdir_path = await save_file(file.file,user_id=current_user.id)
        file_meta = archive_schema.FileUpload(file_name=file.filename,
                                              file_path=path,
                                              file_size=os.path.getsize(path),
                                              file_type=file.content_type,
                                              file_ext=file.filename.split(".")[-1])
        
        db_obj = await archive_crud.create_file(session=session,file=file_meta,user_id=current_user.id)
        docs = await load_and_split(file_ext=file.filename.split(".")[-1],file_path=path)
        
        # Embedding and store
        collection_metadata = {"file_name":file_meta.file_name,
                               "file_size":file_meta.file_size,
                               "file_ext":file_meta.file_ext,
                               "file_desc":file_meta.file_desc}
        
        vectorstore,used_tokens = await embedding_and_store(docs=docs,
                                                connection=engine,
                                                collection_name=db_obj.id.hex, #Userfiles의 ID
                                                api_key=userllm.api_key,
                                                model=userllm.name,
                                                cache_dir=f"{userdir_path}/.cache",
                                                collection_metadata=collection_metadata)
        
        
        db_obj.embedding_yn = True
        db_obj.embedding_model_id = userllm.llm_id
        db_obj.collection_id = vectorstore.uuid
        
        await archive_crud.update_file(session=session,file=db_obj)

        # Return response
        async def get_contents(docs):
            contents = [doc.page_content for doc in docs]
            return contents
        
        contents = await get_contents(docs)   
        response = archive_schema.ResponseFile(id=db_obj.id,
                                               file_name=file_meta.file_name,
                                               file_size=file_meta.file_size,
                                               file_ext=file_meta.file_ext,
                                               file_desc=file_meta.file_desc,
                                               contents=contents)
        
        # Save usage
        if used_tokens > 0:
            embedding_usage = archive_schema.Usage(user_llm_id=userllm.id,
                                                   input_token=used_tokens,
                                                   output_token=0)
            await archive_crud.create_usage(session=session,usage=embedding_usage)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"파일 업로드에 실패하였습니다.")
    
    return response

@router.get("/get_file/{file_id}", response_model=archive_schema.ResponseFile)
async def get_file(*, session: SessionDep_async, current_user: CurrentUser,file_id:uuid.UUID) -> Any:
    
    try:
        rst_file = await archive_crud.get_file(session=session,file_id=file_id)
        docs = await load_and_split(file_ext=rst_file.file_ext,file_path=rst_file.file_path,
                                    splitter_options={"separator":"\n","chunk_size":600,"chunk_overlap":0})
        
        contents = [doc.page_content for doc in docs]
        
        response = archive_schema.ResponseFile(id=rst_file.id,
                                            file_name=rst_file.file_name,
                                            file_size=rst_file.file_size,
                                            file_ext=rst_file.file_ext,
                                            file_desc=rst_file.file_desc,
                                            contents=contents)
        
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"파일 조회에 실패하였습니다.")

@router.put("/delete_file/")
async def delete_file(*, session: SessionDep_async, current_user: CurrentUser,in_file:archive_schema.DeleteFile) -> Any:
    try:    
        file = await archive_crud.delete_file(session=session,
                                              user_id=current_user.id,
                                              file_id=in_file.id)
        path = file.file_path
        print(path)
        if os.path.exists(path):
            os.remove(path)
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"파일 삭제에 실패하였습니다.")
    
@router.get("/download_file/{file_id}")
async def download_file(*, session: SessionDep_async, current_user: CurrentUser,file_id:uuid.UUID) -> Any:  
    try:
        rst_file = await archive_crud.get_file(session=session,file_id=file_id)
        
        if rst_file is None:
            
            rst_archive = await archive_crud.get_archive(session=session,user_id=current_user.id,archive_id=file_id)

            return StreamingResponse(io.BytesIO(rst_archive.content.encode("utf-8")),
                                     media_type="application/octet-stream",)
        
        return FileResponse(path=rst_file.file_path, filename=rst_file.file_name,
                            media_type=rst_file.file_type,
                           )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"파일 다운로드에 실패하였습니다.")