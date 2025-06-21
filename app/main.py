# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from .config import settings
from .api.v1 import api_router
from .utils.exceptions import ExtractionError
from .utils.logging_manager import LoggingManager
from .services.schema_registry import SchemaRegistry

# Configure logging
LoggingManager.configure_logging(level=settings.log_level, debug=settings.debug)

logger = LoggingManager.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting FastAPI Data Extractor API")

    # Initialize schema registry
    SchemaRegistry.discover_schemas()
    logger.success("Schema registry initialized")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI Data Extractor API")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Advanced data extraction API with multiple input types and configurable storage",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api")

    # Global exception handlers
    @app.exception_handler(ExtractionError)
    async def extraction_error_handler(request, exc: ExtractionError):
        logger.error(
            f"Extraction error: {str(exc)}",
            extraction_type=getattr(exc, "extraction_type", None),
            details=getattr(exc, "details", {}),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": str(exc),
                "type": "extraction_error",
                "extraction_type": getattr(exc, "extraction_type", None),
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc: ValueError):
        logger.error(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=400, content={"detail": str(exc), "type": "validation_error"}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}", error_type=type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": "internal_error"},
        )

    # Root endpoint
    @app.get("/")
    async def read_root():
        """Root endpoint with API information"""
        return {
            "message": "FastAPI Data Extractor API",
            "version": settings.version,
            "docs_url": "/docs",
            "health_check": "/health",
            "storage_backend": settings.storage_backend,
        }

    # Health check endpoint (also available at root level)
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Docker and monitoring"""
        try:
            # Test storage backend connection
            from .core.storage.factory import StorageFactory

            storage = StorageFactory.create_storage()
            storage_status = "healthy"
        except Exception as e:
            storage_status = f"error: {str(e)}"

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
            "storage_backend": settings.storage_backend,
            "storage_status": storage_status,
            "environment": "development" if settings.debug else "production",
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
        log_level=settings.log_level.lower(),
    )
