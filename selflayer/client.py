"""
SelfLayer API Client for TUI integration.

This module provides a comprehensive async HTTP client for interacting with
the SelfLayer API, including support for streaming responses, file uploads,
and rich error handling.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, AsyncIterator, Dict

import httpx
from rich.console import Console
from rich.panel import Panel

from . import APIError

# Configure module logger
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8001/api/v1"
DEFAULT_TIMEOUT = 30.0


class SelfLayerAPIClient:
    """
    Async HTTP client for SelfLayer API with comprehensive error handling.

    Provides methods for all API operations with built-in retry logic,
    streaming support, and rich error formatting for the TUI.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the SelfLayer API client.

        Args:
            api_key: SelfLayer API key (uses SELFLAYER_API_KEY env var if None)
            base_url: Base URL for the SelfLayer API
            timeout: Request timeout in seconds

        Raises:
            APIError: If API key is not provided or invalid
        """
        # Get API key from parameter, config, or environment
        if api_key:
            self.api_key = api_key
        else:
            from .config import get_effective_api_key

            self.api_key = get_effective_api_key()

        if not self.api_key:
            raise APIError(
                "SelfLayer API key required. Use /key command to set it, "
                "or set SELFLAYER_API_KEY environment variable."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Setup headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SelfTUI/2.0.0 (SelfLayer Terminal Client)",
        }

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            follow_redirects=True,
        )

        logger.info("SelfLayer API client initialized")

    async def __aenter__(self) -> "SelfLayerAPIClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if hasattr(self, "client"):
            await self.client.aclose()

    def _handle_error(self, response: httpx.Response) -> Panel:
        """
        Convert API error response to rich Panel for TUI display.

        Args:
            response: HTTP response object

        Returns:
            Rich Panel with formatted error message
        """
        try:
            error_data = response.json()
            error_msg = error_data.get("detail", f"HTTP {response.status_code}")
        except Exception:
            error_msg = f"HTTP {response.status_code}: {response.text}"

        # Create appropriate error panel based on status code
        if response.status_code == 401:
            title = "[red]Authentication Error[/red]"
            message = f"[red]{error_msg}[/red]\n\nCheck your SELFLAYER_API_KEY environment variable."
        elif response.status_code == 403:
            title = "[red]Permission Denied[/red]"
            message = f"[red]{error_msg}[/red]\n\nYour API key may not have sufficient permissions."
        elif response.status_code == 404:
            title = "[yellow]Not Found[/yellow]"
            message = f"[yellow]{error_msg}[/yellow]"
        elif response.status_code == 422:
            title = "[red]Validation Error[/red]"
            message = f"[red]{error_msg}[/red]"
        elif response.status_code == 429:
            title = "[yellow]Rate Limited[/yellow]"
            message = f"[yellow]{error_msg}[/yellow]\n\nPlease wait and try again."
        else:
            title = "[red]API Error[/red]"
            message = f"[red]{error_msg}[/red]"

        return Panel(
            message,
            title=title,
            border_style="red" if response.status_code >= 500 else "yellow",
            padding=(1, 2),
        )

    async def get(
        self, endpoint: str, params: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Perform GET request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"GET {url} with params: {params}")
            response = await self.client.get(url, params=params)

            if not response.is_success:
                error_panel = self._handle_error(response)
                console = Console()
                console.print(error_panel)
                raise APIError(f"API request failed: {response.status_code}")

            return response.json()

        except httpx.TimeoutException:
            raise APIError(f"Request timeout for {endpoint}")
        except httpx.RequestError as e:
            raise APIError(f"Request error for {endpoint}: {e}")

    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any] | None = None,
        files: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Perform POST request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON payload
            files: File upload data

        Returns:
            JSON response data

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"POST {url} with data: {json_data}")

            if files:
                # For file uploads, don't set Content-Type header
                headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
                response = await self.client.post(
                    url, json=json_data, files=files, headers=headers
                )
            else:
                response = await self.client.post(url, json=json_data)

            if not response.is_success:
                error_panel = self._handle_error(response)
                console = Console()
                console.print(error_panel)
                raise APIError(f"API request failed: {response.status_code}")

            return response.json()

        except httpx.TimeoutException:
            raise APIError(f"Request timeout for {endpoint}")
        except httpx.RequestError as e:
            raise APIError(f"Request error for {endpoint}: {e}")

    async def put(
        self, endpoint: str, json_data: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Perform PUT request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON payload

        Returns:
            JSON response data

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"PUT {url} with data: {json_data}")
            response = await self.client.put(url, json=json_data)

            if not response.is_success:
                error_panel = self._handle_error(response)
                console = Console()
                console.print(error_panel)
                raise APIError(f"API request failed: {response.status_code}")

            return response.json()

        except httpx.TimeoutException:
            raise APIError(f"Request timeout for {endpoint}")
        except httpx.RequestError as e:
            raise APIError(f"Request error for {endpoint}: {e}")

    async def patch(
        self, endpoint: str, json_data: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Perform PATCH request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON payload

        Returns:
            JSON response data

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"PATCH {url} with data: {json_data}")
            response = await self.client.patch(url, json=json_data)

            if not response.is_success:
                error_panel = self._handle_error(response)
                console = Console()
                console.print(error_panel)
                raise APIError(f"API request failed: {response.status_code}")

            return response.json()

        except httpx.TimeoutException:
            raise APIError(f"Request timeout for {endpoint}")
        except httpx.RequestError as e:
            raise APIError(f"Request error for {endpoint}: {e}")

    async def delete(self, endpoint: str) -> Dict[str, Any] | None:
        """
        Perform DELETE request to the API.

        Args:
            endpoint: API endpoint (without base URL)

        Returns:
            JSON response data or None for 204 responses

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"DELETE {url}")
            response = await self.client.delete(url)

            if not response.is_success:
                error_panel = self._handle_error(response)
                console = Console()
                console.print(error_panel)
                raise APIError(f"API request failed: {response.status_code}")

            if response.status_code == 204:
                return None
            return response.json()

        except httpx.TimeoutException:
            raise APIError(f"Request timeout for {endpoint}")
        except httpx.RequestError as e:
            raise APIError(f"Request error for {endpoint}: {e}")

    async def stream(
        self, endpoint: str, json_data: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream POST request to the API (for streaming AI responses).

        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON payload

        Yields:
            Parsed JSON chunks from the stream

        Raises:
            APIError: If stream fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"STREAM POST {url} with data: {json_data}")

            # Add stream parameter to request
            stream_data = {**json_data, "stream": True}

            async with self.client.stream("POST", url, json=stream_data) as response:
                if not response.is_success:
                    error_panel = self._handle_error(response)
                    console = Console()
                    console.print(error_panel)
                    raise APIError(f"API stream failed: {response.status_code}")

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            # Handle Server-Sent Events format
                            if line.startswith("data: "):
                                json_str = line[6:]  # Remove "data: " prefix
                                if json_str.strip() == "[DONE]":
                                    break
                                chunk = json.loads(json_str)
                                yield chunk
                            else:
                                # Handle plain JSON lines
                                chunk = json.loads(line)
                                yield chunk
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON: {line}")
                            continue

        except httpx.TimeoutException:
            raise APIError(f"Stream timeout for {endpoint}")
        except httpx.RequestError as e:
            raise APIError(f"Stream error for {endpoint}: {e}")

    # Convenience methods for specific API endpoints

    async def ask(
        self, query: str, context_limit: int = 10, stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[Dict[str, Any]]:
        """Ask the AI assistant a question."""
        data = {"query": query, "context_limit": context_limit}

        if stream:
            return self.stream("exocortex/ask", data)
        else:
            return await self.post("exocortex/ask", data)

    async def search(self, query: str) -> Dict[str, Any]:
        """Search the knowledge base."""
        return await self.get("search", {"query": query})

    async def list_documents(self) -> list[Dict[str, Any]]:
        """List all documents."""
        response = await self.get("documents/")
        return response if isinstance(response, list) else response.get("documents", [])

    async def upload_document(
        self, file_path: str, visibility: str = "personal"
    ) -> Dict[str, Any]:
        """Upload a document for processing."""
        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f, "application/octet-stream")
            }
            data = {"visibility": visibility}
            return await self.post("documents/ingest", json_data=data, files=files)

    async def delete_document(self, doc_id: str) -> Dict[str, Any] | None:
        """Delete a document."""
        return await self.delete(f"documents/{doc_id}")

    async def list_notes(self) -> list[Dict[str, Any]]:
        """List all notes."""
        response = await self.get("notes/")
        return response if isinstance(response, list) else response.get("notes", [])

    async def create_note(
        self, title: str, content: str, tags: list[str] | None = None
    ) -> Dict[str, Any]:
        """Create a new note."""
        data = {
            "title": title,
            "content": content,
            "tags": tags or [],
            "visibility": "personal",
        }
        return await self.post("notes/", data)

    async def update_note(
        self, note_id: str, title: str | None = None, content: str | None = None
    ) -> Dict[str, Any]:
        """Update an existing note."""
        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        return await self.put(f"notes/{note_id}", data)

    async def delete_note(self, note_id: str) -> Dict[str, Any] | None:
        """Delete a note."""
        return await self.delete(f"notes/{note_id}")

    async def list_notifications(self) -> list[Dict[str, Any]]:
        """Get all notifications."""
        response = await self.get("notifications/")
        return (
            response
            if isinstance(response, list)
            else response.get("notifications", [])
        )

    async def mark_notification_read(self, notification_id: str) -> Dict[str, Any]:
        """Mark a notification as read."""
        return await self.post(f"notifications/{notification_id}/read")

    async def mark_all_notifications_read(self) -> Dict[str, Any]:
        """Mark all notifications as read."""
        return await self.post("notifications/read-all")

    async def list_integrations(self) -> list[Dict[str, Any]]:
        """List all integration connections."""
        response = await self.get("integrations/connections")
        return (
            response if isinstance(response, list) else response.get("connections", [])
        )

    async def connect_integration(self, provider: str) -> Dict[str, Any]:
        """Connect a new integration."""
        return await self.post(f"integrations/{provider}/connect")

    async def disconnect_integration(self, connection_id: str) -> Dict[str, Any] | None:
        """Disconnect an integration."""
        return await self.delete(f"integrations/connections/{connection_id}")

    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        return await self.get("profile")

    async def surface_memory(self, partial_text: str = "") -> Dict[str, Any]:
        """Surface random memories based on partial text."""
        return await self.get("surface", {"partial_text": partial_text})

    async def get_persona_briefing(
        self,
        email: str = None,
        name: str = None,
        company: str = None,
        title: str = None,
    ) -> Dict[str, Any]:
        """Get persona briefing (RMS) for a person."""
        data = {}
        if email:
            data["email"] = email
        if name:
            data["name"] = name
        if company:
            data["company"] = company
        if title:
            data["title"] = title

        if not data:
            raise ValueError(
                "At least one of email, name, company, or title must be provided"
            )

        return await self.post("agent/persona", data)

    async def list_automations(self) -> list[Dict[str, Any]]:
        """List all automations."""
        response = await self.get("automations")
        return (
            response if isinstance(response, list) else response.get("automations", [])
        )

    async def run_automation(self, automation_id: str) -> Dict[str, Any]:
        """Run an automation manually."""
        return await self.post(f"automations/{automation_id}/run")

    async def toggle_automation(
        self, automation_id: str, enabled: bool
    ) -> Dict[str, Any]:
        """Enable or disable an automation."""
        data = {"is_enabled": enabled}
        return await self.patch(f"automations/{automation_id}", data)


# Global API client instance
_api_client: SelfLayerAPIClient | None = None


def get_api_client() -> SelfLayerAPIClient:
    """Get or create the global API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = SelfLayerAPIClient()
    return _api_client


# Export public interface
__all__ = [
    "SelfLayerAPIClient",
    "get_api_client",
    "APIError",
]
