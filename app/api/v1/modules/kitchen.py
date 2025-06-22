from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from ....models.requests import ExtractionRequest, AudioUploadRequest
from ....models.responses import ExtractionResult
from ....services.extraction_service import ExtractionService
from ....utils.logging_manager import LoggingManager
import base64
import tempfile
import os

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
    - audio: Audio file (transcription)
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


@router.post("/extract-recipe-from-audio", response_model=ExtractionResult)
async def extract_recipe_from_audio(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    save_markdown: bool = Form(
        default=False, description="Save transcription as markdown"
    ),
    save_json: bool = Form(default=True, description="Save extracted JSON data"),
    output_directory: str = Form(default=None, description="Custom output directory"),
    filename_prefix: str = Form(default=None, description="Custom filename prefix"),
    custom_instructions: str = Form(
        default=None, description="Additional extraction instructions"
    ),
    service: ExtractionService = Depends(get_extraction_service),
) -> ExtractionResult:
    """Upload an audio file, transcribe it using OpenAI Whisper, and extract recipe data"""
    temp_file_path = None
    try:
        # Validate audio file type
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Expected audio file, got {audio_file.content_type}",
            )

        # Save uploaded file to temporary location
        file_content = await audio_file.read()

        # Get file extension from content type or filename
        file_extension = ".wav"  # Default
        if audio_file.content_type == "audio/mpeg":
            file_extension = ".mp3"
        elif audio_file.content_type == "audio/wav":
            file_extension = ".wav"
        elif audio_file.content_type == "audio/m4a":
            file_extension = ".m4a"
        elif audio_file.content_type == "audio/ogg":
            file_extension = ".ogg"
        elif audio_file.filename:
            # Extract from filename if available
            original_ext = os.path.splitext(audio_file.filename)[1]
            if original_ext in [".mp3", ".wav", ".m4a", ".ogg", ".webm"]:
                file_extension = original_ext

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file.write(file_content)
        temp_file.close()
        temp_file_path = temp_file.name

        logger.info(
            f"Processing audio file: {audio_file.filename} ({audio_file.content_type})"
        )

        # Create extraction request
        request = ExtractionRequest(
            input_type="audio",
            content=temp_file_path,
            extraction_type="recipes",
            save_markdown=save_markdown,
            save_json=save_json,
            output_directory=output_directory,
            filename_prefix=filename_prefix,
            custom_instructions=custom_instructions,
        )

        # Process extraction
        result = await service.process_extraction(request)

        logger.success(f"Successfully processed audio file: {audio_file.filename}")
        return result

    except Exception as e:
        logger.error(f"Audio recipe extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Audio recipe extraction failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(
                    f"Failed to clean up temporary file {temp_file_path}: {str(e)}"
                )
