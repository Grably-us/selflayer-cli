"""
Pydantic models for SelfLayer application.

This module defines the core data models used throughout the SelfLayer application,
including WebCard for analyzed content, SearchResult for search data,
and AppState for managing application state.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class SearchResult(BaseModel):
    """
    Represents a single search result from web search engines.

    This model captures the essential information returned by search engines
    like DuckDuckGo, providing a structured representation of search hits.
    """

    title: str = Field(..., description="The title of the search result")
    url: HttpUrl = Field(..., description="The URL of the search result")
    snippet: str = Field(
        default="", description="Brief description or snippet from the search result"
    )
    source: str = Field(
        default="unknown",
        description="The search engine or source that provided this result",
    )
    rank: int = Field(
        default=0, ge=0, description="Position in search results (0-based index)"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty and reasonably sized."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()[:200]  # Truncate very long titles

    @field_validator("snippet")
    @classmethod
    def validate_snippet(cls, v: str) -> str:
        """Clean and validate snippet text."""
        return v.strip()[:500]  # Truncate very long snippets


class WebCard(BaseModel):
    """
    Represents analyzed web content with AI-extracted information.

    This is the primary data structure for displaying analyzed web pages.
    It contains structured information extracted by AI models from raw web content.
    """

    title: str = Field(..., description="The main title of the webpage")
    url: HttpUrl = Field(..., description="The source URL of the content")
    large_summary: str = Field(..., description="A detailed summary of the content")
    dates: list[str] = Field(
        default_factory=list, description="Any relevant dates found on the page"
    )
    facts: list[str] = Field(
        default_factory=list, description="A list of key facts or bullet points"
    )
    links: list[str] = Field(
        default_factory=list, description="A list of relevant URLs or references found"
    )
    fetched_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this content was fetched and analyzed",
    )
    content_length: int = Field(
        default=0, ge=0, description="Length of the original content in characters"
    )
    analysis_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for the AI analysis (0.0-1.0)",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty and properly formatted."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("large_summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        """Ensure summary is meaningful."""
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Summary too short - minimum 10 characters")
        return v.strip()

    @field_validator("facts")
    @classmethod
    def validate_facts(cls, v: list[str]) -> list[str]:
        """Clean and validate facts list."""
        return [fact.strip() for fact in v if fact and fact.strip()]

    @field_validator("links")
    @classmethod
    def validate_links(cls, v: list[str]) -> list[str]:
        """Validate and clean links list."""
        validated_links = []
        for link in v:
            if link and link.strip():
                link = link.strip()
                # Basic URL validation
                try:
                    parsed = urlparse(link)
                    if parsed.scheme and parsed.netloc:
                        validated_links.append(link)
                except Exception:
                    continue  # Skip invalid URLs
        return validated_links

    @model_validator(mode="after")
    def validate_card(self) -> "WebCard":
        """Additional validation across fields."""
        # Ensure we have some meaningful content
        if not any([self.large_summary, self.facts, self.links]):
            raise ValueError("WebCard must contain at least summary, facts, or links")
        return self

    def to_display_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary optimized for display purposes.

        Returns:
            Dictionary with formatted data suitable for TUI display
        """
        return {
            "title": self.title,
            "url": str(self.url),
            "summary": self.large_summary,
            "facts_count": len(self.facts),
            "links_count": len(self.links),
            "dates_count": len(self.dates),
            "fetched": self.fetched_at.strftime("%Y-%m-%d %H:%M UTC"),
            "confidence": f"{self.analysis_confidence:.2%}",
        }

    def get_preview(self, max_length: int = 150) -> str:
        """
        Get a preview of the content for display in lists.

        Args:
            max_length: Maximum length of the preview text

        Returns:
            Truncated summary suitable for preview display
        """
        preview = self.large_summary
        if len(preview) > max_length:
            preview = preview[: max_length - 3] + "..."
        return preview


class AIResponse(BaseModel):
    """
    Represents a response from AI analysis operations.

    This model captures both successful AI responses and error states,
    providing a consistent interface for handling AI operations.
    """

    success: bool = Field(..., description="Whether the AI operation succeeded")
    content: WebCard | None = Field(
        default=None, description="The analyzed content (if successful)"
    )
    error_message: str = Field(
        default="", description="Error message (if unsuccessful)"
    )
    model_used: str = Field(
        default="unknown", description="The AI model used for analysis"
    )
    processing_time: float = Field(
        default=0.0, ge=0.0, description="Time taken for processing in seconds"
    )
    tokens_used: int = Field(
        default=0, ge=0, description="Number of tokens consumed (if applicable)"
    )

    @model_validator(mode="after")
    def validate_response(self) -> "AIResponse":
        """Ensure response state is consistent."""
        if self.success and self.content is None:
            raise ValueError("Successful response must include content")
        if not self.success and not self.error_message:
            raise ValueError("Failed response must include error message")
        return self

    def to_summary_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for summary display.

        Returns:
            Dictionary with response summary information
        """
        return {
            "success": self.success,
            "model": self.model_used,
            "processing_time": f"{self.processing_time:.2f}s",
            "tokens_used": self.tokens_used,
            "error": self.error_message if not self.success else None,
        }


class AppState(BaseModel):
    """
    Represents the current state of the SelfTUI application.

    This model tracks the application's current state including API keys,
    search results, and active content for state management in the TUI.
    """

    api_key_set: bool = Field(
        default=False, description="Whether API key is configured"
    )
    current_search_query: str = Field(default="", description="Last search query")
    search_results: list[SearchResult] = Field(
        default_factory=list, description="Current search results"
    )
    active_cards: list[WebCard] = Field(
        default_factory=list, description="Currently displayed web cards"
    )
    last_error: str = Field(default="", description="Last error message")
    session_start: datetime = Field(
        default_factory=datetime.utcnow, description="When the session started"
    )

    def add_search_results(self, results: list[SearchResult]) -> None:
        """Add new search results to the state."""
        self.search_results = results
        self.last_error = ""  # Clear any previous errors

    def add_web_card(self, card: WebCard) -> None:
        """Add a new web card to active cards."""
        # Remove any existing card with the same URL
        self.active_cards = [c for c in self.active_cards if c.url != card.url]
        self.active_cards.append(card)
        self.last_error = ""  # Clear any previous errors

    def clear_results(self) -> None:
        """Clear all current results and cards."""
        self.search_results = []
        self.active_cards = []
        self.current_search_query = ""
        self.last_error = ""

    def set_error(self, error: str) -> None:
        """Set an error message in the state."""
        self.last_error = error

    def get_session_duration(self) -> str:
        """Get formatted session duration."""
        duration = datetime.utcnow() - self.session_start
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


# Export all models
__all__ = [
    "SearchResult",
    "WebCard",
    "AIResponse",
    "AppState",
]
