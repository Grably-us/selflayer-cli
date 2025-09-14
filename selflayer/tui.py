"""
Main CLI interface for SelfLayer using Rich for formatting.

This module implements a pure terminal interface for web search, content analysis,
and display of results using Rich formatting for an elegant terminal experience.
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

from . import APIError, SearchError, WebError
from .ai import get_ai_manager
from .config import load_api_key, save_api_key
from .models import AppState, SearchResult, WebCard
from .search import search_web
from .web import fetch_page_content

# Configure module logger
logger = logging.getLogger(__name__)

# API Key text file path
API_KEY_FILE = Path.home() / ".selflayer" / "api_key.txt"


def save_api_key_txt(api_key: str) -> bool:
    """Save API key to text file."""
    try:
        API_KEY_FILE.parent.mkdir(mode=0o700, exist_ok=True)
        with open(API_KEY_FILE, "w") as f:
            f.write(api_key.strip())
        API_KEY_FILE.chmod(0o600)
        return True
    except Exception as e:
        logger.error(f"Failed to save API key to text file: {e}")
        return False


def load_api_key_txt() -> str | None:
    """Load API key from text file."""
    try:
        if API_KEY_FILE.exists():
            with open(API_KEY_FILE, "r") as f:
                return f.read().strip()
        return None
    except Exception as e:
        logger.error(f"Failed to load API key from text file: {e}")
        return None


def clear_api_key_txt() -> bool:
    """Clear API key text file."""
    try:
        if API_KEY_FILE.exists():
            API_KEY_FILE.unlink()
        return True
    except Exception as e:
        logger.error(f"Failed to clear API key text file: {e}")
        return False


# ASCII Art for SelfLayer
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


def render_welcome(has_api_key: bool = False) -> Panel:
    """Render the welcome message with ASCII art and instructions."""
    # Adjust instructions based on whether API key is available
    if has_api_key:
        getting_started = """[bold cyan]You're ready to go![/bold cyan]
