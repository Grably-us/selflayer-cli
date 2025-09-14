"""
SelfLayer TUI - AI-Powered Terminal User Interface for Knowledge Management.

A modern, intelligent terminal interface that connects to the SelfLayer API
for comprehensive knowledge management, document processing, note-taking,
and AI-powered search and analysis.

Key Components:
- models: Pydantic data models for SelfLayer API responses
- client: SelfLayer API client with comprehensive error handling
- renderers: Rich-powered beautiful card and table renderers
- tui: Main terminal interface with all commands
"""

from __future__ import annotations

__version__ = "2.1.0"
__author__ = "Anton Vice <anton@selflayer.com>"
__description__ = (
    "AI-powered terminal user interface for SelfLayer knowledge management"
)


# Core exceptions
class SelfLayerError(Exception):
    """Base exception for SelfLayer application."""

    pass


class APIError(SelfLayerError):
    """Raised when API operations fail."""

    pass


class WebError(SelfLayerError):
    """Raised when web operations fail."""

    pass


class SearchError(SelfLayerError):
    """Raised when search operations fail."""

    pass


# Package-level exports
__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "SelfLayerError",
    "APIError",
    "WebError",
    "SearchError",
]
