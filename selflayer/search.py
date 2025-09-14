"""
Web search functionality for SelfLayer using DuckDuckGo.

This module provides search capabilities using DuckDuckGo's search engine,
returning structured results that can be used for further content analysis.
Includes caching and rate limiting for efficient searching.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from ddgs import DDGS
from pydantic import HttpUrl

from . import SearchError
from .models import SearchResult

# Configure module logger
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MAX_RESULTS = 10
DEFAULT_REGION = "us-en"
DEFAULT_SAFESEARCH = "moderate"
DEFAULT_TIME_LIMIT = None  # No time limit


class SearchCache:
    """
    Simple in-memory cache for search results to avoid redundant queries.

    This cache stores search results for a configurable duration to improve
    performance and reduce load on the search service.
    """

    def __init__(self, cache_duration: timedelta = timedelta(minutes=15)):
        """
        Initialize the search cache.

        Args:
            cache_duration: How long to keep cached results
        """
        self.cache: dict[str, tuple[datetime, list[SearchResult]]] = {}
        self.cache_duration = cache_duration

    def get(self, query: str, max_results: int) -> list[SearchResult] | None:
        """
        Get cached search results if available and not expired.

        Args:
            query: The search query
            max_results: Maximum number of results requested

        Returns:
            Cached results if available, None otherwise
        """
        cache_key = self._make_key(query, max_results)

        if cache_key in self.cache:
            cached_time, results = self.cache[cache_key]

            # Check if cache is still valid
            if datetime.utcnow() - cached_time < self.cache_duration:
                logger.debug(f"Cache hit for query: {query}")
                return results
            else:
                # Remove expired entry
                del self.cache[cache_key]
                logger.debug(f"Cache expired for query: {query}")

        return None

    def set(self, query: str, max_results: int, results: list[SearchResult]) -> None:
        """
        Cache search results.

        Args:
            query: The search query
            max_results: Maximum number of results requested
            results: Search results to cache
        """
        cache_key = self._make_key(query, max_results)
        self.cache[cache_key] = (datetime.utcnow(), results)
        logger.debug(f"Cached {len(results)} results for query: {query}")

        # Simple cleanup: remove old entries if cache gets too large
        if len(self.cache) > 100:
            self._cleanup_old_entries()

    def clear(self) -> None:
        """Clear all cached results."""
        self.cache.clear()
        logger.debug("Search cache cleared")

    def _make_key(self, query: str, max_results: int) -> str:
        """Generate cache key from query parameters."""
        return f"{query.lower().strip()}:{max_results}"

    def _cleanup_old_entries(self) -> None:
        """Remove oldest cache entries to keep memory usage reasonable."""
        # Remove entries older than half the cache duration
        cutoff_time = datetime.utcnow() - (self.cache_duration / 2)

        keys_to_remove = [
            key
            for key, (cached_time, _) in self.cache.items()
            if cached_time < cutoff_time
        ]

        for key in keys_to_remove:
            del self.cache[key]

        logger.debug(f"Cleaned up {len(keys_to_remove)} old cache entries")


class DuckDuckGoSearcher:
    """
    DuckDuckGo search client with caching and error handling.

    This class provides a high-level interface for performing web searches
    using DuckDuckGo with built-in caching, rate limiting, and result
    normalization.
    """

    def __init__(
        self,
        region: str = DEFAULT_REGION,
        safesearch: str = DEFAULT_SAFESEARCH,
        time_limit: str | None = DEFAULT_TIME_LIMIT,
        enable_cache: bool = True,
        cache_duration: timedelta = timedelta(minutes=15),
    ) -> None:
        """
        Initialize the DuckDuckGo searcher.

        Args:
            region: Search region (e.g., "us-en", "uk-en")
            safesearch: Safe search setting ("strict", "moderate", "off")
            time_limit: Time limit for results ("d", "w", "m", "y", None)
            enable_cache: Whether to enable result caching
            cache_duration: How long to cache results
        """
        self.region = region
        self.safesearch = safesearch
        self.time_limit = time_limit

        # Initialize cache if enabled
        self.cache = SearchCache(cache_duration) if enable_cache else None

        # Rate limiting: track last search time
        self.last_search_time = datetime.min
        self.min_search_interval = timedelta(milliseconds=500)  # 500ms between searches

    async def search(
        self, query: str, max_results: int = DEFAULT_MAX_RESULTS
    ) -> list[SearchResult]:
        """
        Perform a web search using DuckDuckGo.

        Args:
            query: The search query string
            max_results: Maximum number of results to return

        Returns:
            List of SearchResult objects

        Raises:
            SearchError: If the search fails
        """
        if not query or not query.strip():
            raise SearchError("Search query cannot be empty")

        query = query.strip()

        # Check cache first
        if self.cache:
            cached_results = self.cache.get(query, max_results)
            if cached_results is not None:
                return cached_results

        try:
            # Rate limiting: ensure minimum interval between searches
            time_since_last = datetime.utcnow() - self.last_search_time
            if time_since_last < self.min_search_interval:
                sleep_time = (
                    self.min_search_interval - time_since_last
                ).total_seconds()
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

            # Perform the search
            logger.info(f"Searching DuckDuckGo for: {query}")
            results = await self._execute_search(query, max_results)

            # Update last search time
            self.last_search_time = datetime.utcnow()

            # Cache results if caching is enabled
            if self.cache:
                self.cache.set(query, max_results, results)

            logger.info(f"Found {len(results)} results for query: {query}")
            return results

        except Exception as e:
            error_msg = f"DuckDuckGo search failed for '{query}': {e}"
            logger.error(error_msg)
            raise SearchError(error_msg)

    async def _execute_search(self, query: str, max_results: int) -> list[SearchResult]:
        """
        Execute the actual DuckDuckGo search in a thread pool.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        # Run the blocking DuckDuckGo search in a thread pool
        loop = asyncio.get_event_loop()

        def search_sync() -> list[dict[str, Any]]:
            with DDGS() as ddgs:
                return list(
                    ddgs.text(
                        query,
                        region=self.region,
                        safesearch=self.safesearch,
                        timelimit=self.time_limit,
                        max_results=max_results,
                    )
                )

        # Execute in thread pool to avoid blocking
        raw_results = await loop.run_in_executor(None, search_sync)

        # Convert raw results to SearchResult objects
        search_results = []
        for i, raw_result in enumerate(raw_results):
            try:
                result = self._parse_search_result(raw_result, i)
                if result:
                    search_results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse search result {i}: {e}")
                continue

        return search_results

    def _parse_search_result(
        self, raw_result: dict[str, Any], rank: int
    ) -> SearchResult | None:
        """
        Parse a raw DuckDuckGo result into a SearchResult object.

        Args:
            raw_result: Raw result dictionary from DuckDuckGo
            rank: Position in search results

        Returns:
            SearchResult object or None if parsing fails
        """
        try:
            # DuckDuckGo result format: {"title", "href", "body"}
            title = raw_result.get("title", "").strip()
            url = raw_result.get("href", "").strip()
            snippet = raw_result.get("body", "").strip()

            if not title or not url:
                logger.debug(f"Skipping result with missing title or URL: {raw_result}")
                return None

            # Validate URL format
            try:
                HttpUrl(url)  # This will raise if invalid
            except Exception:
                logger.debug(f"Skipping result with invalid URL: {url}")
                return None

            return SearchResult(
                title=title,
                url=HttpUrl(url),
                snippet=snippet,
                source="duckduckgo",
                rank=rank,
            )

        except Exception as e:
            logger.warning(f"Error parsing search result: {e}")
            return None


# Global searcher instance for convenience
_default_searcher: DuckDuckGoSearcher | None = None


def get_default_searcher() -> DuckDuckGoSearcher:
    """Get or create the default searcher instance."""
    global _default_searcher
    if _default_searcher is None:
        _default_searcher = DuckDuckGoSearcher()
    return _default_searcher


async def search_web(
    query: str, max_results: int = DEFAULT_MAX_RESULTS, **kwargs: Any
) -> list[SearchResult]:
    """
    Convenience function to search the web using the default searcher.

    Args:
        query: The search query string
        max_results: Maximum number of results to return
        **kwargs: Additional arguments passed to DuckDuckGoSearcher constructor

    Returns:
        List of SearchResult objects

    Raises:
        SearchError: If the search fails

    Example:
        >>> results = await search_web("python tutorial", max_results=5)
        >>> for result in results:
        ...     print(f"{result.title}: {result.url}")
    """
    if kwargs:
        # Create temporary searcher with custom settings
        searcher = DuckDuckGoSearcher(**kwargs)
    else:
        # Use default searcher
        searcher = get_default_searcher()

    return await searcher.search(query, max_results)


async def search_multiple_queries(
    queries: list[str],
    max_results_per_query: int = DEFAULT_MAX_RESULTS,
    max_concurrent: int = 3,
) -> dict[str, list[SearchResult]]:
    """
    Search multiple queries concurrently.

    Args:
        queries: List of search queries
        max_results_per_query: Maximum results per query
        max_concurrent: Maximum number of concurrent searches

    Returns:
        Dictionary mapping queries to their search results

    Example:
        >>> queries = ["python tutorial", "web scraping"]
        >>> results = await search_multiple_queries(queries)
        >>> for query, search_results in results.items():
        ...     print(f"{query}: {len(search_results)} results")
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def search_with_semaphore(query: str) -> tuple[str, list[SearchResult]]:
        async with semaphore:
            try:
                results = await search_web(query, max_results_per_query)
                return query, results
            except SearchError as e:
                logger.warning(f"Search failed for '{query}': {e}")
                return query, []

    # Execute searches concurrently
    tasks = [search_with_semaphore(query) for query in queries]
    results = await asyncio.gather(*tasks)

    # Convert to dictionary
    return dict(results)


# Export public interface
__all__ = [
    "DuckDuckGoSearcher",
    "SearchCache",
    "SearchError",
    "search_web",
    "search_multiple_queries",
    "get_default_searcher",
]
