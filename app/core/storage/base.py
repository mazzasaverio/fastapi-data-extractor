from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def save_file(
        self, content: str, filepath: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save content to a file

        Args:
            content: Content to save
            filepath: Path where to save the file
            metadata: Optional metadata to include

        Returns:
            Full path or URL of the saved file
        """
        pass

    @abstractmethod
    def save_json(
        self,
        data: Dict[str, Any],
        filepath: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save JSON data to a file

        Args:
            data: JSON data to save
            filepath: Path where to save the file
            metadata: Optional metadata to include

        Returns:
            Full path or URL of the saved file
        """
        pass

    @abstractmethod
    def file_exists(self, filepath: str) -> bool:
        """Check if a file exists"""
        pass

    @abstractmethod
    def get_file_url(self, filepath: str) -> str:
        """Get the URL/path to access the file"""
        pass
