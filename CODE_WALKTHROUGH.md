# 🔍 SelfLayer: AI-Powered Terminal Web Browser
# Basic functionality demo

import asyncio
from selflayer.search import search_web
from selflayer.web import fetch_page_content
from selflayer.ai import get_ai_manager

async def selflayer_demo():
    """
    Demonstrates the core SelfLayer workflow:
    1. Search the web with DuckDuckGo
    2. Fetch content from top results
    3. Analyze with AI for structured insights
    """

    # Step 1: Search for content
    query = "python async programming 2024"
    print(f"Searching for: {query}")

    search_results = await search_web(query, max_results=2)
    print(f"Found {len(search_results)} results\n")

    # Step 2: Analyze each result with AI
    ai_manager = get_ai_manager()  # Requires GEMINI_API_KEY

    for i, result in enumerate(search_results, 1):
        print(f"[{i}] {result.title[:50]}...")
        print(f"    URL: {result.url}")

        try:
            # Fetch webpage content
            content_data = await fetch_page_content(str(result.url))
            print(f"    Fetched: {len(content_data['content']):,} characters")

            # AI analysis with structured output
            ai_response = await ai_manager.analyze_web_content(
                content_data['content'],
                str(result.url)
            )

            if ai_response.success and ai_response.content:
                card = ai_response.content
                print(f"    AI Analysis: {card.analysis_confidence:.1%} confidence")
                print(f"    Key Facts: {len(card.facts)} extracted")

                # Show top 2 facts
                for j, fact in enumerate(card.facts[:2], 1):
                    print(f"      {j}. {fact}")
            else:
                print(f"    AI Analysis: Failed")

        except Exception as e:
            print(f"    Error: {e}")

        print()  # Empty line between results

# --- Main execution ---
if __name__ == "__main__":
    print("SelfLayer Demo: Search + AI Analysis\n")
    asyncio.run(selflayer_demo())

# Expected Output:
# The key takeaway is that SelfLayer combines web search, content fetching,
# and AI analysis into a single workflow. Each result will be analyzed with
# structured extraction of facts and confidence scoring.

# Your output will look something like this:

SelfLayer Demo: Search + AI Analysis

Searching for: python async programming 2024
Found 2 results

[1] Python Asyncio: The Complete Guide - Real Python...
    URL: https://realpython.com/async-io-python/
    Fetched: 47,230 characters
    AI Analysis: 96.3% confidence
    Key Facts: 5 extracted
      1. Python asyncio is a library for concurrent programming using async/await syntax
      2. AsyncIO provides event loop management for handling multiple I/O operations

[2] FastAPI Async Programming Tutorial - Modern Python...
    URL: https://fastapi.tiangolo.com/async/
    Fetched: 23,187 characters
    AI Analysis: 94.7% confidence
    Key Facts: 4 extracted
      1. FastAPI provides native support for async/await patterns
      2. Async endpoints can handle thousands of concurrent requests

# CLI Usage - Interactive TUI (Terminal User Interface):
# pip install selflayer
# selflayer                          # Launch interactive TUI
# /key YOUR_GEMINI_API_KEY           # Set API key
# /find "python async programming" 3  # Search & analyze
# /search "web scraping"              # Search only
# /open 1                            # Analyze result #1
# /url https://example.com           # Direct URL analysis
# /help                              # Show help
# /quit                              # Exit

# CLI Usage - Direct command line:
# sl search "machine learning" --max-results 3
# sl analyze https://docs.python.org/3/tutorial/

# 🖼️ TUI Screenshot:
# [Space reserved for TUI interface screenshot showing the colorful terminal interface]

# 🚀 SelfLayer: AI-powered terminal web browser
# 🔗 GitHub: github.com/antonvice/selflayer
# 📦 PyPI: pypi.org/project/selflayer
