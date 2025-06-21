import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ..config import settings
from ..utils.logging_manager import LoggingManager
from .storage.factory import StorageFactory
from .storage.base import StorageBackend

logger = LoggingManager.get_logger(__name__)


class FileManager:
    """Manages file operations for extracted data with configurable storage backends"""

    def __init__(self, storage_backend: Optional[StorageBackend] = None):
        self.storage = storage_backend or StorageFactory.create_storage()

    def _generate_filename(
        self,
        content_hash: str,
        extraction_type: str,
        prefix: Optional[str] = None,
        extension: str = ".json",
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
        filename_prefix: Optional[str] = None,
    ) -> str:
        """Save extracted data as JSON file"""
        content_hash = self._get_content_hash(content)
        filename = self._generate_filename(
            content_hash, extraction_type, filename_prefix
        )

        # Determine the relative path for storage
        if output_dir:
            # Extract just the directory name if full path provided
            dir_name = output_dir.split("/")[-1] if "/" in output_dir else output_dir
            filepath = f"{dir_name}/{filename}"
        else:
            filepath = f"json/{filename}"

        # Prepare data with metadata
        save_data = {
            "metadata": {
                "extraction_type": extraction_type,
                "content_hash": content_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "filename": filename,
                "storage_backend": settings.storage_backend,
            },
            "extracted_data": data,
        }

        # Save using the storage backend
        saved_path = self.storage.save_json(save_data, filepath)

        logger.info(
            f"Saved JSON file: {filename}",
            filepath=saved_path,
            extraction_type=extraction_type,
            storage_backend=settings.storage_backend,
        )

        return saved_path

    def save_markdown(
        self,
        content: str,
        source_url: Optional[str] = None,
        output_dir: Optional[str] = None,
        filename_prefix: Optional[str] = None,
    ) -> str:
        """Save markdown content to file"""
        content_hash = self._get_content_hash(content)
        filename = self._generate_filename(
            content_hash, "markdown", filename_prefix, ".md"
        )

        # Determine the relative path for storage
        if output_dir:
            # Extract just the directory name if full path provided
            dir_name = output_dir.split("/")[-1] if "/" in output_dir else output_dir
            filepath = f"{dir_name}/{filename}"
        else:
            filepath = f"markdown/{filename}"

        # Prepare markdown content with metadata
        markdown_content = ""
        if source_url:
            markdown_content += f"<!-- Source URL: {source_url} -->\n"
        markdown_content += f"<!-- Content Hash: {content_hash} -->\n"
        markdown_content += (
            f"<!-- Saved: {datetime.now(timezone.utc).isoformat()} -->\n"
        )
        markdown_content += f"<!-- Storage Backend: {settings.storage_backend} -->\n\n"
        markdown_content += content

        # Save using the storage backend
        saved_path = self.storage.save_file(
            markdown_content,
            filepath,
            metadata={
                "source_url": source_url or "",
                "content_hash": content_hash,
                "storage_backend": settings.storage_backend,
            },
        )

        logger.info(
            f"Saved markdown file: {filename}",
            filepath=saved_path,
            storage_backend=settings.storage_backend,
        )

        return saved_path
