# app/core/extraction_engine.py
import time
from typing import Optional, Dict, Any, Tuple
from openai import OpenAI

from ..config import settings
from ..services.schema_registry import SchemaRegistry
from ..utils.logging_manager import LoggingManager
from ..core.content_scraper import ContentScraper

logger = LoggingManager.get_logger(__name__)


class ExtractionEngine:
    """Core engine for structured data extraction using OpenAI"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Provide it as parameter or set "
                "OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = model or settings.openai_model
        self.schema_registry = SchemaRegistry()

    def extract_structured_data(
        self,
        content: str,
        extraction_type: str,
        custom_instructions: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, int], float]:
        """
        Extract structured data from content using specified schema

        Returns:
            Tuple of (extracted_data, token_usage, processing_time)
        """
        start_time = time.time()

        # Try registry first, fallback to direct import
        try:
            schema_class = self.schema_registry.get_schema(extraction_type)
        except ValueError:
            # Direct import fallback for new schemas
            if extraction_type == "recipes":
                from ..models.schemas.recipes import RecipeExtraction

                schema_class = RecipeExtraction
            elif extraction_type == "quotes":
                from ..models.schemas.quotes import QuotesExtraction

                schema_class = QuotesExtraction
            elif extraction_type == "insights":
                from ..models.schemas.insights import InsightsExtraction

                schema_class = InsightsExtraction
            else:
                raise ValueError(f"Unknown extraction type: {extraction_type}")

        # Build system prompt
        system_prompt = schema_class.prompt
        if custom_instructions:
            system_prompt += f"\n\nAdditional instructions: {custom_instructions}"

        logger.info(f"Starting extraction", extraction_type=extraction_type)

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Extract structured information from this content:\n\n{content}"
                        ),
                    },
                ],
                response_format=schema_class,
            )

            result = completion.choices[0].message.parsed
            token_usage = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            }

            processing_time = time.time() - start_time

            logger.success(
                f"Successfully extracted data",
                extraction_type=extraction_type,
                processing_time=round(processing_time, 2),
                tokens_used=token_usage["total_tokens"],
            )

            return result.model_dump(), token_usage, processing_time

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"Error extracting structured data",
                extraction_type=extraction_type,
                error=str(e),
                processing_time=round(processing_time, 2),
            )

            raise

    def extract_from_image_directly(
        self,
        image_input: str,
        extraction_type: str,
        custom_instructions: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, int], float]:
        """Extract structured data directly from image using Vision API"""
        start_time = time.time()

        # Get schema class
        if extraction_type == "recipes":
            from ..models.schemas.recipes import RecipeExtraction

            schema_class = RecipeExtraction
        else:
            raise ValueError(
                f"Direct image extraction not supported for: {extraction_type}"
            )

        # Prepare image
        scraper = ContentScraper()
        image_url = scraper._prepare_image_for_openai(image_input)

        # Build prompt for direct extraction
        system_prompt = f"""You are extracting structured recipe data directly from an image. 
        {schema_class.prompt}
        
        Look at the image carefully and extract all recipe information you can see.
        If ingredients are listed, extract them with quantities.
        If cooking steps are shown, extract them in order.
        """

        if custom_instructions:
            system_prompt += f"\n\nAdditional instructions: {custom_instructions}"

        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract recipe information from this image:",
                            },
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    },
                ],
                response_format=schema_class,
            )

            result = completion.choices[0].message.parsed
            token_usage = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            }

            processing_time = time.time() - start_time

            logger.success(
                f"Direct image extraction completed",
                processing_time=round(processing_time, 2),
            )

            return result.model_dump(), token_usage, processing_time

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Direct image extraction failed: {str(e)}")
            raise
