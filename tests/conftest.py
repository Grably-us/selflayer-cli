"""Test configuration and fixtures for SelfLayer."""

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

from selflayer.models import SearchResult, WebCard


@pytest.fixture
def api_key():
    """Get API key from environment for testing."""
    return os.getenv("GEMINI_API_KEY", "test_api_key")


@pytest.fixture
def mock_web_card():
    """Mock WebCard for testing."""
    return WebCard(
        title="Test Article",
        url="https://example.com/test",
        large_summary="This is a test article about testing software. It contains important information about best practices and methodologies.",
        facts=[
            "Testing is crucial for software quality",
            "Unit tests should cover edge cases",
            "Integration tests verify system interactions",
        ],
        links=["https://example.com/related", "https://docs.testing.com"],
        dates=["2024-01-15"],
        analysis_confidence=0.85,
        content_length=500,
    )


@pytest.fixture
def mock_search_results():
    """Mock search results for testing."""
    return [
        SearchResult(
            title="Test Result 1",
            url="https://example.com/result1",
            snippet="First test result snippet with relevant information.",
        ),
        SearchResult(
            title="Test Result 2",
            url="https://example.com/result2",
            snippet="Second test result with different content.",
        ),
    ]


@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing web scraping."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Article</title>
        <meta name="description" content="A test article for testing purposes">
    </head>
    <body>
        <article>
            <h1>Test Article Title</h1>
            <p>This is the first paragraph of the test article.</p>
            <p>This is the second paragraph with some <a href="https://example.com">links</a>.</p>
            <ul>
                <li>First list item</li>
                <li>Second list item</li>
            </ul>
            <time datetime="2024-01-15">January 15, 2024</time>
        </article>
    </body>
    </html>
    """


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing HTTP requests."""
    mock = AsyncMock()
    mock.get = AsyncMock()
    mock.post = AsyncMock()
    return mock


@pytest.fixture
def mock_ai_response():
    """Mock AI response for testing."""
    mock = MagicMock()
    mock.output = WebCard(
        title="AI Generated Title",
        url="https://example.com",
        large_summary="AI generated summary of the content.",
        facts=["Fact 1", "Fact 2"],
        links=["https://related.com"],
        dates=["2024-01-15"],
        analysis_confidence=0.9,
        content_length=300,
    )
    return mock


@pytest.fixture(autouse=True)
def setup_env():
    """Set up environment variables for testing."""
    os.environ.setdefault("GEMINI_API_KEY", "test_key_for_unit_tests")
    os.environ.setdefault("SELFLAYER_LOG_LEVEL", "DEBUG")
