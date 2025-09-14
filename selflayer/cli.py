"""Command-line interface for SelfLayer."""

import argparse
import asyncio
import os
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .ai import ContentAnalyzer
from .search import search_web
from .web import WebClient

console = Console()


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    import logging

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


async def analyze_url(url: str, api_key: Optional[str] = None) -> None:
    """Analyze a single URL and display results."""
    try:
        console.print(f"🔍 Analyzing: {url}")

        # Initialize components
        scraper = WebClient()
        analyzer = ContentAnalyzer(api_key=api_key)

        # Scrape content
        with console.status("📄 Fetching content..."):
            scraped_data = await scraper.extract_content(url)

        if not scraped_data or not scraped_data.get("content"):
            console.print("❌ Failed to extract content from URL")
            return

        # Analyze with AI
        with console.status("🤖 Analyzing with AI..."):
            result = await analyzer.analyze_content(
                content=scraped_data["content"], url=url
            )

        if not result.success:
            console.print(f"❌ AI analysis failed: {result.error_message}")
            return

        # Display results
        card = result.content
        if card:
            display_web_card(card)
        else:
            console.print("❌ No analysis results available")

    except Exception as e:
        console.print(f"❌ Error analyzing URL: {e}")


def display_web_card(card) -> None:
    """Display a WebCard in a nice format."""
    # Title panel
    title_text = Text(card.title, style="bold blue")
    console.print(Panel(title_text, title="📄 Title"))

    # URL if available
    if card.url:
        console.print(f"🔗 URL: {card.url}")

    # Summary
    if card.large_summary:
        console.print(Panel(card.large_summary, title="📝 Summary"))

    # Facts
    if card.facts:
        facts_text = Text()
        for i, fact in enumerate(card.facts, 1):
            facts_text.append(f"{i}. {fact}\n")
        console.print(Panel(facts_text, title="✨ Key Facts"))

    # Links
    if card.links:
        links_text = Text()
        for link in card.links[:5]:  # Show max 5 links
            links_text.append(f"• {link}\n", style="blue underline")
        console.print(Panel(links_text, title="🔗 Related Links"))

    # Dates
    if card.dates:
        dates_text = Text(", ".join(card.dates))
        console.print(Panel(dates_text, title="📅 Important Dates"))

    # Confidence
    confidence_color = (
        "green"
        if card.analysis_confidence > 0.8
        else "yellow" if card.analysis_confidence > 0.6 else "red"
    )
    confidence_text = Text(
        f"{card.analysis_confidence:.1%}", style=f"bold {confidence_color}"
    )
    console.print(Panel(confidence_text, title="🎯 Analysis Confidence"))


async def search_and_analyze(
    query: str, max_results: int = 5, api_key: Optional[str] = None
) -> None:
    """Search and analyze top results."""
    try:
        console.print(f"🔍 Searching for: {query}")

        # Search
        with console.status("🔎 Searching..."):
            results = await search_web(query, max_results=max_results)

        if not results:
            console.print("❌ No search results found")
            return

        console.print(f"📋 Found {len(results)} results")

        # Analyze each result
        for i, result in enumerate(results, 1):
            console.print(f"\n{'='*60}")
            console.print(f"📄 Result {i}/{len(results)}")
            await analyze_url(result.url, api_key=api_key)

    except Exception as e:
        console.print(f"❌ Error in search and analysis: {e}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SelfLayer - AI-powered terminal web browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  selflayer analyze https://example.com/article
  selflayer search "machine learning trends 2024" --max-results 3
  selflayer --version
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"SelfLayer {__version__}"
    )
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )
    parser.add_argument(
        "--api-key", help="Google Gemini API key (or set GEMINI_API_KEY env var)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single URL")
    analyze_parser.add_argument("url", help="URL to analyze")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search and analyze results")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--max-results",
        type=int,
        default=3,
        help="Maximum number of results to analyze",
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)

    # Get API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print(
            "❌ No Gemini API key provided. Set GEMINI_API_KEY environment variable or use --api-key option."
        )
        sys.exit(1)

    # Handle commands
    if args.command == "analyze":
        asyncio.run(analyze_url(args.url, api_key=api_key))
    elif args.command == "search":
        asyncio.run(
            search_and_analyze(
                args.query, max_results=args.max_results, api_key=api_key
            )
        )
    else:
        # Show welcome message
        welcome_text = Text.assemble(
            ("SelfLayer ", "bold blue"),
            ("v", "dim"),
            (__version__, "bold"),
            (" - AI-powered terminal web browser\n\n", "dim"),
            ("Use ", ""),
            ("--help", "bold"),
            (" to see available commands", ""),
        )
        console.print(Panel(welcome_text, title="🌐 Welcome to SelfLayer"))
        parser.print_help()


if __name__ == "__main__":
    main()
