# app/core/extraction_engine.py
import time
from typing import Optional, Dict, Any, Tuple
from openai import OpenAI

from ..config import settings
from ..services.schema_registry import SchemaRegistry
from ..utils.logging_manager import LoggingManager

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
        custom_instructions: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, int], float]:
        """
        Extract structured data from content using specified schema
        
        Returns:
            Tuple of (extracted_data, token_usage, processing_time)
        """
        start_time = time.time()
        
        # Get schema class for extraction type
        schema_class = self.schema_registry.get_schema(extraction_type)
        
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
                "total_tokens": completion.usage.total_tokens
            }
            
            processing_time = time.time() - start_time
            
            logger.success(
                f"Successfully extracted data",
                extraction_type=extraction_type,
                processing_time=round(processing_time, 2),
                tokens_used=token_usage["total_tokens"]
            )
            
            # Log metrics
            LoggingManager.log_extraction_metrics(
                extraction_type, processing_time, token_usage, True
            )
            
            return result.model_dump(), token_usage, processing_time
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"Error extracting structured data",
                extraction_type=extraction_type,
                error=str(e),
                processing_time=round(processing_time, 2)
            )
            
            # Log failed metrics
            LoggingManager.log_extraction_metrics(
                extraction_type, processing_time, {}, False
            )
            
            raise