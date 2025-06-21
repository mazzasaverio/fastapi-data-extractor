from typing import Optional

from .base import StorageBackend
from .local_storage import LocalStorage
from .s3_storage import S3Storage
from ...config import settings
from ...utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)


class StorageFactory:
    """Factory class to create storage backends"""

    @staticmethod
    def create_storage(backend_type: Optional[str] = None) -> StorageBackend:
        """
        Create a storage backend based on configuration

        Args:
            backend_type: Override the configured backend type

        Returns:
            StorageBackend instance
        """
        backend = backend_type or settings.storage_backend

        if backend == "local":
            logger.info("Using local storage backend")
            return LocalStorage(base_dir=settings.data_dir)

        elif backend == "s3":
            logger.info("Using S3 storage backend")

            # Validate S3 configuration
            if not settings.s3_bucket_name:
                raise ValueError("S3 bucket name is required when using S3 storage")

            return S3Storage(
                bucket_name=settings.s3_bucket_name,
                region=settings.s3_region,
                access_key_id=settings.s3_access_key_id or None,
                secret_access_key=settings.s3_secret_access_key or None,
                endpoint_url=settings.s3_endpoint_url or None,
                prefix=settings.s3_prefix,
            )

        else:
            raise ValueError(f"Unsupported storage backend: {backend}")
