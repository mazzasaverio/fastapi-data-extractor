from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from ....models.requests import ExtractionRequest
from ....models.responses import ExtractionResult
from ....services.extraction_service import ExtractionService
from ....utils.logging_manager import LoggingManager
import base64

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
    """
    Extract structured recipe data from multiple input types:
    - text: Direct text input
    - url: Web page URL
    - image: Image file (OCR)
    - youtube_url: YouTube video (transcript)
    """
    try:
        request.extraction_type = "recipes"
        logger.info(f"Processing recipe extraction from {request.input_type.value}")
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


@router.post("/extract-recipe-from-file", response_model=ExtractionResult)
async def extract_recipe_from_file(
    file: UploadFile = File(...),
    service: ExtractionService = Depends(get_extraction_service),
) -> ExtractionResult:
    """Upload an image file and extract recipe data"""
    try:
        # Read file content
        file_content = await file.read()
        base64_image = base64.b64encode(file_content).decode("utf-8")

        # Create request
        request = ExtractionRequest(
            input_type="image",
            content=f"data:image/{file.content_type.split('/')[-1]};base64,{base64_image}",
            extraction_type="recipes",
            save_json=True,
        )

        return await service.process_extraction(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
