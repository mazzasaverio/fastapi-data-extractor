import time
from typing import Optional

from ..core.content_scraper import ContentScraper
from ..core.extraction_engine import ExtractionEngine
from ..core.file_manager import FileManager
from ..models.base import InputType
from ..models.requests import ExtractionRequest
from ..models.responses import ExtractionResult
from ..utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)


class ExtractionService:
    """Service for extraction requests supporting multiple input types"""

    def __init__(self):
        self.scraper = ContentScraper()
        self.extraction_engine = ExtractionEngine()
        self.file_manager = FileManager()

    async def process_extraction(self, request: ExtractionRequest) -> ExtractionResult:
        """Process extraction request with multiple input types"""
        start_time = time.time()

        logger.info(
            f"Processing extraction request",
            extraction_type=request.extraction_type,
            input_type=request.input_type.value,
        )

        try:
            # For images, use direct extraction if it's recipes
            if (
                request.input_type == InputType.IMAGE
                and request.extraction_type == "recipes"
            ):
                extracted_data, token_usage, extraction_time = (
                    self.extraction_engine.extract_from_image_directly(
                        request.content,
                        request.extraction_type,
                        request.custom_instructions,
                    )
                )
                markdown_path = None  # No intermediate text for direct extraction
                content = "Direct image extraction - no intermediate text"
            else:
                # Standard flow: extract text first, then process
                if request.input_type == InputType.TEXT:
                    content = request.content
                    markdown_path = None
                    if request.save_markdown:
                        markdown_path = self.file_manager.save_markdown(
                            content,
                            None,
                            request.output_directory,
                            request.filename_prefix,
                        )
                else:
                    # Use ContentScraper for URL, YOUTUBE_URL, AUDIO (now async!)
                    content, markdown_path = await self.scraper.fetch_content(
                        request.content,
                        request.input_type.value,
                        request.save_markdown,
                        request.output_directory,
                    )

                # Extract structured data
                extracted_data, token_usage, extraction_time = (
                    self.extraction_engine.extract_structured_data(
                        content, request.extraction_type, request.custom_instructions
                    )
                )

            # Save JSON if requested
            json_path = None
            if request.save_json:
                json_path = self.file_manager.save_json(
                    extracted_data,
                    content,
                    request.extraction_type,
                    request.output_directory,
                    request.filename_prefix,
                )

            processing_time = time.time() - start_time

            logger.success(
                f"Successfully completed extraction",
                extraction_type=request.extraction_type,
                total_time=round(processing_time, 2),
                extraction_time=round(extraction_time, 2),
            )

            return ExtractionResult(
                success=True,
                extraction_type=request.extraction_type,
                extracted_data=extracted_data,
                markdown_path=markdown_path,
                json_path=json_path,
                processing_time=processing_time,
                token_usage=token_usage,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_message = str(e)

            # Log the FULL error with traceback
            logger.error(
                f"Extraction failed: {error_message}",
                extraction_type=request.extraction_type,
                error=error_message,
                processing_time=round(processing_time, 2),
                exc_info=True,  # This will include the full traceback
            )

            return ExtractionResult(
                success=False,
                extraction_type=request.extraction_type,
                processing_time=processing_time,
                error_message=error_message,
            )
