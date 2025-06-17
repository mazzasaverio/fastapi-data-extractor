import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import settings
from ..utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)

class FileManager:
    """Manages file operations for extracted data"""
    
    def __init__(self):
        Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
        Path(settings.markdown_output_dir).mkdir(parents=True, exist_ok=True)
        Path(settings.json_output_dir).mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(
        self, 
        content_hash: str, 
        extraction_type: str,
        prefix: Optional[str] = None,
        extension: str = ".json"
    ) -> str:
        """Generate filename with optional versioning"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        parts = []
        if prefix:
            parts.append(prefix)
        parts.extend([extraction_type, content_hash[:8], timestamp])
        
        return "_".join(parts) + extension
    
    def _get_content_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def save_json(
        self,
        data: Dict[str, Any],
        content: str,
        extraction_type: str,
        output_dir: Optional[str] = None,
        filename_prefix: Optional[str] = None
    ) -> str:
        """Save extracted data as JSON file"""
        output_dir = output_dir or settings.json_output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        content_hash = self._get_content_hash(content)
        filename = self._generate_filename(
            content_hash, 
            extraction_type, 
            filename_prefix
        )
        filepath = os.path.join(output_dir, filename)
        
        # Add metadata to saved data
        save_data = {
            "metadata": {
                "extraction_type": extraction_type,
                "content_hash": content_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "filename": filename
            },
            "extracted_data": data
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(filepath)
        logger.info(
            f"Saved JSON file: {filename}",
            filepath=filepath,
            extraction_type=extraction_type,
            size_bytes=file_size
        )
        
        return filepath
    
    def save_markdown(
        self,
        content: str,
        source_url: Optional[str] = None,
        output_dir: Optional[str] = None,
        filename_prefix: Optional[str] = None
    ) -> str:
        """Save markdown content to file"""
        output_dir = output_dir or settings.markdown_output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        content_hash = self._get_content_hash(content)
        filename = self._generate_filename(
            content_hash, 
            "markdown", 
            filename_prefix,
            ".md"
        )
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            if source_url:
                f.write(f"<!-- Source URL: {source_url} -->\n")
            f.write(f"<!-- Content Hash: {content_hash} -->\n")
            f.write(f"<!-- Saved: {datetime.now(timezone.utc).isoformat()} -->\n\n")
            f.write(content)
        
        file_size = os.path.getsize(filepath)
        logger.info(f"Saved markdown file: {filename}", filepath=filepath, size_bytes=file_size)
        
        return filepath