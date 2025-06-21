from fastapi import APIRouter
from .modules import kitchen

api_router = APIRouter()

# Only kitchen module with single tag
api_router.include_router(
    kitchen.router, prefix="/kitchen", tags=["kitchen"]  # ← Solo un tag = una sezione
)


@api_router.get("/modules")
async def get_available_modules():
    """Get information about available modules"""
    return {"available_modules": ["kitchen"], "total_modules": 1}
