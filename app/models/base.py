from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from enum import Enum


class InputType(str, Enum):
    TEXT = "text"
    URL = "url"
    IMAGE = "image"
    YOUTUBE_URL = "youtube_url"


class BaseExtractionSchema(BaseModel):
    """Base class for all extraction schemas

    Subclasses should define these class attributes:
    - extraction_type: str - Unique identifier for this extraction type
    - description: str - Human-readable description of what this schema extracts
    - prompt: str - System prompt for OpenAI extraction
    """

    # These will be set by subclasses as class attributes
    # Don't define them here to avoid Pydantic field conflicts
    pass