1. Search & analyze: [bold]/find python tutorial[/bold] (or [bold]/f[/bold])
2. Search only: [bold]/search query[/bold] (or [bold]/s[/bold])
3. Analyze URL: [bold]/url https://example.com[/bold] (or [bold]/u[/bold])"""
        api_status = "[bold green]✓ API Key Loaded[/bold green] (from previous session)"
    else:
        getting_started = """[bold cyan]Getting Started:[/bold cyan]
1. Set your Gemini API key: [bold]/key YOUR_API_KEY[/bold] (or [bold]/k[/bold])
2. Search & analyze: [bold]/find python tutorial[/bold] (or [bold]/f[/bold])
3. Search only: [bold]/search query[/bold] (or [bold]/s[/bold])"""
        api_status = "[bold red]✗ API Key Required[/bold red]"

    welcome_content = f"""[bold magenta]{SELFLAYER_ART}[/bold magenta]

[bold]Welcome to SelfLayer![/bold]

An AI-powered terminal web browser for intelligent content analysis and research.

{api_status}

{getting_started}

[bold cyan]Available Commands:[/bold cyan]
• [bold]/key <api_key>[/bold] - Set your Google Gemini API key
• [bold]/search <query>[/bold] - Search the web using DuckDuckGo
• [bold]/open <number>[/bold] - Analyze a search result by number
• [bold]/url <url>[/bold] - Directly analyze a URL
• [bold]/clear[/bold] - Clear the screen
• [bold]/help[/bold] - Show detailed help
• [bold]/quit[/bold] or [bold]/exit[/bold] - Exit the application

[bold yellow]Need an API key?[/bold yellow]
Get your free Gemini API key at: https://makersuite.google.com/app/apikey"""

    return Panel(
        welcome_content,
        title="[bold green]SelfLayer - AI-Powered Terminal Web Browser[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def render_search_results(results: list[SearchResult]) -> Panel:
    """Render search results as a table."""
    if not results:
        return Panel(
            "[yellow]No search results to display[/yellow]",
            title="Search Results",
            border_style="yellow",
        )

    table = Table(
        title=f"Search Results ({len(results)} found)",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
    )
    table.add_column("#", style="cyan", width=3)
    table.add_column("Title", style="bold white", ratio=2)
    table.add_column("URL", style="blue", ratio=2)
    table.add_column("Snippet", style="dim", ratio=3)

    for i, result in enumerate(results, 1):
        table.add_row(
            str(i),
            result.title[:60] + "..." if len(result.title) > 60 else result.title,
            (
                str(result.url)[:50] + "..."
                if len(str(result.url)) > 50
                else str(result.url)
            ),
            (
                result.snippet[:100] + "..."
                if len(result.snippet) > 100
                else result.snippet
            ),
        )

    return Panel(table, border_style="cyan")


def render_webcard(web_card: WebCard) -> Panel:
    """Render a WebCard with rich formatting."""

    # Facts section (if available)
    facts_text = ""
    if web_card.facts:
        facts_text = "\n".join(f"• {fact}" for fact in web_card.facts)

    # Info section with metadata
    info_table = Table.grid(padding=1)
    info_table.add_column(style="bold")
    info_table.add_column()

    info_table.add_row("URL:", str(web_card.url))
    info_table.add_row("Analyzed:", web_card.fetched_at.strftime("%Y-%m-%d %H:%M UTC"))
    info_table.add_row("Confidence:", f"{web_card.analysis_confidence:.1%}")
    info_table.add_row("Content Length:", f"{web_card.content_length:,} chars")

    if web_card.dates:
        info_table.add_row("Dates:", ", ".join(web_card.dates[:3]))

    if web_card.links:
        info_table.add_row("Links Found:", f"{len(web_card.links)} links")

    # Combine sections
    content_parts = [f"[bold magenta]{web_card.title}[/bold magenta]\n"]

    content_parts.append("[bold cyan]Summary[/bold cyan]")
    content_parts.append(web_card.large_summary)
    content_parts.append("")

    if facts_text:
        content_parts.append("[bold green]Key Facts[/bold green]")
        content_parts.append(facts_text)
        content_parts.append("")

    content_parts.append("[bold yellow]Information[/bold yellow]")

    # Format info as text instead of table for simplicity
    info_lines = [
        f"[bold]URL:[/bold] {web_card.url}",
        f"[bold]Analyzed:[/bold] {web_card.fetched_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"[bold]Confidence:[/bold] {web_card.analysis_confidence:.1%}",
        f"[bold]Content Length:[/bold] {web_card.content_length:,} chars",
    ]

    if web_card.dates:
        info_lines.append(f"[bold]Dates:[/bold] {', '.join(web_card.dates[:3])}")

    if web_card.links:
        info_lines.append(f"[bold]Links Found:[/bold] {len(web_card.links)} links")

    content_parts.extend(info_lines)

    return Panel(
        "\n".join(content_parts),
        title="[bold]WebCard Analysis[/bold]",
        border_style="bright_magenta",
        padding=(1, 2),
    )


def render_help() -> Panel:
    """Render the help information."""
    help_content = """[bold magenta]SelfLayer Commands Reference[/bold magenta]

[bold cyan]Setup Commands:[/bold cyan]
• [bold]/key <api_key>[/bold] (or [bold]/k[/bold])
  Set your Google Gemini API key for AI analysis (saved as text file)
  Example: /key AIzaSy...

• [bold]/key clear[/bold] (or [bold]/k clear[/bold])
  Clear the stored API key from local storage

[bold cyan]Search & Analysis Commands:[/bold cyan]
• [bold]/find <query> [depth][/bold] (or [bold]/f[/bold])
  Search the web and automatically analyze multiple results (default: 5)
  Example: /find python tutorials 3

• [bold]/search <query>[/bold] (or [bold]/s[/bold])
  Search the web using DuckDuckGo (no analysis)
  Example: /search python machine learning tutorials

• [bold]/open <number>[/bold] (or [bold]/o[/bold])
  Analyze a search result by its number (1, 2, 3, etc.)
  Example: /open 1

• [bold]/url <url>[/bold] (or [bold]/u[/bold])
  Directly analyze content from a specific URL
  Example: /url https://docs.python.org

[bold cyan]Utility Commands:[/bold cyan]
• [bold]/clear[/bold] (or [bold]/c[/bold]) - Clear the screen
• [bold]/status[/bold] - Show current configuration status
• [bold]/help[/bold] (or [bold]/h[/bold]) - Show this help message
• [bold]/quit[/bold] or [bold]/exit[/bold] (or [bold]/q[/bold]) - Exit SelfLayer

[bold yellow]Tips:[/bold yellow]
• Get your Gemini API key from: https://makersuite.google.com/app/apikey
• Use /find for comprehensive analysis of multiple results at once
• Use /search + /open for step-by-step analysis
• API key is saved as plain text in ~/.selflayer/api_key.txt
• All operations are performed asynchronously for smooth experience"""

    return Panel(
        help_content,
        title="[bold green]Help & Documentation[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


class CLI:
    """Command-line interface for SelfLayer."""

    def __init__(self) -> None:
        """Initialize the CLI with state and console."""
        self.console = Console()
        self.app_state = AppState()
        self.ai_manager = get_ai_manager()
        self.running = True

        # Try to load stored API key and initialize AI if available
        self._load_stored_config()

    def _load_stored_config(self) -> None:
        """Load stored configuration and initialize AI if API key is available."""
        try:
            # Try to load from text file first, then fall back to JSON config
            api_key = load_api_key_txt() or load_api_key()
            if api_key:
                # Initialize AI manager with stored key
                self.ai_manager = get_ai_manager()
                self.ai_manager.api_key = api_key
                # Initialize the AI manager so it's ready for use
                initialization_success = self.ai_manager.initialize()
                if initialization_success:
                    self.app_state.api_key_set = True
                    logger.info(
                        "Loaded stored API key and initialized AI manager successfully"
                    )
                else:
                    logger.warning(
                        "API key loaded but AI manager initialization failed"
                    )
        except Exception as e:
            logger.warning(f"Failed to load stored config: {e}")

    def parse_command(self, raw: str) -> tuple[str, list[str]]:
        """Parse a raw command input into command and arguments.

        Args:
            raw: Raw command string from user input

        Returns:
            Tuple of (command, args_list)
        """
        parts = raw.strip().split()
        if not parts:
            return "", []

        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        return command, args

    async def run(self) -> None:
        """Run the main command loop."""
        clear_screen()
        self.console.print(render_welcome(self.app_state.api_key_set))
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
                self.console.print(
                    "\n[yellow]Use /quit or /exit to exit gracefully.[/yellow]"
                )
                break
            except Exception as e:
                logger.exception("Unexpected error in command loop")
                self.console.print(f"[red]Unexpected error: {e}[/red]")

    async def _execute_command(self, command: str, args: list[str]) -> None:
        """Execute a parsed command with arguments.

        Args:
            command: The command to execute
            args: List of command arguments
        """
        if command in ["/help", "help", "?", "/?", "/h"]:
            await self.cmd_help()
        elif command in ["/key", "key", "/k"]:
            await self.cmd_key(args)
        elif command in ["/search", "search", "/s"]:
            await self.cmd_search(args)
        elif command in ["/find", "find", "/f"]:
            await self.cmd_find(args)
        elif command in ["/open", "open", "/o"]:
            await self.cmd_open(args)
        elif command in ["/url", "url", "/u"]:
            await self.cmd_url(args)
        elif command in ["/clear", "clear", "cls", "/c"]:
            await self.cmd_clear()
        elif command in ["/status", "status"]:
            await self.cmd_status()
        elif command in ["/quit", "/exit", "quit", "exit", "/q"]:
            await self.cmd_quit()
        else:
            self.console.print(
                f"[red]Unknown command: {command}. Type /help for available commands.[/red]"
            )

    async def cmd_help(self) -> None:
        """Show help information."""
        self.console.print(render_help())
        self.console.print()

    async def cmd_key(self, args: list[str]) -> None:
        """Set or clear the Gemini API key.

        Args:
            args: Command arguments, expecting [api_key] or ["clear"]
        """
        if not args:
            self.console.print(
                "[red]Please provide an API key or 'clear': /key YOUR_API_KEY[/red]"
            )
            self.console.print("[dim]Use '/key clear' to remove stored API key[/dim]")
            return

        # Handle clear command
        if len(args) == 1 and args[0].lower() == "clear":
            await self._clear_api_key()
            return

        api_key = " ".join(args)  # Join in case key was split

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task("Setting up API key...", total=None)

            try:
                # Initialize AI manager with the new API key
                self.ai_manager = get_ai_manager()
                self.ai_manager.api_key = api_key

                success = await self.ai_manager.initialize()

                if success:
                    self.app_state.api_key_set = True

                    # Save API key to both text file and JSON config
                    txt_saved = save_api_key_txt(api_key)
                    json_saved = save_api_key(api_key)

                    if txt_saved:
                        self.console.print(
                            "[green]✓ API key configured and saved successfully![/green]"
                        )
                        self.console.print(
                            "Your API key has been stored locally and will be used in future sessions."
                        )
                    elif json_saved:
                        self.console.print(
                            "[green]✓ API key configured and saved to config![/green]"
                        )
                        self.console.print(
                            "Your API key has been stored in config and will be used in future sessions."
                        )
                    else:
                        self.console.print(
                            "[yellow]⚠ API key configured but could not be saved to storage.[/yellow]"
                        )

                    self.console.print(
                        "AI services are now ready. You can start searching with: [cyan]/search your query here[/cyan]"
                    )
                else:
                    self.console.print(
                        "[red]Failed to initialize AI services. Please check your API key.[/red]"
                    )

            except APIError as e:
                self.console.print(f"[red]API Error: {e}[/red]")
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {e}[/red]")

        self.console.print()

    async def _clear_api_key(self) -> None:
        """Clear the stored API key."""
        from .config import get_config_manager

        try:
            config_manager = get_config_manager()

            # Clear both text file and JSON config
            txt_cleared = clear_api_key_txt()
            json_cleared = config_manager.clear_api_key()

            if txt_cleared or json_cleared:
                self.app_state.api_key_set = False
                self.ai_manager = get_ai_manager()  # Reset AI manager
                self.console.print("[green]✓ API key cleared successfully![/green]")
                self.console.print(
                    "You will need to set a new API key to use AI features."
                )
            else:
                self.console.print("[red]Failed to clear API key from storage.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error clearing API key: {e}[/red]")

        self.console.print()

    async def cmd_search(self, args: list[str]) -> None:
        """Search the web using DuckDuckGo.

        Args:
            args: Command arguments, expecting search query terms
        """
        if not args:
            self.console.print(
                "[red]Please provide a search query: /search your query[/red]"
            )
            return

        query = " ".join(args)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"Searching for: {query}", total=None)

            try:
                # Perform search
                results = await search_web(query, max_results=10)

                if results:
                    # Store results in app state
                    self.app_state.add_search_results(results)
                    self.app_state.current_search_query = query

                    # Display results
                    self.console.print(render_search_results(results))

                    # Instructions for next step
                    self.console.print(
                        Panel(
                            f"[green]Found {len(results)} results![/green]\n\n"
                            "To analyze a result, use: [cyan]/open <number>[/cyan]\n"
                            "For example: [bold]/open 1[/bold] to analyze the first result",
                            title="[blue]Next Steps[/blue]",
                            border_style="blue",
                        )
                    )

                else:
                    self.console.print(
                        Panel(
                            f"[yellow]No results found for query: {query}[/yellow]\n\n"
                            "Try a different search query or check your internet connection.",
                            title="[yellow]No Results[/yellow]",
                            border_style="yellow",
                        )
                    )

            except SearchError as e:
                self.console.print(f"[red]Search error: {e}[/red]")
            except Exception as e:
                self.console.print(f"[red]Unexpected error during search: {e}[/red]")

        self.console.print()

    async def cmd_open(self, args: list[str]) -> None:
        """Open and analyze a search result by number.

        Args:
            args: Command arguments, expecting [result_number]
        """
        if not self.app_state.search_results:
            self.console.print(
                "[red]No search results available. Use /search first.[/red]"
            )
            return

        if not args:
            self.console.print("[red]Please provide a result number: /open 1[/red]")
            return

        try:
            number = int(args[0])
            if number < 1 or number > len(self.app_state.search_results):
                self.console.print(
                    f"[red]Invalid result number. Use 1-{len(self.app_state.search_results)}[/red]"
                )
                return
        except ValueError:
            self.console.print("[red]Please provide a valid number: /open 1[/red]")
            return

        if not self.ai_manager.is_ready:
            self.console.print(
                "[red]AI services not ready. Please set your API key first with /key[/red]"
            )
            return

        # Get the selected result
        result = self.app_state.search_results[number - 1]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"Fetching content from {result.url}", total=None)

            try:
                # Fetch web content
                content_data = await fetch_page_content(str(result.url))

                # Analyzing content with AI...

                # Analyze content with AI
                ai_response = await self.ai_manager.analyze_web_content(
                    content_data["content"], str(result.url)
                )

                if ai_response.success and ai_response.content:
                    # Store in app state
                    self.app_state.add_web_card(ai_response.content)

                    # Display WebCard
                    self.console.print(render_webcard(ai_response.content))
                    self.console.print(
                        f"[green]Analysis complete! Confidence: {ai_response.content.analysis_confidence:.1%}[/green]"
                    )
                else:
                    self.console.print(
                        Panel(
                            f"[red]Analysis failed: {ai_response.error_message}[/red]",
                            title="[red]Error[/red]",
                            border_style="red",
                        )
                    )

            except WebError as e:
                self.console.print(f"[red]Web error: {e}[/red]")
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {e}[/red]")

        self.console.print()

    async def cmd_url(self, args: list[str]) -> None:
        """Directly analyze content from a URL.

        Args:
            args: Command arguments, expecting [url]
        """
        if not args:
            self.console.print(
                "[red]Please provide a URL: /url https://example.com[/red]"
            )
            return

        if not self.ai_manager.is_ready:
            self.console.print(
                "[red]AI services not ready. Please set your API key first with /key[/red]"
            )
            return

        url = args[0]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(f"Fetching content from {url}", total=None)

            try:
                # Fetch web content
                content_data = await fetch_page_content(url)

                # Analyzing content with AI...

                # Analyze content with AI
                ai_response = await self.ai_manager.analyze_web_content(
                    content_data["content"], url
                )

                if ai_response.success and ai_response.content:
                    # Store in app state
                    self.app_state.add_web_card(ai_response.content)

                    # Display WebCard
                    self.console.print(render_webcard(ai_response.content))
                    self.console.print(
                        f"[green]Analysis complete! Confidence: {ai_response.content.analysis_confidence:.1%}[/green]"
                    )
                else:
                    self.console.print(
                        Panel(
                            f"[red]Analysis failed: {ai_response.error_message}[/red]",
                            title="[red]Error[/red]",
                            border_style="red",
                        )
                    )

            except WebError as e:
                self.console.print(f"[red]Web error: {e}[/red]")
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {e}[/red]")

        self.console.print()

    async def cmd_find(self, args: list[str]) -> None:
        """Search the web and analyze multiple results automatically.

        Args:
            args: Command arguments, expecting search query and optional depth
        """
        if not args:
            self.console.print(
                "[red]Please provide a search query: /find your query[/red]"
            )
            self.console.print(
                "[dim]Optional: /find your query 3 (to limit to 3 results)[/dim]"
            )
            return

        if not self.ai_manager.is_ready:
            self.console.print(
                "[red]AI services not ready. Please set your API key first with /key[/red]"
            )
            return

        # Parse arguments: query and optional depth
        depth = 5  # Default depth
        query_parts = args.copy()

        # Check if last argument is a number (depth)
        if args and args[-1].isdigit():
            depth = int(args[-1])
            depth = max(1, min(depth, 10))  # Limit between 1 and 10
            query_parts = args[:-1]

        if not query_parts:
            self.console.print(
                "[red]Please provide a search query: /find your query[/red]"
            )
            return

        query = " ".join(query_parts)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            # Step 1: Search
            progress.add_task(f"Searching for: {query}", total=None)

            try:
                # Perform search
                results = await search_web(query, max_results=depth)

                if not results:
                    self.console.print(
                        Panel(
                            f"[yellow]No results found for query: {query}[/yellow]\n\n"
                            "Try a different search query or check your internet connection.",
                            title="[yellow]No Results[/yellow]",
                            border_style="yellow",
                        )
                    )
                    return

                # Store results in app state
                self.app_state.add_search_results(results)
                self.app_state.current_search_query = query

                # Display search results
                self.console.print(render_search_results(results))
                self.console.print()

                # Step 2: Analyze each result
                successful_analyses = []
                failed_analyses = []

                for i, result in enumerate(results, 1):
                    # Analyzing result {i}/{len(results)}: {result.title[:50]}...

                    try:
                        # Fetch web content
                        content_data = await fetch_page_content(str(result.url))

                        # Analyze content with AI
                        ai_response = await self.ai_manager.analyze_web_content(
                            content_data["content"], str(result.url)
                        )

                        if ai_response.success and ai_response.content:
                            # Store in app state
                            self.app_state.add_web_card(ai_response.content)
                            successful_analyses.append((i, result, ai_response.content))
                        else:
                            failed_analyses.append(
                                (
                                    i,
                                    result,
                                    ai_response.error_message or "Unknown error",
                                )
                            )

                    except Exception as e:
                        failed_analyses.append((i, result, str(e)))

                # Display results
                # Complete! Displaying results...
                await asyncio.sleep(0.5)  # Brief pause for user to see completion

                # Show successful analyses
                if successful_analyses:
                    self.console.print(
                        Panel(
                            f"[green]Successfully analyzed {len(successful_analyses)} out of {len(results)} results![/green]",
                            title="[green]Analysis Complete[/green]",
                            border_style="green",
                        )
                    )

                    for i, result, web_card in successful_analyses:
                        self.console.print(
                            f"\n[bold cyan]Result #{i}: {result.title}[/bold cyan]"
                        )
                        self.console.print(render_webcard(web_card))

                # Show failed analyses
                if failed_analyses:
                    self.console.print(
                        Panel(
                            "\n".join(
                                [
                                    f"[red]#{i}: {result.title[:50]}... - {error[:100]}...[/red]"
                                    for i, result, error in failed_analyses
                                ]
                            ),
                            title="[red]Failed Analyses[/red]",
                            border_style="red",
                        )
                    )

                # Summary
                self.console.print(
                    Panel(
                        f"[bold]Query:[/bold] {query}\n"
                        f"[bold]Depth:[/bold] {depth} results\n"
                        f"[bold]Successful:[/bold] {len(successful_analyses)}\n"
                        f"[bold]Failed:[/bold] {len(failed_analyses)}",
                        title="[blue]Find Summary[/blue]",
                        border_style="blue",
                    )
                )

            except SearchError as e:
                self.console.print(f"[red]Search error: {e}[/red]")
            except Exception as e:
                self.console.print(f"[red]Unexpected error during find: {e}[/red]")

        self.console.print()

    async def cmd_clear(self) -> None:
        """Clear the terminal screen."""
        clear_screen()
        self.console.print(render_welcome(self.app_state.api_key_set))
        self.console.print()

    async def cmd_status(self) -> None:
        """Show current configuration status."""
        from .config import get_config_manager

        try:
            config_manager = get_config_manager()
            config = config_manager.get_config()

            status_info = []
            status_info.append("[bold blue]SelfLayer Configuration Status[/bold blue]")
            status_info.append("")

            # API Key status
            if config.has_api_key():
                api_key_masked = (
                    config.gemini_api_key[:8] + "..." + config.gemini_api_key[-4:]
                    if config.gemini_api_key
                    else "None"
                )
                status_info.append(
                    f"[bold]API Key:[/bold] [green]✓ Configured[/green] ({api_key_masked})"
                )
                status_info.append(
                    f"[bold]AI Services:[/bold] {'[green]✓ Ready[/green]' if self.ai_manager.is_ready else '[yellow]⚠ Not Initialized[/yellow]'}"
                )
            else:
                status_info.append("[bold]API Key:[/bold] [red]✗ Not Set[/red]")
                status_info.append(
                    "[bold]AI Services:[/bold] [red]✗ Not Available[/red]"
                )

            status_info.append("")
            status_info.append(
                f"[bold]Config File:[/bold] {config_manager.get_config_file_path()}"
            )
            status_info.append(
                f"[bold]Session Duration:[/bold] {self.app_state.get_session_duration()}"
            )
            status_info.append(
                f"[bold]Search Results:[/bold] {len(self.app_state.search_results)} cached"
            )
            status_info.append(
                f"[bold]Web Cards:[/bold] {len(self.app_state.active_cards)} cached"
            )

            status_panel = Panel(
                "\n".join(status_info),
                title="[bold blue]Status[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            )

            self.console.print(status_panel)

        except Exception as e:
            self.console.print(f"[red]Error retrieving status: {e}[/red]")

        self.console.print()

    async def cmd_quit(self) -> None:
        """Exit the application."""
        self.console.print("[yellow]👋 Thanks for using SelfLayer![/yellow]")
        self.running = False


async def main() -> None:
    """Main entry point for the CLI application."""
    cli = CLI()
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
