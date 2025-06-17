"""Custom exceptions for the structured extraction API"""

class ExtractionError(Exception):
    """Base exception for extraction-related errors"""
    
    def __init__(self, message: str, extraction_type: str = None, details: dict = None):
        self.message = message
        self.extraction_type = extraction_type
        self.details = details or {}
        super().__init__(self.message)

class SchemaNotFoundError(ExtractionError):
    """Raised when requested extraction schema is not found"""
    
    def __init__(self, extraction_type: str, available_types: list = None):
        self.available_types = available_types or []
        message = f"Schema not found: {extraction_type}"
        if self.available_types:
            message += f". Available types: {', '.join(self.available_types)}"
        super().__init__(message, extraction_type)

class ContentScrapingError(ExtractionError):
    """Raised when content scraping fails"""
    
    def __init__(self, url: str, reason: str = None):
        self.url = url
        self.reason = reason
        message = f"Failed to scrape content from URL: {url}"
        if reason:
            message += f". Reason: {reason}"
        super().__init__(message, details={"url": url, "reason": reason})

class OpenAIExtractionError(ExtractionError):
    """Raised when OpenAI extraction fails"""
    
    def __init__(self, message: str, extraction_type: str = None, token_usage: dict = None):
        self.token_usage = token_usage or {}
        details = {"token_usage": self.token_usage}
        super().__init__(message, extraction_type, details)

class ValidationError(ExtractionError):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        message = f"Validation error for field '{field}': {reason}"
        details = {"field": field, "value": value, "reason": reason}
        super().__init__(message, details=details)

class ConfigurationError(ExtractionError):
    """Raised when there's a configuration issue"""
    
    def __init__(self, setting: str, message: str):
        self.setting = setting
        full_message = f"Configuration error for '{setting}': {message}"
        details = {"setting": setting}
        super().__init__(full_message, details=details)