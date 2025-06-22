from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .base import InputType


class ExtractionRequest(BaseModel):
    input_type: InputType = Field(
        ..., description="Type of input: text, url, image, audio, or youtube_url"
    )
    content: str = Field(
        ...,
        description="Text content, URL, image path/base64, audio path/base64, or YouTube URL to process",
    )
    extraction_type: str = Field(..., description="Type of data to extract")

    # File management options
    save_markdown: bool = Field(
        default=False, description="Save scraped markdown content"
    )
    save_json: bool = Field(default=True, description="Save extracted JSON data")
    output_directory: Optional[str] = Field(
        default=None, description="Custom output directory"
    )
    filename_prefix: Optional[str] = Field(
        default=None, description="Custom filename prefix"
    )

    # Processing options
    custom_instructions: Optional[str] = Field(
        default=None, description="Additional extraction instructions"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()

    # COMMENTA questo validator che causa il problema
    # @validator('extraction_type')
    # def validate_extraction_type(cls, v):
    #     from ..services.schema_registry import SchemaRegistry
    #     # Validate against available schemas at runtime
    #     available_types = SchemaRegistry.get_available_types()
    #     if v not in available_types:
    #         raise ValueError(f"Invalid extraction type: {v}. Available: {available_types}")
    #     return v


class AudioUploadRequest(BaseModel):
    """Request model for audio file uploads"""

    extraction_type: str = Field(
        ..., description="Type of data to extract from transcription"
    )

    # File management options
    save_markdown: bool = Field(
        default=False, description="Save transcription as markdown"
    )
    save_json: bool = Field(default=True, description="Save extracted JSON data")
    output_directory: Optional[str] = Field(
        default=None, description="Custom output directory"
    )
    filename_prefix: Optional[str] = Field(
        default=None, description="Custom filename prefix"
    )

    # Processing options
    custom_instructions: Optional[str] = Field(
        default=None, description="Additional extraction instructions"
    )
