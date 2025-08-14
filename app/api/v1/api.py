from fastapi import APIRouter
from app.api.v1.endpoints import hello, background_removal

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(hello.router, tags=["hello"])
api_router.include_router(background_removal.router, prefix="/ai", tags=["background-removal"]) 