from typing import List, Optional
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema


class Quote(BaseModel):
    text: str = Field(..., description="The actual quote text")
    author: Optional[str] = Field(default=None, description="Quote author if mentioned")
    context: Optional[str] = Field(
        default=None, description="Context or situation of the quote"
    )


class QuotesExtraction(BaseExtractionSchema):
    quotes: List[Quote] = Field(..., description="Extracted quotes")
    main_themes: List[str] = Field(..., description="Main themes of the quotes")
    total_quotes: int = Field(..., description="Total number of quotes found")

    # Class configuration
    extraction_type: str = "quotes"
    description: str = "Extracts meaningful quotes and memorable statements from text"
    prompt: str = (
        """Extract meaningful quotes from the given content. Focus on impactful statements and preserve exact text."""
    )
