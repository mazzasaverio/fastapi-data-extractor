# app/core/content_scraper.py
import asyncio
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import base64

import html2text
from playwright.async_api import async_playwright

from ..config import settings
from ..utils.logging_manager import LoggingManager
from ..core.file_manager import FileManager

from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.parse import urlparse, parse_qs
from openai import OpenAI

logger = LoggingManager.get_logger(__name__)


class ContentScraper:
    """Enhanced content scraper supporting multiple input types"""

    def __init__(self):
        self.file_manager = FileManager()
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

    async def fetch_content(
        self,
        content: str,
        input_type: str,
        save_markdown: bool = False,
        output_directory: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        """
        Extract text content from various input types

        Returns:
            Tuple of (extracted_text, markdown_path)
        """
        try:
            if input_type == "text":
                return self._process_text(content, save_markdown, output_directory)
            elif input_type == "url":
                return await self._process_url_async(
                    content, save_markdown, output_directory
                )
            elif input_type == "image":
                return self._process_image_with_vision(
                    content, save_markdown, output_directory
                )
            elif input_type == "youtube_url":
                return self._process_youtube(content, save_markdown, output_directory)
            elif input_type == "audio":
                return self._process_audio_with_whisper(
                    content, save_markdown, output_directory
                )
            else:
                raise ValueError(f"Unsupported input type: {input_type}")

        except Exception as e:
            logger.error(f"Content extraction failed for {input_type}: {str(e)}")
            raise

    def _process_text(
        self, text: str, save_markdown: bool, output_dir: Optional[str]
    ) -> Tuple[str, Optional[str]]:
        """Process plain text input"""
        markdown_path = None
        if save_markdown:
            markdown_path = self.file_manager.save_markdown(
                text, None, output_dir, "text_input"
            )
        return text, markdown_path

    async def _process_url_async(
        self, url: str, save_markdown: bool, output_dir: Optional[str]
    ) -> Tuple[str, Optional[str]]:
        """Process URL input using web scraping"""
        logger.info(f"Processing URL: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Navigate to URL
                await page.goto(url, wait_until="networkidle")

                # Get page content
                html_content = await page.content()

                # Convert HTML to markdown
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = True
                markdown_content = h.handle(html_content)

                # Clean up content
                content = markdown_content.strip()

                if not content:
                    raise ValueError("No content extracted from URL")

                logger.info(f"URL scraping extracted {len(content)} characters")

                # Save markdown if requested
                markdown_path = None
                if save_markdown:
                    # Generate filename from URL
                    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                    markdown_path = self.file_manager.save_markdown(
                        content, url, output_dir, f"url_{url_hash}"
                    )

                return content, markdown_path

            except Exception as e:
                logger.error(f"URL scraping failed: {str(e)}")
                raise
            finally:
                await browser.close()

    def _process_image_with_vision(
        self, image_input: str, save_markdown: bool, output_dir: Optional[str]
    ) -> Tuple[str, Optional[str]]:
        """Process image using OpenAI Vision API - no PIL needed!"""
        logger.info("Processing image with OpenAI Vision API")

        try:
            # Prepare image for OpenAI (no PIL processing)
            image_url = self._prepare_image_for_openai(image_input)

            # Direct API call - no local image processing
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text content from this image. If it contains a recipe, cooking instructions, or food-related content, provide a detailed transcription.",
                            },
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                max_tokens=1500,
            )

            extracted_text = response.choices[0].message.content

            if not extracted_text or not extracted_text.strip():
                raise ValueError("No content extracted from image")

            logger.info(f"Vision API extracted {len(extracted_text)} characters")

            # Save markdown if requested
            markdown_path = None
            if save_markdown:
                markdown_path = self.file_manager.save_markdown(
                    extracted_text,
                    f"image_vision_{hash(image_input)}",
                    output_dir,
                    "image_vision",
                )

            return extracted_text.strip(), markdown_path

        except Exception as e:
            logger.error(f"Vision API processing failed: {str(e)}")
            raise

    def _prepare_image_for_openai(self, image_input: str) -> str:
        """Prepare image for OpenAI Vision API - no PIL needed!"""

        # URL? Pass through
        if image_input.startswith("http"):
            return image_input

        # Already base64? Pass through
        if image_input.startswith("data:image"):
            return image_input

        # File path? Convert to base64 (no PIL needed)
        if image_input.startswith("/") or image_input.startswith("./"):
            with open(image_input, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                # Simple extension detection
                ext = image_input.lower().split(".")[-1]
                mime_type = (
                    f"image/{ext}"
                    if ext in ["jpg", "jpeg", "png", "gif", "webp"]
                    else "image/jpeg"
                )
                return f"data:{mime_type};base64,{base64_image}"

        raise ValueError("Invalid image input format")

    def _process_youtube(
        self, youtube_url: str, save_markdown: bool, output_dir: Optional[str]
    ) -> Tuple[str, Optional[str]]:
        """Process YouTube URL to extract transcript"""
        logger.info(f"Processing YouTube URL: {youtube_url}")

        try:
            # Extract video ID from URL
            video_id = self._extract_youtube_id(youtube_url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")

            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=[
                    "en",
                    "it",
                    "auto",
                ],  # Try English, Italian, then auto-generated
            )

            # Combine transcript text
            transcript_text = " ".join([entry["text"] for entry in transcript_list])

            if not transcript_text.strip():
                raise ValueError("No transcript available for this video")

            logger.info(
                f"YouTube transcript extracted: {len(transcript_text)} characters"
            )

            # Save markdown if requested
            markdown_path = None
            if save_markdown:
                markdown_path = self.file_manager.save_markdown(
                    transcript_text, youtube_url, output_dir, f"youtube_{video_id}"
                )

            return transcript_text.strip(), markdown_path

        except Exception as e:
            logger.error(f"YouTube transcript extraction failed: {str(e)}")
            raise

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)",
            r"youtube\.com\/watch\?.*v=([^&\n?#]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _process_audio_with_whisper(
        self, audio_input: str, save_markdown: bool, output_dir: Optional[str]
    ) -> Tuple[str, Optional[str]]:
        """Process audio file using OpenAI Whisper API"""
        logger.info("Processing audio with OpenAI Whisper API")

        try:
            # Prepare audio file for OpenAI
            audio_file_path = self._prepare_audio_for_openai(audio_input)

            # Transcribe audio using Whisper
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, response_format="text"
                )

            if not transcript or not transcript.strip():
                raise ValueError("No content extracted from audio")

            logger.info(f"Whisper API transcribed {len(transcript)} characters")

            # Save markdown if requested
            markdown_path = None
            if save_markdown:
                audio_hash = hashlib.md5(audio_input.encode()).hexdigest()[:8]
                markdown_path = self.file_manager.save_markdown(
                    transcript,
                    f"audio_transcription_{audio_hash}",
                    output_dir,
                    "audio_transcription",
                )

            # Clean up temporary file if created
            if audio_file_path != audio_input and os.path.exists(audio_file_path):
                os.unlink(audio_file_path)

            return transcript.strip(), markdown_path

        except Exception as e:
            logger.error(f"Whisper API processing failed: {str(e)}")
            raise

    def _prepare_audio_for_openai(self, audio_input: str) -> str:
        """Prepare audio for OpenAI Whisper API"""

        # If it's a file path, return it directly
        if os.path.isfile(audio_input):
            return audio_input

        # If it's base64 encoded audio, decode and save to temp file
        if audio_input.startswith("data:audio"):
            # Extract base64 data
            header, data = audio_input.split(",", 1)
            audio_data = base64.b64decode(data)

            # Extract file extension from header
            if "audio/wav" in header:
                ext = ".wav"
            elif "audio/mp3" in header:
                ext = ".mp3"
            elif "audio/m4a" in header:
                ext = ".m4a"
            elif "audio/ogg" in header:
                ext = ".ogg"
            else:
                ext = ".wav"  # Default

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            temp_file.write(audio_data)
            temp_file.close()

            return temp_file.name

        # If it's raw base64 without header, assume it's audio
        try:
            audio_data = base64.b64decode(audio_input)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.write(audio_data)
            temp_file.close()
            return temp_file.name
        except Exception:
            pass

        raise ValueError(
            "Invalid audio input format. Provide file path or base64 encoded audio."
        )
