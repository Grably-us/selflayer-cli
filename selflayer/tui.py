"""
Main CLI interface for SelfLayer using Rich for formatting and SelfLayer API.

This module implements the completely reworked terminal interface for SelfLayer,
featuring beautiful Rich formatting, comprehensive API integration, and all the
new commands for documents, notes, integrations, notifications, and AI assistant.
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

from . import APIError
from .client import SelfLayerAPIClient, get_api_client
from .models import AppState, Profile, SearchResult
from .renderers import (
    render_ask_response,
    render_document_card,
    render_documents_list,
    render_error_panel,
    render_integrations_list,
    render_note_card,
    render_notes_list,
    render_notifications_list,
    render_profile_card,
    render_search_results,
    render_streaming_response,
    render_success_panel,
)

# Configure module logger
logger = logging.getLogger(__name__)

# SelfLayer ASCII Art
SELFLAYER_ART = """
███████╗███████╗██╗     ███████╗██╗      █████╗ ██╗   ██╗███████╗██████╗
██╔════╝██╔════╝██║     ██╔════╝██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗
███████╗█████╗  ██║     █████╗  ██║     ███████║ ╚████╔╝ █████╗  ██████╔╝
╚════██║██╔══╝  ██║     ██╔══╝  ██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗
███████║███████╗███████╗██║     ███████╗██║  ██║   ██║   ███████╗██║  ██║
╚══════╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def render_welcome(has_api_key: bool = False, profile: Profile | None = None) -> Panel:
    """Render the welcome message with ASCII art and instructions."""

    if has_api_key and profile:
        greeting = profile.get_greeting()
        api_status = f"[bold green]✓ Connected as {profile.name}[/bold green]"
        getting_started = """[bold cyan]Ready to go![/bold cyan]
• [bold]/ask <question>[/bold] - Ask AI assistant
• [bold]/search <query>[/bold] - Search your knowledge
• [bold]/d[/bold] - Documents • [bold]/n[/bold] - Notes • [bold]/i[/bold] - Integrations"""
    elif has_api_key:
        greeting = "Welcome to SelfLayer!"
        api_status = "[bold green]✓ API Key Configured[/bold green]"
        getting_started = """[bold cyan]Ready to go![/bold cyan]
• [bold]/ask <question>[/bold] - Ask AI assistant
• [bold]/search <query>[/bold] - Search your knowledge
• [bold]/d[/bold] - Documents • [bold]/n[/bold] - Notes • [bold]/i[/bold] - Integrations"""
    else:
        greeting = "Welcome to SelfLayer!"
        api_status = "[bold red]✗ API Key Required[/bold red]"
        getting_started = """[bold cyan]Getting Started:[/bold cyan]
• Set API key: [bold]/key sl_live_your_api_key_here[/bold]
• Or set environment: [bold]SELFLAYER_API_KEY[/bold]"""

    welcome_content = f"""[bold magenta]{SELFLAYER_ART}[/bold magenta]

[bold]{greeting}[/bold]

Your AI-powered knowledge management and research assistant.

{api_status}

{getting_started}

Type [bold cyan]/h[/bold cyan] for help • [bold cyan]/q[/bold cyan] to quit"""

    return Panel(
        welcome_content,
        title="[bold green]SelfLayer TUI v2.0 - AI-Powered Knowledge Management[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def render_help() -> Panel:
    """Render comprehensive help information."""
    help_content = """[bold magenta]SelfLayer Commands Reference[/bold magenta]

[bold cyan]🔑 Setup:[/bold cyan]
• [bold]/key[/bold] (or [bold]/k[/bold]) - Show API key status
• [bold]/key <api_key>[/bold] - Set SelfLayer API key
• [bold]/key clear[/bold] - Clear stored API key
  Example: /key sl_live_your_api_key_here

[bold cyan]🤖 AI & Search:[/bold cyan]
• [bold]/ask <question>[/bold] (or [bold]/a[/bold])
  Ask the AI assistant anything about your knowledge base
  Example: /ask What are my recent project notes?

• [bold]/search <query>[/bold] (or [bold]/s[/bold])
  Search across documents, notes, and knowledge graph
  Example: /search machine learning projects

[bold cyan]📄 Document Management:[/bold cyan]
• [bold]/documents[/bold] or [bold]/d[/bold] - List all documents
• [bold]/d new /path/to/file[/bold] - Upload and process document
• [bold]/d 1[/bold] - View details for document #1
• [bold]/d delete 1[/bold] - Delete document #1

[bold cyan]📝 Notes Management:[/bold cyan]
• [bold]/notes[/bold] or [bold]/n[/bold] - List all notes
• [bold]/n new "Title" "Content here"[/bold] - Create new note
• [bold]/n 1[/bold] - View details for note #1
• [bold]/n edit 1 "Updated content"[/bold] - Edit note #1
• [bold]/n delete 1[/bold] - Delete note #1

[bold cyan]🔗 Integrations:[/bold cyan]
• [bold]/integrations[/bold] or [bold]/i[/bold] - List connections
• [bold]/i connect gmail[/bold] - Connect Gmail account
• [bold]/i connect google_calendar[/bold] - Connect Google Calendar
• [bold]/i connect google_drive[/bold] - Connect Google Drive
• [bold]/i disconnect 1[/bold] - Disconnect integration #1

[bold cyan]📢 Notifications:[/bold cyan]
• [bold]/notifications[/bold] or [bold]/notifs[/bold] - View all notifications
• [bold]/notifs read 1[/bold] - Mark notification #1 as read
• [bold]/notifs clear[/bold] - Mark all as read

[bold cyan]🔮 Advanced:[/bold cyan]
• [bold]/rms <email|name|company>[/bold] or [bold]/r[/bold] - Relationship Micro-Summary
  Get a briefing about a person or company from your knowledge
  Example: /rms anton96vice@gmail.com or /rms "SelfLayer"
• [bold]/clear[/bold] or [bold]/c[/bold] - Clear screen
• [bold]/help[/bold] or [bold]/h[/bold] - Show this help
• [bold]/quit[/bold] or [bold]/q[/bold] - Exit application

[bold yellow]Tips:[/bold yellow]
• Use numbers to reference items: [cyan]/d 1[/cyan], [cyan]/n edit 2[/cyan]
• All operations show beautiful progress indicators
• Streaming responses for AI conversations
• Rich formatting for all data types"""

    return Panel(
        help_content,
        title="[bold green]Help & Documentation[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


class SelfLayerCLI:
    """Command-line interface for SelfLayer with comprehensive API integration."""

    def __init__(self) -> None:
        """Initialize the CLI with state and console."""
        self.console = Console()
        self.app_state = AppState()
        self.client: SelfLayerAPIClient | None = None
        self.running = True

        # Try to initialize API client
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize API client and fetch profile if possible."""
        try:
            from .config import get_effective_api_key

            api_key = get_effective_api_key()

            if api_key:
                self.client = get_api_client()
                logger.info("API client initialized successfully")
            else:
                logger.info("No API key found, client not initialized")
                self.client = None
        except APIError as e:
            logger.warning(f"Failed to initialize API client: {e}")
            self.client = None

    async def _fetch_profile(self) -> None:
        """Fetch and cache user profile."""
        if not self.client:
            return

        try:
            profile_data = await self.client.get_profile()
            self.app_state.set_profile(profile_data)
            logger.info("Profile loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load profile: {e}")

    def parse_command(self, raw: str) -> tuple[str, list[str]]:
        """Parse a raw command input into command and arguments."""
        parts = raw.strip().split()
        if not parts:
            return "", []

        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        return command, args

    async def run(self) -> None:
        """Run the main command loop."""
        # Fetch profile if we have a client
        if self.client:
            await self._fetch_profile()

        clear_screen()
        self.console.print(
            render_welcome(
                has_api_key=bool(self.client), profile=self.app_state.user_profile
            )
        )

        # Show profile card if we have profile data
        if self.app_state.user_profile:
            self.console.print()
            self.console.print(render_profile_card(self.app_state.user_profile))

        self.console.print()

        while self.running:
            try:
                # Get user input
                command_input = await asyncio.to_thread(
                    Prompt.ask, "[bold cyan]SelfLayer[/bold cyan]", console=self.console
                )

                if not command_input.strip():
                    continue

                # Parse and execute command
                command, args = self.parse_command(command_input)
                await self._execute_command(command, args)

            except (KeyboardInterrupt, asyncio.CancelledError):
                self.console.print("\n[yellow]Use /quit to exit gracefully.[/yellow]")
                break
            except Exception as e:
                logger.exception("Unexpected error in command loop")
                self.console.print(render_error_panel(f"Unexpected error: {e}"))

    async def _execute_command(self, command: str, args: list[str]) -> None:
        """Execute a parsed command with arguments."""
        # Check if we have an API client for most commands
        if (
            command
            not in [
                "/help",
                "/h",
                "help",
                "/key",
                "/k",
                "key",
                "/clear",
                "/c",
                "clear",
                "/quit",
                "/q",
                "quit",
                "exit",
            ]
            and not self.client
        ):
            self.console.print(
                render_error_panel(
                    "SelfLayer API key required. Use /key to set it or set SELFLAYER_API_KEY environment variable.",
                    "API Error",
                )
            )
            return

        # Route commands
        if command in ["/help", "help", "/h"]:
            await self.cmd_help()
        elif command in ["/key", "key", "/k"]:
            await self.cmd_key(args)
        elif command in ["/ask", "ask", "/a"]:
            await self.cmd_ask(args)
        elif command in ["/search", "search", "/s"]:
            await self.cmd_search(args)
        elif command in ["/documents", "documents", "/d"]:
            await self.cmd_documents(args)
        elif command in ["/notes", "notes", "/n"]:
            await self.cmd_notes(args)
        elif command in ["/integrations", "integrations", "/i"]:
            await self.cmd_integrations(args)
        elif command in ["/automations", "automations", "/auto"]:
            await self.cmd_automations(args)
        elif command in ["/notifications", "notifications", "/notifs"]:
            await self.cmd_notifications(args)
        elif command in ["/rms", "rms", "/r"]:
            await self.cmd_rms(args)
        elif command in ["/clear", "clear", "/c"]:
            await self.cmd_clear()
        elif command in ["/quit", "/exit", "quit", "exit", "/q"]:
            await self.cmd_quit()
        else:
            self.console.print(
                render_error_panel(
                    f"Unknown command: {command}. Type /help for available commands.",
                    "Invalid Command",
                )
            )

    async def cmd_help(self) -> None:
        """Show help information."""
        self.console.print(render_help())
        self.console.print()

    async def cmd_key(self, args: list[str]) -> None:
        """Set or manage the SelfLayer API key."""
        import os

        from .config import get_config_manager, get_effective_api_key

        config_manager = get_config_manager()

        if not args:
            # Show current key status
            config = config_manager.get_config()
            effective_key = get_effective_api_key()

            if effective_key:
                key_source = (
                    "environment" if os.getenv("SELFLAYER_API_KEY") else "config"
                )
                self.console.print(
                    Panel(
                        f"[green]✅ API Key Status: Configured[/green]\n\n"
                        f"[bold]Source:[/bold] {key_source}\n"
                        f"[bold]Key:[/bold] {config.get_masked_api_key() if config.api_key else 'Set via environment'}\n\n"
                        f"Use [cyan]/key clear[/cyan] to remove stored key\n"
                        f"Use [cyan]/key YOUR_API_KEY[/cyan] to update",
                        title="[bold green]🔑 API Key Status[/bold green]",
                        border_style="green",
                        padding=(1, 2),
                    )
                )
            else:
                self.console.print(
                    Panel(
                        "[red]❌ No API Key Configured[/red]\n\n"
                        "Set your SelfLayer API key using:\n"
                        "• [cyan]/key sl_live_your_api_key_here[/cyan]\n"
                        "• Or set environment variable: [cyan]SELFLAYER_API_KEY[/cyan]\n\n"
                        "[bold yellow]Get your API key:[/bold yellow]\n"
                        "Visit your SelfLayer dashboard → API Settings",
                        title="[bold red]🔑 API Key Required[/bold red]",
                        border_style="red",
                        padding=(1, 2),
                    )
                )
            return

        if args[0].lower() == "clear":
            # Clear the stored API key
            if config_manager.clear_api_key():
                self.console.print(
                    render_success_panel(
                        "API key cleared from local storage.\n\nNote: Environment variable SELFLAYER_API_KEY (if set) will still be used.",
                        "Key Cleared",
                    )
                )

                # Reset client to None since key was cleared
                if self.client:
                    await self.client.close()
                    self.client = None
                    self.app_state.clear_all_data()
                    self.app_state.api_key_set = False
                    self.app_state.user_profile = None
            else:
                self.console.print(
                    render_error_panel(
                        "Failed to clear API key from storage.", "Clear Error"
                    )
                )
            return

        # Set new API key
        api_key = " ".join(args).strip()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task("🔑 Setting API key...", total=None)

            try:
                # Save the key to config
                if config_manager.update_api_key(api_key):
                    # Initialize new client with the key
                    from .client import SelfLayerAPIClient

                    if self.client:
                        await self.client.close()

                    self.client = SelfLayerAPIClient(api_key=api_key)

                    # Test the key by fetching profile
                    try:
                        profile_data = await self.client.get_profile()
                        self.app_state.set_profile(profile_data)

                        self.console.print(
                            render_success_panel(
                                f"API key saved and verified successfully!\n\n"
                                f"Welcome, {profile_data.get('name', 'User')}! 👋\n\n"
                                f"You can now use all SelfLayer features.",
                                "Key Configured",
                            )
                        )

                        # Show profile card
                        if self.app_state.user_profile:
                            self.console.print()
                            self.console.print(
                                render_profile_card(self.app_state.user_profile)
                            )

                    except Exception as e:
                        self.console.print(
                            render_error_panel(
                                f"API key saved but verification failed: {e}\n\n"
                                f"Please check your API key is valid and has appropriate permissions.",
                                "Verification Failed",
                            )
                        )

                else:
                    self.console.print(
                        render_error_panel(
                            "Failed to save API key to local storage.", "Save Error"
                        )
                    )

            except ValueError as e:
                self.console.print(render_error_panel(str(e), "Invalid API Key"))
            except Exception as e:
                self.console.print(
                    render_error_panel(f"Unexpected error: {e}", "Setup Error")
                )

        self.console.print()

    async def cmd_ask(self, args: list[str]) -> None:
        """Ask the AI assistant a question with streaming support."""
        if not args:
            self.console.print(
                render_error_panel(
                    "Please provide a question: /ask What are my recent notes?",
                    "Missing Query",
                )
            )
            return

        question = " ".join(args)

        # Use streaming by default for better UX
        try:
            accumulated_content = ""

            with Live(
                render_streaming_response("", False),
                console=self.console,
                refresh_per_second=4,
            ) as live:
                async for chunk in await self.client.ask(question, stream=True):
                    if isinstance(chunk, dict):
                        # Handle different chunk types from streaming
                        if "data" in chunk and "response" in chunk["data"]:
                            content = chunk["data"]["response"]
                            accumulated_content += content
                            live.update(
                                render_streaming_response(accumulated_content, False)
                            )
                        elif "content" in chunk:
                            accumulated_content += chunk["content"]
                            live.update(
                                render_streaming_response(accumulated_content, False)
                            )

                # Show final result
                live.update(render_streaming_response(accumulated_content, True))

        except Exception as e:
            # Fallback to non-streaming if streaming fails
            logger.warning(f"Streaming failed, falling back to regular ask: {e}")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            ) as progress:
                progress.add_task(f"🤖 Asking: {question[:50]}...", total=None)

                try:
                    response = await self.client.ask(question, stream=False)
                    self.console.print(render_ask_response(response))
                except Exception as e:
                    self.console.print(render_error_panel(str(e), "AI Error"))

        self.console.print()

    async def cmd_search(self, args: list[str]) -> None:
        """Search the knowledge base."""
        if not args:
            self.console.print(
                render_error_panel(
                    "Please provide a search query: /search machine learning",
                    "Missing Query",
                )
            )
            return

        query = " ".join(args)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"🔍 Searching: {query}", total=None)

            try:
                search_data = await self.client.search(query)
                search_result = SearchResult(**search_data)

                # Cache results
                self.app_state.search_results = search_result
                self.app_state.current_search_query = query

                self.console.print(render_search_results(search_result, query))

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Search Error"))

        self.console.print()

    async def cmd_documents(self, args: list[str]) -> None:
        """Manage documents with subcommands."""
        if not args:
            # List all documents
            await self._list_documents()
        elif args[0] == "new" and len(args) > 1:
            # Upload new document
            await self._upload_document(args[1])
        elif args[0] == "delete" and len(args) > 1:
            # Delete document
            await self._delete_document(args[1])
        elif args[0].isdigit():
            # View document details
            await self._view_document(int(args[0]))
        else:
            self.console.print(
                render_error_panel(
                    "Usage: /d, /d new /path/to/file, /d 1, /d delete 1",
                    "Invalid Arguments",
                )
            )

    async def _list_documents(self) -> None:
        """List all documents."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task("📄 Loading documents...", total=None)

            try:
                documents_data = await self.client.list_documents()
                self.app_state.update_documents(documents_data)
                self.console.print(render_documents_list(self.app_state.documents))
            except Exception as e:
                self.console.print(render_error_panel(str(e), "Documents Error"))

        self.console.print()

    async def _upload_document(self, file_path: str) -> None:
        """Upload a document."""
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            self.console.print(
                render_error_panel(f"File not found: {file_path}", "File Error")
            )
            return

        if not file_path_obj.is_file():
            self.console.print(
                render_error_panel(f"Not a file: {file_path}", "File Error")
            )
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"📤 Uploading {file_path_obj.name}...", total=None)

            try:
                await self.client.upload_document(str(file_path_obj))
                self.console.print(
                    render_success_panel(
                        f"Document '{file_path_obj.name}' uploaded successfully and is being processed.",
                        "Upload Complete",
                    )
                )

                # Refresh documents list
                await self._list_documents()

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Upload Error"))

    async def _view_document(self, index: int) -> None:
        """View document details."""
        document = self.app_state.get_document_by_index(index)

        if not document:
            self.console.print(
                render_error_panel(
                    f"Document #{index} not found. Use /d to list documents.",
                    "Document Not Found",
                )
            )
            return

        self.console.print(render_document_card(document, index))
        self.console.print()

    async def _delete_document(self, index_str: str) -> None:
        """Delete a document."""
        try:
            index = int(index_str)
        except ValueError:
            self.console.print(
                render_error_panel(
                    f"Invalid document number: {index_str}", "Invalid Input"
                )
            )
            return

        document = self.app_state.get_document_by_index(index)

        if not document:
            self.console.print(
                render_error_panel(
                    f"Document #{index} not found. Use /d to list documents.",
                    "Document Not Found",
                )
            )
            return

        # Confirm deletion
        if not await asyncio.to_thread(
            Confirm.ask,
            f"Delete document '{document.title}'?",
            console=self.console,
            default=False,
        ):
            self.console.print("[yellow]Deletion cancelled.[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"🗑️ Deleting {document.title}...", total=None)

            try:
                await self.client.delete_document(document.id)
                self.console.print(
                    render_success_panel(
                        f"Document '{document.title}' deleted successfully.", "Deleted"
                    )
                )

                # Refresh documents list
                await self._list_documents()

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Delete Error"))

    async def cmd_notes(self, args: list[str]) -> None:
        """Manage notes with subcommands."""
        if not args:
            # List all notes
            await self._list_notes()
        elif args[0] == "new" and len(args) >= 3:
            # Create new note: /n new "Title" "Content"
            await self._create_note(args[1], " ".join(args[2:]))
        elif args[0] == "edit" and len(args) >= 3:
            # Edit note: /n edit 1 "New content"
            await self._edit_note(args[1], " ".join(args[2:]))
        elif args[0] == "delete" and len(args) > 1:
            # Delete note: /n delete 1
            await self._delete_note(args[1])
        elif args[0].isdigit():
            # View note details: /n 1
            await self._view_note(int(args[0]))
        else:
            self.console.print(
                render_error_panel(
                    'Usage: /n, /n new "Title" "Content", /n 1, /n edit 1 "Content", /n delete 1',
                    "Invalid Arguments",
                )
            )

    async def _list_notes(self) -> None:
        """List all notes."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task("📝 Loading notes...", total=None)

            try:
                notes_data = await self.client.list_notes()
                self.app_state.update_notes(notes_data)
                self.console.print(render_notes_list(self.app_state.notes))
            except Exception as e:
                self.console.print(render_error_panel(str(e), "Notes Error"))

        self.console.print()

    async def _create_note(self, title: str, content: str) -> None:
        """Create a new note."""
        # Clean quotes from title and content
        title = title.strip("\"'")
        content = content.strip("\"'")

        if not title or not content:
            self.console.print(
                render_error_panel(
                    "Both title and content are required", "Invalid Input"
                )
            )
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"📝 Creating note '{title[:30]}...'", total=None)

            try:
                await self.client.create_note(title, content)
                self.console.print(
                    render_success_panel(
                        f"Note '{title}' created successfully.", "Note Created"
                    )
                )

                # Refresh notes list
                await self._list_notes()

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Create Error"))

    async def _view_note(self, index: int) -> None:
        """View note details."""
        note = self.app_state.get_note_by_index(index)

        if not note:
            self.console.print(
                render_error_panel(
                    f"Note #{index} not found. Use /n to list notes.", "Note Not Found"
                )
            )
            return

        self.console.print(render_note_card(note, index))
        self.console.print()

    async def _edit_note(self, index_str: str, new_content: str) -> None:
        """Edit a note's content."""
        try:
            index = int(index_str)
        except ValueError:
            self.console.print(
                render_error_panel(f"Invalid note number: {index_str}", "Invalid Input")
            )
            return

        note = self.app_state.get_note_by_index(index)

        if not note:
            self.console.print(
                render_error_panel(
                    f"Note #{index} not found. Use /n to list notes.", "Note Not Found"
                )
            )
            return

        new_content = new_content.strip("\"'")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"✏️ Updating {note.title}...", total=None)

            try:
                await self.client.update_note(note.id, content=new_content)
                self.console.print(
                    render_success_panel(
                        f"Note '{note.title}' updated successfully.", "Note Updated"
                    )
                )

                # Refresh notes list
                await self._list_notes()

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Update Error"))

    async def _delete_note(self, index_str: str) -> None:
        """Delete a note."""
        try:
            index = int(index_str)
        except ValueError:
            self.console.print(
                render_error_panel(f"Invalid note number: {index_str}", "Invalid Input")
            )
            return

        note = self.app_state.get_note_by_index(index)

        if not note:
            self.console.print(
                render_error_panel(
                    f"Note #{index} not found. Use /n to list notes.", "Note Not Found"
                )
            )
            return

        # Confirm deletion
        if not await asyncio.to_thread(
            Confirm.ask,
            f"Delete note '{note.title}'?",
            console=self.console,
            default=False,
        ):
            self.console.print("[yellow]Deletion cancelled.[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"🗑️ Deleting {note.title}...", total=None)

            try:
                await self.client.delete_note(note.id)
                self.console.print(
                    render_success_panel(
                        f"Note '{note.title}' deleted successfully.", "Deleted"
                    )
                )

                # Refresh notes list
                await self._list_notes()

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Delete Error"))

    async def cmd_integrations(self, args: list[str]) -> None:
        """Manage integrations."""
        if not args:
            # List integrations
            await self._list_integrations()
        elif args[0] == "connect" and len(args) > 1:
            # Connect integration
            await self._connect_integration(args[1])
        elif args[0] == "disconnect" and len(args) > 1:
            # Disconnect integration
            await self._disconnect_integration(args[1])
        else:
            self.console.print(
                render_error_panel(
                    "Usage: /i, /i connect gmail, /i disconnect 1", "Invalid Arguments"
                )
            )

    async def _list_integrations(self) -> None:
        """List all integrations."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task("🔗 Loading integrations...", total=None)

            try:
                integrations_data = await self.client.list_integrations()
                self.app_state.update_integrations(integrations_data)
                self.console.print(
                    render_integrations_list(self.app_state.integrations)
                )
            except Exception as e:
                self.console.print(render_error_panel(str(e), "Integrations Error"))

        self.console.print()

    async def _connect_integration(self, provider: str) -> None:
        """Connect a new integration."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"🔗 Connecting {provider}...", total=None)

            try:
                result = await self.client.connect_integration(provider)

                if "redirect_url" in result:
                    self.console.print(
                        Panel(
                            f"🔗 Please visit this URL to authorize {provider}:\n\n"
                            f"[bold blue]{result['redirect_url']}[/bold blue]\n\n"
                            "After authorization, the connection will be established automatically.",
                            title="[bold green]Authorization Required[/bold green]",
                            border_style="green",
                            padding=(1, 2),
                        )
                    )
                else:
                    self.console.print(
                        render_success_panel(
                            f"{provider} connected successfully.", "Connected"
                        )
                    )

                # Refresh integrations list
                await self._list_integrations()

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Connection Error"))

    async def _disconnect_integration(self, index_str: str) -> None:
        """Disconnect an integration."""
        try:
            index = int(index_str)
        except ValueError:
            self.console.print(
                render_error_panel(
                    f"Invalid integration number: {index_str}", "Invalid Input"
                )
            )
            return

        integration = self.app_state.get_integration_by_index(index)

        if not integration:
            self.console.print(
                render_error_panel(
                    f"Integration #{index} not found. Use /i to list integrations.",
                    "Integration Not Found",
                )
            )
            return

        # Confirm disconnection
        if not await asyncio.to_thread(
            Confirm.ask,
            f"Disconnect {integration.provider} ({integration.account_identifier})?",
            console=self.console,
            default=False,
        ):
            self.console.print("[yellow]Disconnection cancelled.[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"🔌 Disconnecting {integration.provider}...", total=None)

            try:
                await self.client.disconnect_integration(integration.id)
                self.console.print(
                    render_success_panel(
                        f"{integration.provider} disconnected successfully.",
                        "Disconnected",
                    )
                )

                # Refresh integrations list
                await self._list_integrations()

            except Exception as e:
                self.console.print(render_error_panel(str(e), "Disconnect Error"))

    async def cmd_notifications(self, args: list[str]) -> None:
        """Manage notifications."""
        if not args:
            # List notifications
            await self._list_notifications()
        elif args[0] == "read" and len(args) > 1:
            # Mark notification as read
            await self._mark_notification_read(args[1])
        elif args[0] == "clear":
            # Mark all as read
            await self._mark_all_notifications_read()
        else:
            self.console.print(
                render_error_panel(
                    "Usage: /notifications, /notifications read 1, /notifications clear",
                    "Invalid Arguments",
                )
            )

    async def _list_notifications(self) -> None:
        """List all notifications."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task("📢 Loading notifications...", total=None)

            try:
                notifications_data = await self.client.list_notifications()
                self.app_state.update_notifications(notifications_data)
                self.console.print(
                    render_notifications_list(self.app_state.notifications)
                )
            except Exception as e:
                self.console.print(render_error_panel(str(e), "Notifications Error"))

        self.console.print()

    async def _mark_notification_read(self, index_str: str) -> None:
        """Mark a notification as read."""
        try:
            index = int(index_str)
        except ValueError:
            self.console.print(
                render_error_panel(
                    f"Invalid notification number: {index_str}", "Invalid Input"
                )
            )
            return

        notification = self.app_state.get_notification_by_index(index)

        if not notification:
            self.console.print(
                render_error_panel(
                    f"Notification #{index} not found.", "Notification Not Found"
                )
            )
            return

        try:
            await self.client.mark_notification_read(notification.id)
            self.console.print(
                render_success_panel("Notification marked as read.", "Updated")
            )

            # Refresh notifications list
            await self._list_notifications()

        except Exception as e:
            self.console.print(render_error_panel(str(e), "Update Error"))

    async def _mark_all_notifications_read(self) -> None:
        """Mark all notifications as read."""
        try:
            await self.client.mark_all_notifications_read()
            self.console.print(
                render_success_panel("All notifications marked as read.", "All Updated")
            )

            # Refresh notifications list
            await self._list_notifications()

        except Exception as e:
            self.console.print(render_error_panel(str(e), "Update Error"))

    async def cmd_rms(self, args: list[str]) -> None:
        """Relationship Micro-Summary - get persona briefing for someone."""
        from .models import PersonaAgentResponse
        from .renderers import render_persona_briefing

        if not args:
            self.console.print(
                render_error_panel(
                    "Usage: /rms <email|name|company>\n\n"
                    "Examples:\n"
                    "  /rms anton96vice@gmail.com\n"
                    "  /rms Anton Alice Vice\n"
                    '  /rms "SelfLayer"\n\n'
                    "Provide at least an email, name, or company to get a relationship summary.",
                    "RMS Usage",
                )
            )
            self.console.print()
            return

        query = " ".join(args)

        # Try to parse the query - check if it's an email, name, or company
        email = None
        name = None
        company = None

        if "@" in query:
            email = query
        elif query.startswith('"') and query.endswith('"'):
            # Quoted string - treat as company
            company = query.strip('"')
        else:
            # Assume it's a name
            name = query

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(
                f"🤝 Getting RMS{f' for: {query}' if query else '...'}", total=None
            )

            try:
                persona_data = await self.client.get_persona_briefing(
                    email=email, name=name, company=company
                )
                persona_response = PersonaAgentResponse(**persona_data)
                self.console.print(render_persona_briefing(persona_response, query))
            except Exception as e:
                self.console.print(render_error_panel(str(e), "RMS Error"))

        self.console.print()

    async def cmd_clear(self) -> None:
        """Clear the terminal screen."""
        clear_screen()
        self.console.print(
            render_welcome(
                has_api_key=bool(self.client), profile=self.app_state.user_profile
            )
        )
        self.console.print()

    async def cmd_quit(self) -> None:
        """Exit the application."""
        self.console.print("[yellow]👋 Thanks for using SelfLayer![/yellow]")
        if self.client:
            await self.client.close()
        self.running = False


async def main() -> None:
    """Main entry point for the CLI application."""
    cli = SelfLayerCLI()
    await cli.run()


def main_sync() -> None:
    """Synchronous wrapper for main() - used by entry points."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Thanks for using SelfLayer!")
    except Exception as e:
        print(f"Error: {e}")
        import sys

        sys.exit(1)


if __name__ == "__main__":
    main_sync()
