from fastapi import APIRouter
from .modules import kitchen, job_postings, articles

api_router = APIRouter()

# Domain-specific modules only
api_router.include_router(
    kitchen.router, prefix="/kitchen", tags=["kitchen", "recipes"]
)

api_router.include_router(
    job_postings.router, prefix="/job-postings", tags=["job-postings", "careers"]
)

api_router.include_router(
    articles.router, prefix="/articles", tags=["articles", "content"]
)
