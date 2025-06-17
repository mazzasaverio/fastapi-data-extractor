# app/core/content_scraper.py
import asyncio
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple

import html2text
from playwright.async_api import async_playwright

from ..config import settings
from ..utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)

class ContentScraper:
    """Web content scraper using Playwright"""
    
    def __init__(self, headless: bool = True, timeout: int = 60000):
        self.headless = headless
        self.timeout = timeout
        
        # Configure html2text converter
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.body_width = 0
        self.converter.ignore_images = True
        
        logger.debug("ContentScraper initialized", 
                    headless=headless, 
                    timeout=timeout)
    
    def _generate_filename(self, url: str) -> str:
        """Generate a unique filename based on URL hash"""
        url_hash = hashlib.sha1(url.encode()).hexdigest()
        return f"{url_hash}.md"
    
    async def _fetch_content_async(
        self, url: str, save_markdown: bool = False, output_dir: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """Asynchronously fetch content from URL"""
        logger.info(f"Fetching content from URL", url=url)
        
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                
                # Set viewport and user agent
                await page.set_viewport_size({"width": 1280, "height": 720})
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })
                
                # Navigate to URL
                await page.goto(
                    url, 
                    wait_until="domcontentloaded", 
                    timeout=self.timeout
                )
                
                # Wait a bit for dynamic content
                await asyncio.sleep(2)
                
                # Get page info
                title = await page.title()
                content = await page.content()
                
                # Close browser
                await browser.close()
                
                # Convert HTML to markdown
                markdown = self.converter.handle(content)
                
                logger.success(
                    f"Successfully fetched content",
                    url=url,
                    title=title, 
                    content_length=len(markdown)
                )
                
                # Save markdown if requested
                filepath = None
                if save_markdown:
                    filepath = self._save_markdown(url, markdown, output_dir)
                
                return markdown, filepath
                
        except Exception as e:
            logger.error(f"Error fetching content from URL", url=url, error=str(e))
            raise
    
    def _save_markdown(
        self, url: str, content: str, output_dir: Optional[str] = None
    ) -> str:
        """Save markdown content to file"""
        output_dir = output_dir or settings.markdown_output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        filename = self._generate_filename(url)
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"<!-- URL: {url} -->\n")
                f.write(f"<!-- Filename: {filename} -->\n")
                f.write(f"<!-- Scraped: {asyncio.get_event_loop().time()} -->\n\n")
                f.write(content)
            
            logger.info(f"Saved markdown file", filepath=filepath, url=url)
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save markdown file", filepath=filepath, error=str(e))
            raise
    
    def fetch_content(
        self, url: str, save_markdown: bool = False, output_dir: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """Fetch content from URL (synchronous wrapper)"""
        return asyncio.run(self._fetch_content_async(url, save_markdown, output_dir))