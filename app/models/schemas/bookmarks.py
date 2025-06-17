from typing import List, Optional
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema

class BookmarkTag(BaseModel):
    name: str = Field(..., description="Tag name")
    color: Optional[str] = Field(default=None, description="Tag color code")

class BookmarkExtraction(BaseExtractionSchema):
    # Schema definition
    title: str = Field(..., description="Bookmark title")
    description: str = Field(..., description="Bookmark description")
    url: Optional[str] = Field(default=None, description="Original URL if available")
    category: str = Field(..., description="Bookmark category")
    tags: List[BookmarkTag] = Field(..., description="Associated tags")
    importance: int = Field(..., description="Importance score 1-10", ge=1, le=10)
    read_later: bool = Field(..., description="Whether this should be read later")
    estimated_read_time: Optional[int] = Field(default=None, description="Estimated reading time in minutes")
    
    # Class configuration for auto-discovery
    extraction_type: str = "bookmarks"
    schema_description: str = "Organizes content into structured bookmarks with categories, tags, and reading recommendations"
    prompt: str = """You are an expert bookmark organizer. Extract and categorize bookmark information from the given content.
    
    Focus on:
    - Creating descriptive titles and summaries
    - Identifying the most relevant category
    - Assigning meaningful tags with optional colors
    - Estimating importance and reading time
    - Determining if content warrants reading later
    
    Be precise in categorization and helpful in organization."""