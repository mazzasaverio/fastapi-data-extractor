from typing import List, Optional
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema

class Tag(BaseModel):
    name: str = Field(..., description="Tag name")
    category: Optional[str] = Field(default=None, description="Tag category")

class Note(BaseModel):
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Main note content")
    summary: str = Field(..., description="Brief summary of the note")
    
class NotesExtraction(BaseExtractionSchema):
    # Schema definition
    notes: List[Note] = Field(..., description="Extracted notes")
    main_topics: List[str] = Field(..., description="Main topics covered")
    tags: List[Tag] = Field(..., description="Relevant tags")
    priority: str = Field(..., description="Priority level", enum=["low", "medium", "high"])
    category: str = Field(..., description="Note category")
    
    # Class configuration for auto-discovery
    extraction_type: str = "notes"
    description: str = "Extracts and organizes text into structured notes with topics, tags, and priority levels"
    prompt: str = """You are an expert note-taking assistant. Extract and organize information from the given text into structured notes. 
    
    Focus on:
    - Creating clear, actionable notes with meaningful titles
    - Identifying main topics and themes
    - Assigning appropriate tags and categories
    - Determining priority based on urgency and importance
    - Providing concise but comprehensive summaries
    
    Be thorough and ensure all important information is captured."""