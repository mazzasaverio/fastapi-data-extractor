from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends

from ....models.requests import ExtractionRequest
from ....models.responses import ExtractionResult
from ....services.extraction_service import ExtractionService
from ....services.schema_registry import SchemaRegistry
from ....utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)
router = APIRouter()

def get_extraction_service() -> ExtractionService:
    """Dependency to get extraction service instance"""
    return ExtractionService()

@router.post("/extract", response_model=ExtractionResult)
async def extract_data(
    request: ExtractionRequest,
    service: ExtractionService = Depends(get_extraction_service)
) -> ExtractionResult:
    """
    Extract structured data from text or URL
    
    - **input_type**: Either 'text' or 'url'
    - **content**: The text content or URL to process
    - **extraction_type**: Type of data to extract (notes, bookmarks, books, etc.)
    - **save_markdown**: Whether to save scraped content as markdown
    - **save_json**: Whether to save extracted data as JSON
    - **output_directory**: Custom output directory (optional)
    - **filename_prefix**: Custom filename prefix (optional)
    - **custom_instructions**: Additional extraction instructions (optional)
    """
    try:
        logger.info(f"API extraction request received", extraction_type=request.extraction_type)
        result = await service.process_extraction(request)  # Simplified method name
        
        if result.success:
            logger.info(f"API extraction completed successfully", extraction_type=request.extraction_type)
        else:
            logger.warning(f"API extraction failed", extraction_type=request.extraction_type, error=result.error_message)
        
        return result
    except Exception as e:
        logger.error(f"API extraction endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.get("/schemas")
async def get_available_schemas() -> Dict[str, Dict[str, Any]]:
    """Get information about all available extraction schemas"""
    try:
        schemas = SchemaRegistry.get_all_schemas()
        logger.debug(f"Available schemas requested", count=len(schemas))
        return schemas  # Ritorna direttamente il dict, no wrapper
    except Exception as e:
        logger.error(f"Error getting available schemas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get schemas: {str(e)}")

@router.get("/schemas/{extraction_type}")
async def get_schema_details(extraction_type: str) -> Dict[str, Any]:
    """Get detailed information about a specific extraction schema"""
    try:
        schema_class = SchemaRegistry.get_schema(extraction_type)
        
        result = {
            "name": extraction_type,
            "description": schema_class.description,
            "prompt": schema_class.prompt,
            "schema": schema_class.model_json_schema(),
            "example": {
                "input_type": "text",
                "content": "Your sample content here...",
                "extraction_type": extraction_type,
                "save_json": True
            }
        }
        
        logger.debug(f"Schema details requested", extraction_type=extraction_type)
        return result
    except ValueError as e:
        logger.warning(f"Schema not found: {extraction_type}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting schema details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get schema details: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "structured-extraction-api"}