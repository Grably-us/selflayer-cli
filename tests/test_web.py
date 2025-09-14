"""Unit tests for SelfLayer web module."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from selflayer import WebError
from selflayer.web import WebClient


class TestWebClient:
    """Test cases for WebClient class."""

    def test_web_client_initialization(self):
        """Test WebClient initialization."""
        client = WebClient()
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.user_agent is not None

    def test_web_client_custom_config(self):
        """Test WebClient with custom configuration."""
        client = WebClient(timeout=60.0, max_retries=5, user_agent="Custom Agent")
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.user_agent == "Custom Agent"

    @pytest.mark.asyncio
    async def test_fetch_content_success(self, sample_html_content):
        """Test successful content fetching."""
        client = WebClient()

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = sample_html_content
            mock_response.content = sample_html_content.encode()
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            content = await client.fetch_content("https://example.com")

            assert content is not None
            assert "Test Article Title" in content
            assert len(content) > 0

    @pytest.mark.asyncio
    async def test_fetch_content_404_error(self):
        """Test handling of 404 errors."""
        client = WebClient()

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=mock_response
            )

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            with pytest.raises(WebError):
                await client.fetch_content("https://example.com/nonexistent")

    @pytest.mark.asyncio
    async def test_fetch_content_timeout(self):
        """Test handling of timeout errors."""
        client = WebClient()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                httpx.TimeoutException("Timeout")
            )

            with pytest.raises(WebError):
                await client.fetch_content("https://slow-site.com")

    @pytest.mark.asyncio
    async def test_fetch_content_connection_error(self):
        """Test handling of connection errors."""
        client = WebClient()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                httpx.ConnectError("Connection failed")
            )

            with pytest.raises(WebError):
                await client.fetch_content("https://unreachable.com")

    @pytest.mark.asyncio
    async def test_extract_content_success(self, sample_html_content):
        """Test successful content extraction."""
        client = WebClient()

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = sample_html_content
            mock_response.content = sample_html_content.encode()
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            result = await client.extract_content("https://example.com")

            assert result is not None
            assert "title" in result
            assert "content" in result
            assert "links" in result
            assert "meta_description" in result
            assert "word_count" in result
            assert "content_length" in result

            assert (
                "Test Article Title" in result["title"]
                or "Test Article Title" in result["content"]
            )
            assert result["word_count"] > 0
            assert result["content_length"] > 0

    @pytest.mark.asyncio
    async def test_extract_content_with_context_manager(self, sample_html_content):
        """Test content extraction using async context manager."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = sample_html_content
            mock_response.content = sample_html_content.encode()
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            async with WebClient() as client:
                result = await client.extract_content("https://example.com")
                assert result is not None
                assert "title" in result

    def test_extract_title_from_various_sources(self):
        """Test title extraction from various HTML sources."""
        client = WebClient()

        # Mock BeautifulSoup parsing internally by testing the private method
        from bs4 import BeautifulSoup

        html = """
        <html>
            <head>
                <title>Page Title</title>
                <meta property="og:title" content="OG Title">
                <meta name="twitter:title" content="Twitter Title">
            </head>
            <body>
                <h1>H1 Title</h1>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "html.parser")
        title = client._extract_title(soup)
        assert title == "Page Title"

    def test_extract_meta_description(self):
        """Test meta description extraction."""
        client = WebClient()

        from bs4 import BeautifulSoup

        html = """
        <html>
            <head>
                <meta name="description" content="Test description">
                <meta property="og:description" content="OG description">
            </head>
        </html>
        """

        soup = BeautifulSoup(html, "html.parser")
        desc = client._extract_meta_description(soup)
        assert desc == "Test description"

    def test_clean_html_content(self):
        """Test HTML content cleaning."""
        client = WebClient()

        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <h1>Title</h1>
                <p>First paragraph</p>
                <p>Second paragraph</p>
                <script>console.log('remove me');</script>
                <nav>Navigation</nav>
                <ul>
                    <li>First list item</li>
                    <li>Second list item</li>
                </ul>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "html.parser")
        content = client._clean_html_content(soup)

        assert "Title" in content
        assert "First paragraph" in content
        assert "Second paragraph" in content
        assert "First list item" in content
        assert "console.log" not in content  # Script should be removed
        assert "Navigation" not in content  # Nav should be removed

    def test_extract_links(self):
        """Test link extraction and resolution."""
        client = WebClient()

        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <a href="https://example.com/absolute">Absolute link</a>
                <a href="/relative/path">Relative link</a>
                <a href="../parent">Parent relative</a>
                <a href="#fragment">Fragment link</a>
                <a href="mailto:test@example.com">Email link</a>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "html.parser")
        links = client._extract_links(soup, "https://example.com/current/page")

        # Should include absolute and resolved relative URLs, but not fragments or mailto
        absolute_links = [link for link in links if link.startswith("http")]
        assert len(absolute_links) > 0
        assert any("https://example.com" in link for link in links)
