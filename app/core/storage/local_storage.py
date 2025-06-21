import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .base import StorageBackend
from ...utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)


class LocalStorage(StorageBackend):
    """Local filesystem storage backend"""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(
        self, content: str, filepath: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save content to local file"""
        full_path = self.base_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = os.path.getsize(full_path)
        logger.info(
            f"Saved file locally: {filepath}",
            filepath=str(full_path),
            size_bytes=file_size,
        )

        return str(full_path)

    def save_json(
        self,
        data: Dict[str, Any],
        filepath: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save JSON data to local file"""
        full_path = self.base_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        save_data = data.copy()
        if metadata:
            save_data["metadata"] = {**save_data.get("metadata", {}), **metadata}

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(full_path)
        logger.info(
            f"Saved JSON file locally: {filepath}",
            filepath=str(full_path),
            size_bytes=file_size,
        )

        return str(full_path)

    def file_exists(self, filepath: str) -> bool:
        """Check if file exists locally"""
        return (self.base_dir / filepath).exists()

    def get_file_url(self, filepath: str) -> str:
        """Get local file path"""
        return str(self.base_dir / filepath)
