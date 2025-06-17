# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .api.v1 import api_router
from .utils.exceptions import ExtractionError
from .utils.logging_manager import LoggingManager

LoggingManager.configure_logging()
logger = LoggingManager.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    
    # Initialize Playwright browsers
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            await p.chromium.launch(headless=settings.playwright_headless)
        logger.success("Playwright initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Playwright: {e}")
        raise
    
    # Initialize schema registry (trigger auto-discovery)
    try:
        from .services.schema_registry import SchemaRegistry
        SchemaRegistry.discover_schemas()
        available_schemas = SchemaRegistry.get_available_types()
        logger.success("Schema registry initialized", schemas=available_schemas)
    except Exception as e:
        logger.error(f"Failed to initialize schema registry: {e}")
        raise
    
    yield
    

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Modular system for structured data extraction using OpenAI with auto-discovery schemas",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Global exception handlers
    @app.exception_handler(ExtractionError)
    async def extraction_error_handler(request, exc: ExtractionError):
        logger.error(f"Extraction error: {str(exc)}", 
                    extraction_type=getattr(exc, 'extraction_type', None),
                    details=getattr(exc, 'details', {}))
        return JSONResponse(
            status_code=422,
            content={
                "detail": str(exc),
                "type": "extraction_error",
                "extraction_type": getattr(exc, 'extraction_type', None)
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc: ValueError):
        logger.error(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "type": "validation_error"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}", error_type=type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": "internal_error"
            }
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": settings.app_name,
            "version": settings.version,
            "status": "running",
            "docs": "/docs" if settings.debug else "disabled",
            "api_base": "/api/v1"
        }
    
    # Health check endpoint (also available at root level)
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.version
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )