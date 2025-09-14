"""
Web scraping and content extraction utilities for SelfLayer.

This module provides async HTTP client functionality with robust error handling,
retry logic, and content extraction using BeautifulSoup. Designed for efficient
web content fetching with proper rate limiting and timeout management.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag
from pydantic import HttpUrl

from . import WebError

# Configure module logger
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5MB limit


class WebClient:
    """
    Async HTTP client with retry logic and content extraction capabilities.

    This class provides a high-level interface for fetching and processing
    web content with built-in error handling, rate limiting, and content
    cleaning functionality.
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        user_agent: str | None = None,
    ) -> None:
        """
        Initialize the web client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Default user agent that identifies as a content analyzer
        default_ua = (
            "SelfLayer/1.0 (AI Terminal Browser; "
            "+https://github.com/antonvice/selflayer) httpx"
        )
        self.user_agent = user_agent or default_ua

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            follow_redirects=True,
        )

    async def __aenter__(self) -> "WebClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if hasattr(self, "client"):
            await self.client.aclose()

    async def fetch_content(self, url: str | HttpUrl) -> str:
        """
        Fetch raw HTML content from a URL with retry logic.

        Args:
            url: The URL to fetch content from

        Returns:
            Raw HTML content as a string

        Raises:
            WebError: If fetching fails after all retries
        """
        url_str = str(url)
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Fetching {url_str} (attempt {attempt + 1})")

                response = await self.client.get(url_str)
                response.raise_for_status()

                # Check content size
                content_length = len(response.content)
                if content_length > MAX_CONTENT_SIZE:
                    raise WebError(
                        f"Content too large: {content_length} bytes "
                        f"(max: {MAX_CONTENT_SIZE})"
                    )

                # Detect encoding and decode content
                content = response.text
                logger.info(f"Successfully fetched {url_str} ({content_length} bytes)")
                return content

            except httpx.HTTPStatusError as e:
                last_exception = WebError(f"HTTP {e.response.status_code}: {e}")
                logger.warning(f"HTTP error for {url_str}: {e}")

                # Don't retry for client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    break

            except httpx.TimeoutException as e:
                last_exception = WebError(f"Request timeout for {url_str}: {e}")
                logger.warning(f"Timeout for {url_str}")

            except Exception as e:
                last_exception = WebError(f"Network error for {url_str}: {e}")
                logger.error(f"Unexpected error for {url_str}: {e}")

            # Wait before retrying (exponential backoff)
            if attempt < self.max_retries:
                delay = self.retry_delay * (2**attempt)
                logger.debug(f"Retrying {url_str} in {delay:.1f}s")
                await asyncio.sleep(delay)

        # All attempts failed
        error_msg = f"Failed to fetch {url_str} after {self.max_retries + 1} attempts"
        if last_exception:
            error_msg += f": {last_exception}"

        logger.error(error_msg)
        raise WebError(error_msg)

    async def extract_content(self, url: str | HttpUrl) -> dict[str, Any]:
        """
        Fetch and extract clean content from a web page.

        Args:
            url: The URL to fetch and extract content from

        Returns:
            Dictionary containing extracted content with keys:
            - title: Page title
            - content: Cleaned text content
            - links: List of absolute URLs found
            - meta_description: Meta description if available
            - word_count: Number of words in content
            - content_length: Character count of original content

        Raises:
            WebError: If fetching or parsing fails
        """
        try:
            # Fetch raw HTML
            html_content = await self.fetch_content(url)
            url_str = str(url)

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract basic information
            title = self._extract_title(soup)
            meta_description = self._extract_meta_description(soup)

            # Clean and extract text content
            cleaned_content = self._clean_html_content(soup)

            # Extract links
            links = self._extract_links(soup, url_str)

            # Calculate metrics
            word_count = len(cleaned_content.split())
            content_length = len(html_content)

            result = {
                "title": title,
                "content": cleaned_content,
                "links": links,
                "meta_description": meta_description,
                "word_count": word_count,
                "content_length": content_length,
            }

            logger.info(
                f"Extracted content from {url_str}: "
                f"{word_count} words, {len(links)} links"
            )

            return result

        except Exception as e:
            if isinstance(e, WebError):
                raise
            error_msg = f"Failed to extract content from {url}: {e}"
            logger.error(error_msg)
            raise WebError(error_msg)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from HTML."""
        # Try different title sources in order of preference
        title_sources = [
            soup.find("title"),
            soup.find("h1"),
            soup.find("meta", {"property": "og:title"}),
            soup.find("meta", {"name": "twitter:title"}),
        ]

        for source in title_sources:
            if source:
                if source.name == "meta":
                    title = source.get("content", "").strip()
                else:
                    title = source.get_text().strip()

                if title:
                    # Clean up title
                    title = re.sub(r"\s+", " ", title)
                    return title[:200]  # Truncate very long titles

        return "Untitled"

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from HTML."""
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            desc = meta_desc.get("content", "").strip()
            return desc[:500]  # Truncate long descriptions

        # Try Open Graph description
        og_desc = soup.find("meta", {"property": "og:description"})
        if og_desc:
            desc = og_desc.get("content", "").strip()
            return desc[:500]

        return ""

    def _clean_html_content(self, soup: BeautifulSoup) -> str:
        """
        Extract and clean text content from HTML.

        This function removes unwanted elements and extracts meaningful
        text content suitable for AI analysis.
        """
        # Remove unwanted elements
        unwanted_tags = [
            "script",
            "style",
            "nav",
            "header",
            "footer",
            "aside",
            "form",
            "button",
            "input",
            "select",
            "textarea",
            "iframe",
            "object",
            "embed",
            "applet",
            "noscript",
            "canvas",
            "svg",
        ]

        for tag_name in unwanted_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Remove elements with common unwanted classes/IDs
        unwanted_selectors = [
            '[class*="ad"]',
            '[class*="advertisement"]',
            '[class*="sidebar"]',
            '[class*="menu"]',
            '[class*="navigation"]',
            '[class*="comment"]',
            '[id*="comment"]',
            '[class*="social"]',
            '[class*="share"]',
            '[class*="related"]',
            '[class*="recommended"]',
        ]

        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Focus on main content areas
        main_content_selectors = [
            "main",
            "article",
            '[role="main"]',
            ".content",
            ".main-content",
            ".post-content",
            ".entry-content",
            ".article-content",
            ".story-body",
        ]

        main_content = None
        for selector in main_content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # Use main content if found, otherwise use body
        content_root = main_content or soup.find("body") or soup

        # Extract text with some structure preservation
        text_parts = []

        for element in content_root.descendants:
            if isinstance(element, Tag):
                # Add line breaks for block elements
                if element.name in [
                    "p",
                    "div",
                    "br",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "li",
                ]:
                    text_parts.append("\n")
            else:
                # Add text content
                text = element.string
                if text:
                    text_parts.append(text.strip())

        # Join and clean up the text
        content = " ".join(text_parts)

        # Clean up whitespace
        content = re.sub(r"\n\s*\n", "\n\n", content)  # Multiple newlines to double
        content = re.sub(r" +", " ", content)  # Multiple spaces to single
        content = content.strip()

        return content

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """Extract and resolve absolute URLs from HTML."""
        links = set()

        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if not href or href.startswith("#"):
                continue

            # Convert relative URLs to absolute
            try:
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)

                # Only include HTTP/HTTPS links
                if parsed.scheme in ("http", "https"):
                    links.add(absolute_url)

            except Exception:
                continue  # Skip invalid URLs

        # Return sorted list (limited to reasonable number)
        return sorted(list(links))[:50]


# Convenience functions for direct use
async def fetch_page_content(url: str | HttpUrl, **kwargs: Any) -> dict[str, Any]:
    """
    Convenience function to fetch and extract content from a single URL.

    Args:
        url: The URL to fetch content from
        **kwargs: Additional arguments passed to WebClient

    Returns:
        Dictionary with extracted content

    Raises:
        WebError: If fetching fails
    """
    async with WebClient(**kwargs) as client:
        return await client.extract_content(url)


async def fetch_multiple_urls(
    urls: list[str | HttpUrl], max_concurrent: int = 5, **kwargs: Any
) -> list[dict[str, Any]]:
    """
    Fetch content from multiple URLs concurrently.

    Args:
        urls: List of URLs to fetch
        max_concurrent: Maximum number of concurrent requests
        **kwargs: Additional arguments passed to WebClient

    Returns:
        List of content dictionaries (same order as input URLs)
        Failed requests return None in their position
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(
        client: WebClient, url: str | HttpUrl
    ) -> dict[str, Any] | None:
        async with semaphore:
            try:
                return await client.extract_content(url)
            except WebError as e:
                logger.warning(f"Failed to fetch {url}: {e}")
                return None

    async with WebClient(**kwargs) as client:
        tasks = [fetch_with_semaphore(client, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return results


# Export public interface
__all__ = [
    "WebClient",
    "WebError",
    "fetch_page_content",
    "fetch_multiple_urls",
]
