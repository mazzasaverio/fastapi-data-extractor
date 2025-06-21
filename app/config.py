import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Structured Extraction API"
    version: str = "0.1.0"
    debug: bool = True

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-2024-08-06"

    # Storage Configuration
    storage_backend: Literal["local", "s3"] = "local"
    data_dir: str = "data"
    markdown_output_dir: str = "data/markdown"
    json_output_dir: str = "data/json"

    # S3 Configuration (only used if storage_backend is "s3")
    s3_bucket_name: str = ""
    s3_region: str = "eu-west-3"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_endpoint_url: str = ""  # For custom S3-compatible services
    s3_prefix: str = "fastapi-data-extractor/"  # Prefix for all files in S3

    # Scraper Configuration
    playwright_headless: bool = True
    playwright_timeout: int = 60000

    # Logging Configuration
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "logs/app.log"
    log_rotation: str = "10 MB"
    log_retention: str = "1 month"
    log_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )

    # File Management
    enable_versioning: bool = True
    max_file_size_mb: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
