from typing import Optional
from pydantic import BaseModel, Field, validator
from .base import InputType

class ExtractionRequest(BaseModel):
    input_type: InputType = Field(..., description="Type of input: text or url")
    content: str = Field(..., description="Text content or URL to process")
    extraction_type: str = Field(..., description="Type of data to extract")
    
    # File management options
    save_markdown: bool = Field(default=False, description="Save scraped markdown content")
    save_json: bool = Field(default=True, description="Save extracted JSON data")
    output_directory: Optional[str] = Field(default=None, description="Custom output directory")
    filename_prefix: Optional[str] = Field(default=None, description="Custom filename prefix")
    
    # Processing options
    custom_instructions: Optional[str] = Field(default=None, description="Additional extraction instructions")
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()
    
    @validator('extraction_type')
    def validate_extraction_type(cls, v):
        from ..services.schema_registry import SchemaRegistry
        # Validate against available schemas at runtime
        available_types = SchemaRegistry.get_available_types()
        if v not in available_types:
            raise ValueError(f"Invalid extraction type: {v}. Available: {available_types}")
        return v
    
