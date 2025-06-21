from fastapi import APIRouter, HTTPException, Depends
from ....models.requests import ExtractionRequest
from ....models.responses import ExtractionResult
from ....services.extraction_service import ExtractionService
from ....services.schema_registry import SchemaRegistry
from ....utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)
router = APIRouter()


def get_extraction_service() -> ExtractionService:
    return ExtractionService()


@router.post("/extract-job", response_model=ExtractionResult)
async def extract_job_posting(
    request: ExtractionRequest,
    service: ExtractionService = Depends(get_extraction_service),
) -> ExtractionResult:
    """Extract structured data from job postings"""
    try:
        request.extraction_type = "job_postings"
        logger.info("Processing job posting extraction request")
        return await service.process_extraction(request)
    except Exception as e:
        logger.error(f"Job posting extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Job posting extraction failed: {str(e)}"
        )


@router.get("/schemas")
async def get_job_schemas():
    """Get available job posting extraction schemas"""
    try:
        all_schemas = SchemaRegistry.get_all_schemas()
        job_schemas = {k: v for k, v in all_schemas.items() if "job" in k.lower()}
        return {"module": "job_postings", "schemas": job_schemas}
    except Exception as e:
        logger.error(f"Error getting job schemas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
