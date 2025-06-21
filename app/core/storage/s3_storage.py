import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from .base import StorageBackend
from ...utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)


class S3Storage(StorageBackend):
    """S3 storage backend"""

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        prefix: str = "",
    ):
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for S3 storage. Install it with: pip install boto3"
            )

        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/") + "/" if prefix else ""

        # Initialize S3 client
        # Se access_key_id e secret_access_key sono None o vuoti, boto3 userà le credenziali di default
        if access_key_id and secret_access_key:
            # Usa credenziali esplicite
            session = boto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region,
            )
            logger.info("Using explicit AWS credentials from environment")
        else:
            # Usa credenziali di default (aws configure, IAM role, etc.)
            session = boto3.Session(region_name=region)
            logger.info("Using default AWS credentials (aws configure or IAM role)")

        client_kwargs = {}
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url

        self.s3_client = session.client("s3", **client_kwargs)

        # Verify bucket access
        self._verify_bucket_access()

    def _verify_bucket_access(self):
        """Verify that we can access the S3 bucket"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Successfully connected to S3 bucket: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise ValueError(f"S3 bucket '{self.bucket_name}' does not exist")
            elif error_code == "403":
                raise ValueError(f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                raise ValueError(f"Error accessing S3 bucket '{self.bucket_name}': {e}")
        except NoCredentialsError:
            raise ValueError(
                "AWS credentials not found. Please run 'aws configure' or set credentials in environment variables."
            )

    def _get_s3_key(self, filepath: str) -> str:
        """Get the full S3 key including prefix"""
        return f"{self.prefix}{filepath.lstrip('/')}"

    def save_file(
        self, content: str, filepath: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save content to S3"""
        s3_key = self._get_s3_key(filepath)

        # Prepare metadata for S3
        s3_metadata = {
            "saved-at": datetime.now(timezone.utc).isoformat(),
            "content-type": "text/plain",
        }
        if metadata:
            # Convert metadata values to strings (S3 requirement)
            s3_metadata.update({k: str(v) for k, v in metadata.items()})

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content.encode("utf-8"),
                ContentType="text/plain; charset=utf-8",
                Metadata=s3_metadata,
            )

            logger.info(
                f"Saved file to S3: {filepath}",
                bucket=self.bucket_name,
                s3_key=s3_key,
                size_bytes=len(content.encode("utf-8")),
            )

            return f"s3://{self.bucket_name}/{s3_key}"

        except ClientError as e:
            logger.error(f"Failed to save file to S3: {e}")
            raise

    def save_json(
        self,
        data: Dict[str, Any],
        filepath: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save JSON data to S3"""
        s3_key = self._get_s3_key(filepath)

        save_data = data.copy()
        if metadata:
            save_data["metadata"] = {**save_data.get("metadata", {}), **metadata}

        json_content = json.dumps(save_data, indent=2, ensure_ascii=False)

        # Prepare metadata for S3
        s3_metadata = {
            "saved-at": datetime.now(timezone.utc).isoformat(),
            "content-type": "application/json",
        }
        if metadata:
            s3_metadata.update({k: str(v) for k, v in metadata.items()})

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_content.encode("utf-8"),
                ContentType="application/json; charset=utf-8",
                Metadata=s3_metadata,
            )

            logger.info(
                f"Saved JSON file to S3: {filepath}",
                bucket=self.bucket_name,
                s3_key=s3_key,
                size_bytes=len(json_content.encode("utf-8")),
            )

            return f"s3://{self.bucket_name}/{s3_key}"

        except ClientError as e:
            logger.error(f"Failed to save JSON file to S3: {e}")
            raise

    def file_exists(self, filepath: str) -> bool:
        """Check if file exists in S3"""
        s3_key = self._get_s3_key(filepath)

        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def get_file_url(self, filepath: str) -> str:
        """Get S3 URL for the file"""
        s3_key = self._get_s3_key(filepath)
        return f"s3://{self.bucket_name}/{s3_key}"
