from fastapi import APIRouter
from .endpoints import extraction

api_router = APIRouter()

api_router.include_router(
    extraction.router,
    prefix="/extraction",
    tags=["extraction"]
)

