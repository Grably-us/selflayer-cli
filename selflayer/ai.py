"""AI integration for SelfLayer using Pydantic AI and Google Gemini.

This module provides structured AI analysis capabilities with streaming support,
using Pydantic AI for reliable structured outputs and error handling. Designed
to analyze web content and return structured WebCard objects.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, AsyncIterator

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from . import APIError
from .models import AIResponse, WebCard

# Configure module logger
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MODEL = "gemini-2.5-flash-lite"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_TOKENS = 10000
DEFAULT_TEMPERATURE = 0.1  # Low temperature for consistent structured output


class ContentAnalysisContext(BaseModel):
    """Context for content analysis operations."""

    url: str
    content_length: int
    analysis_type: str = "web_content"
    user_preferences: dict[str, Any] = {}


class ContentAnalyzer:
    """
    AI content analyzer using Pydantic AI and Google Gemini.

    This class provides structured content analysis with streaming support,
    converting raw web content into WebCard objects with proper validation
    and error handling.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> None:
        """
        Initialize the content analyzer.

        Args:
            api_key: Google Gemini API key (uses GEMINI_API_KEY env var if None)
            model_name: Gemini model to use
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)

        Raises:
            APIError: If API key is not provided or invalid
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise APIError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model_name = model_name
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize Gemini model
        # Set the API key in environment for pydantic-ai to use
        os.environ["GEMINI_API_KEY"] = self.api_key

        try:
            self.model = GeminiModel(model_name)
            logger.info(f"Initialized Gemini model: {model_name}")
        except Exception as e:
            raise APIError(f"Failed to initialize Gemini model: {e}")

        # Create Pydantic AI agent for content analysis
        self.agent = Agent(
            model=self.model,
            output_type=WebCard,
            system_prompt=self._get_system_prompt(),
        )

        logger.info("Content analyzer initialized successfully")

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for content analysis.

        Returns:
            System prompt string optimized for web content analysis
        """
        return """You are an expert content analyzer for SelfLayer, an AI-powered terminal web browser.

Your job is to analyze web content and extract structured information into a WebCard format.

INSTRUCTIONS:
1. Analyze the provided web content thoroughly
2. Extract the most important information
3. Create a comprehensive summary (large_summary) that captures the main points
4. Identify key facts as bullet points (facts list)
5. Extract relevant links found in the content (links list)
6. Find any important dates mentioned (dates list)
7. Assess your confidence in the analysis (analysis_confidence: 0.0-1.0)

GUIDELINES:
- Focus on factual, objective information
- Make the summary clear and informative (aim for 200-500 words)
- Keep facts concise and specific
- Only include working HTTPS/HTTP links
- Format dates consistently (YYYY-MM-DD when possible)
- Set confidence based on content quality and completeness
- If content seems truncated or unclear, lower confidence accordingly

QUALITY STANDARDS:
- Ensure summary is substantive and valuable
- Facts should be distinct and informative
- Links should be relevant and functional
- Be honest about limitations in your analysis
- Prioritize accuracy over completeness

Remember: You are helping users quickly understand web content through structured, reliable analysis."""

    async def analyze_content(
        self, content: str, url: str, additional_context: dict[str, Any] | None = None
    ) -> AIResponse:
        """
        Analyze web content and return structured results.

        Args:
            content: The raw web content to analyze
            url: Source URL of the content
            additional_context: Optional additional context for analysis

        Returns:
            AIResponse with WebCard content or error information
        """
        if not content or not content.strip():
            return AIResponse(
                success=False,
                error_message="Content cannot be empty",
                model_used=self.model_name,
            )

        start_time = time.time()

        try:
            # Prepare context
            context = ContentAnalysisContext(
                url=url,
                content_length=len(content),
                user_preferences=additional_context or {},
            )

            # Truncate content if too long (keep within token limits)
            max_content_length = 15000  # Approximate token limit
            if len(content) > max_content_length:
                content = content[:max_content_length] + "\n\n[Content truncated...]"
                logger.info(
                    f"Content truncated from {context.content_length} to {len(content)} chars"
                )

            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(content, url)

            logger.info(f"Analyzing content from {url} ({len(content)} chars)")

            # Run analysis with timeout
            result = await asyncio.wait_for(
                self.agent.run(analysis_prompt), timeout=self.timeout
            )

            # Extract WebCard from structured result
            # In Pydantic AI, the structured output is available via result.output
            web_card = result.output

            # Update WebCard with additional metadata
            web_card.url = url
            web_card.content_length = context.content_length

            # Calculate processing metrics
            processing_time = time.time() - start_time

            logger.info(
                f"Successfully analyzed content from {url} in {processing_time:.2f}s "
                f"(confidence: {web_card.analysis_confidence:.2%})"
            )

            return AIResponse(
                success=True,
                content=web_card,
                model_used=self.model_name,
                processing_time=processing_time,
                tokens_used=self._estimate_tokens_used(content, web_card),
            )

        except asyncio.TimeoutError:
            error_msg = f"Analysis timed out after {self.timeout}s for {url}"
            logger.error(error_msg)
            return AIResponse(
                success=False,
                error_message=error_msg,
                model_used=self.model_name,
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            error_msg = f"Analysis failed for {url}: {e}"
            logger.error(error_msg)
            return AIResponse(
                success=False,
                error_message=error_msg,
                model_used=self.model_name,
                processing_time=time.time() - start_time,
            )

    async def stream_analysis(
        self, content: str, url: str, additional_context: dict[str, Any] | None = None
    ) -> AsyncIterator[WebCard | dict[str, Any]]:
        """
        Stream content analysis results as they become available.

        Args:
            content: The raw web content to analyze
            url: Source URL of the content
            additional_context: Optional additional context

        Yields:
            Partial WebCard objects or progress updates

        Note:
            This is a placeholder for streaming implementation.
            Gemini streaming with structured outputs requires special handling.
        """
        # Note: Real streaming with structured outputs in Pydantic AI
        # requires careful implementation. For now, we'll simulate streaming
        # by yielding progress updates, then the final result.

        logger.info(f"Starting streaming analysis for {url}")

        # Yield progress updates
        yield {
            "status": "starting",
            "progress": 0.0,
            "message": "Initializing analysis...",
        }
        await asyncio.sleep(0.1)

        yield {
            "status": "analyzing",
            "progress": 0.25,
            "message": "Analyzing content structure...",
        }
        await asyncio.sleep(0.2)

        yield {
            "status": "extracting",
            "progress": 0.50,
            "message": "Extracting key information...",
        }
        await asyncio.sleep(0.2)

        yield {
            "status": "structuring",
            "progress": 0.75,
            "message": "Structuring results...",
        }
        await asyncio.sleep(0.2)

        # Perform the actual analysis
        result = await self.analyze_content(content, url, additional_context)

        if result.success and result.content:
            yield {
                "status": "complete",
                "progress": 1.0,
                "message": "Analysis complete!",
            }
            yield result.content
        else:
            yield {
                "status": "error",
                "progress": 0.0,
                "message": result.error_message or "Analysis failed",
            }

    def _create_analysis_prompt(self, content: str, url: str) -> str:
        """
        Create a detailed analysis prompt for the content.

        Args:
            content: Web content to analyze
            url: Source URL

        Returns:
            Formatted prompt string
        """
        return f"""Please analyze the following web content and provide structured information:

SOURCE URL: {url}

CONTENT TO ANALYZE:
---
{content}
---

Please provide a comprehensive analysis following the WebCard structure:
- Create a clear, informative title
- Write a detailed summary (200-500 words) covering the main points
- Extract key facts as bullet points
- List any relevant dates found
- Include important links mentioned in the content
- Assess your confidence in this analysis (0.0 to 1.0)

Focus on accuracy, clarity, and usefulness for someone trying to quickly understand this content."""

    def _estimate_tokens_used(self, input_content: str, output_card: WebCard) -> int:
        """
        Estimate token usage for the analysis operation.

        Args:
            input_content: Input content
            output_card: Generated WebCard

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for English text
        input_tokens = len(input_content) // 4

        # Estimate output tokens from WebCard content
        output_text = (
            output_card.title
            + output_card.large_summary
            + " ".join(output_card.facts)
            + " ".join(output_card.dates)
            + " ".join(output_card.links)
        )
        output_tokens = len(output_text) // 4

        return input_tokens + output_tokens


class AIManager:
    """
    High-level manager for AI operations in SelfLayer.

    This class provides a convenient interface for managing multiple AI
    operations and maintaining application-wide AI state.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the AI manager.

        Args:
            api_key: Gemini API key (uses environment if None)
        """
        self.api_key = api_key
        self._analyzer: ContentAnalyzer | None = None
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        Initialize AI services.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self._analyzer = ContentAnalyzer(api_key=self.api_key)
            self._is_initialized = True
            logger.info("AI Manager initialized successfully")
            return True
        except APIError as e:
            logger.error(f"Failed to initialize AI Manager: {e}")
            return False

    @property
    def is_ready(self) -> bool:
        """Check if AI services are ready for use."""
        return self._is_initialized and self._analyzer is not None

    async def analyze_web_content(
        self, content: str, url: str, **kwargs: Any
    ) -> AIResponse:
        """
        Analyze web content using the content analyzer.

        Args:
            content: Web content to analyze
            url: Source URL
            **kwargs: Additional context parameters

        Returns:
            AIResponse with analysis results
        """
        if not self.is_ready:
            return AIResponse(
                success=False,
                error_message="AI services not initialized",
                model_used="unknown",
            )

        return await self._analyzer.analyze_content(content, url, kwargs)

    async def stream_web_analysis(
        self, content: str, url: str, **kwargs: Any
    ) -> AsyncIterator[WebCard | dict[str, Any]]:
        """
        Stream web content analysis.

        Args:
            content: Web content to analyze
            url: Source URL
            **kwargs: Additional context parameters

        Yields:
            Analysis progress updates and final WebCard
        """
        if not self.is_ready:
            yield {
                "status": "error",
                "progress": 0.0,
                "message": "AI services not initialized",
            }
            return

        async for result in self._analyzer.stream_analysis(content, url, kwargs):
            yield result


# Global AI manager instance
_ai_manager: AIManager | None = None


def get_ai_manager() -> AIManager:
    """Get or create the global AI manager instance."""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
    return _ai_manager


async def quick_analyze(content: str, url: str, **kwargs: Any) -> AIResponse:
    """
    Quick content analysis using the global AI manager.

    Args:
        content: Web content to analyze
        url: Source URL
        **kwargs: Additional parameters

    Returns:
        AIResponse with analysis results
    """
    manager = get_ai_manager()
    if not manager.is_ready:
        manager.initialize()

    return await manager.analyze_web_content(content, url, **kwargs)


# Export public interface
__all__ = [
    "ContentAnalyzer",
    "AIManager",
    "ContentAnalysisContext",
    "APIError",
    "get_ai_manager",
    "quick_analyze",
]
