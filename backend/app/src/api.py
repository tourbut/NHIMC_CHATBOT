from fastapi import APIRouter
from app.src.routes import users,settings,admin,archive,chat,textmining

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(archive.router, prefix="/archive", tags=["archive"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(textmining.router, prefix="/textmining", tags=["textmining"])