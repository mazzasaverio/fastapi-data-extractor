import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Structured Extraction API"
    version: str = "0.1.0"
    debug: bool = False
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-2024-08-06"
    
    # Storage Configuration
    data_dir: str = "data"
    markdown_output_dir: str = "data/markdown"
    json_output_dir: str = "data/json"
    
    # Scraper Configuration
    playwright_headless: bool = True
    playwright_timeout: int = 60000
    
    # Logging Configuration
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "logs/app.log"
    log_rotation: str = "10 MB"
    log_retention: str = "1 month"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    
    # File Management
    enable_versioning: bool = True
    max_file_size_mb: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()