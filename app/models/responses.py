from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class ExtractionResult(BaseModel):
    success: bool = Field(..., description="Whether extraction was successful")
    extraction_type: str = Field(..., description="Type of extraction performed")
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, description="Extracted structured data")
    
    # File paths
    markdown_path: Optional[str] = Field(default=None, description="Path to saved markdown file")
    json_path: Optional[str] = Field(default=None, description="Path to saved JSON file")
    
    # Metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    token_usage: Optional[Dict[str, int]] = Field(default=None, description="OpenAI token usage")
    
    # Error handling
    error_message: Optional[str] = Field(default=None, description="Error message if extraction failed")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
