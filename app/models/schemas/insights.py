from typing import List, Optional
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema


class Insight(BaseModel):
    title: str = Field(..., description="Insight title or summary")
    content: str = Field(..., description="Detailed insight content")
    category: str = Field(
        ...,
        description="Insight category",
        enum=["trend", "analysis", "prediction", "recommendation", "observation"],
    )
    importance: str = Field(
        ..., description="Importance level", enum=["low", "medium", "high"]
    )
    source_section: Optional[str] = Field(
        default=None, description="Section where insight was found"
    )


class InsightsExtraction(BaseExtractionSchema):
    # Schema definition
    insights: List[Insight] = Field(..., description="Extracted insights")
    key_takeaways: List[str] = Field(..., description="Main takeaways from the content")
    action_items: List[str] = Field(
        default_factory=list, description="Actionable items derived from insights"
    )

    # Class configuration for auto-discovery
    extraction_type: str = "insights"
    description: str = (
        "Extracts valuable insights, analysis, and actionable information from content"
    )
    prompt: str = """You are a strategic analyst expert at extracting valuable insights from content. Analyze the given text and extract meaningful insights.
    
    Focus on:
    - Identifying trends, patterns, and analytical observations
    - Extracting strategic recommendations and predictions
    - Capturing actionable insights and takeaways
    - Categorizing insights by type and importance
    - Providing clear, actionable summaries
    
    Prioritize insights that provide value and actionable intelligence."""
