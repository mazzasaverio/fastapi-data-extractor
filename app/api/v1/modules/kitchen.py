from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from ....models.requests import ExtractionRequest
from ....models.responses import ExtractionResult
from ....services.extraction_service import ExtractionService
from ....utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)


router = APIRouter()


def get_extraction_service() -> ExtractionService:
    """Dependency to get extraction service instance"""
    return ExtractionService()


@router.post("/extract-recipe", response_model=ExtractionResult)
async def extract_recipe_data(
    request: ExtractionRequest,
    service: ExtractionService = Depends(get_extraction_service),
) -> ExtractionResult:
    """Extract structured data from recipes"""
    try:
        # Force the extraction type (bypasses validation)
        request.extraction_type = "recipes"
        logger.info("Processing recipe extraction request")
        return await service.process_extraction(request)
    except Exception as e:
        logger.error(f"Recipe extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Recipe extraction failed: {str(e)}"
        )


@router.post("/extract-ingredients", response_model=ExtractionResult)
async def extract_ingredients_data(
    request: ExtractionRequest,
    service: ExtractionService = Depends(get_extraction_service),
) -> ExtractionResult:
    """Extract ingredients list from recipe content"""
    try:
        request.extraction_type = "ingredients"
        logger.info("Processing ingredients extraction request")
        return await service.process_extraction(request)
    except Exception as e:
        logger.error(f"Ingredients extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Ingredients extraction failed: {str(e)}"
        )
