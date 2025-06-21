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


@router.post("/extract-quotes", response_model=ExtractionResult)
async def extract_quotes(
    request: ExtractionRequest,
    service: ExtractionService = Depends(get_extraction_service),
) -> ExtractionResult:
    """Extract meaningful quotes from articles"""
    try:
        request.extraction_type = "quotes"
        logger.info("Processing quotes extraction request")
        return await service.process_extraction(request)
    except Exception as e:
        logger.error(f"Quotes extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Quotes extraction failed: {str(e)}"
        )


@router.post("/extract-insights", response_model=ExtractionResult)
async def extract_insights(
    request: ExtractionRequest,
    service: ExtractionService = Depends(get_extraction_service),
) -> ExtractionResult:
    """Extract insights and key takeaways from articles"""
    try:
        request.extraction_type = "insights"
        logger.info("Processing insights extraction request")
        return await service.process_extraction(request)
    except Exception as e:
        logger.error(f"Insights extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Insights extraction failed: {str(e)}"
        )


@router.get("/schemas")
async def get_article_schemas():
    """Get available article extraction schemas"""
    try:
        all_schemas = SchemaRegistry.get_all_schemas()
        article_schemas = {
            k: v
            for k, v in all_schemas.items()
            if any(
                term in k.lower() for term in ["quote", "insight", "article", "notes"]
            )
        }
        return {"module": "articles", "schemas": article_schemas}
    except Exception as e:
        logger.error(f"Error getting article schemas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
