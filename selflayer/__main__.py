"""
Main entry point for SelfLayer package.

This module allows SelfLayer to be run as a Python module using:
    python -m selflayer

It sets up logging and launches the main CLI application.
"""

from __future__ import annotations

import logging
import sys


# Configure logging for the application
def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration for SelfLayer.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            # Log to file for debugging
            logging.FileHandler("selflayer.log"),
            # Also log to stderr for development
            logging.StreamHandler(sys.stderr),
        ],
    )

    # Suppress some noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main() -> None:
    """Main entry point for SelfLayer application."""
    # Setup logging
    setup_logging()

    # Import and run the CLI
    try:
        import asyncio

        from .tui import main as cli_main

        asyncio.run(cli_main())
    except KeyboardInterrupt:
        print("\n👋 Thanks for using SelfLayer!")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
