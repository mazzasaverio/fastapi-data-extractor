from typing import List, Optional
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema

class Author(BaseModel):
    name: str = Field(..., description="Author's full name")
    role: Optional[str] = Field(default=None, description="Author role (author, editor, translator)")

class BookReview(BaseModel):
    rating: Optional[int] = Field(default=None, description="Book rating 1-5", ge=1, le=5)
    review_text: Optional[str] = Field(default=None, description="Review content")
    reviewer: Optional[str] = Field(default=None, description="Reviewer name or source")

class BookExtraction(BaseExtractionSchema):
    # Schema definition
    title: str = Field(..., description="Book title")
    authors: List[Author] = Field(..., description="Book authors")
    isbn: Optional[str] = Field(default=None, description="ISBN number")
    publication_year: Optional[int] = Field(default=None, description="Publication year")
    publisher: Optional[str] = Field(default=None, description="Publisher name")
    genre: List[str] = Field(..., description="Book genres")
    summary: str = Field(..., description="Book summary or description")
    key_topics: List[str] = Field(..., description="Main topics covered")
    target_audience: str = Field(..., description="Target audience")
    page_count: Optional[int] = Field(default=None, description="Number of pages")
    language: str = Field(default="English", description="Book language")
    reviews: List[BookReview] = Field(default_factory=list, description="Book reviews")
    
    # Class configuration for auto-discovery
    extraction_type: str = "books"
    description: str = "Extracts comprehensive book information including metadata, content summary, and reviews"
    prompt: str = """You are a librarian and book cataloging expert. Extract comprehensive book information from the given content.
    
    Focus on:
    - Identifying complete bibliographic information
    - Extracting accurate publication details
    - Summarizing content and key topics
    - Determining target audience
    - Capturing any reviews or ratings mentioned
    - Classifying genres appropriately
    
    Be thorough and accurate in extracting all available book metadata."""