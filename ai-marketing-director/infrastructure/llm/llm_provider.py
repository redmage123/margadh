"""
LLM Provider - Abstraction layer for LLM API calls.

WHY: Provides unified interface for multiple LLM providers (Anthropic, OpenAI).
     Handles retries, rate limiting, and error handling consistently.

HOW: Factory pattern for provider selection, async API calls, retry logic.

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from infrastructure.llm import LLMProvider

    # Manual resource management
    provider = LLMProvider(
        provider="anthropic",
        model="claude-sonnet-3-5",
        api_key="your_api_key"
    )
    response = await provider.complete("Write a blog post")
    await provider.close()

    # Or use async context manager (recommended)
    async with LLMProvider(
        provider="anthropic",
        model="claude-sonnet-3-5",
        api_key="your_api_key"
    ) as provider:
        response = await provider.complete("Write a blog post")
"""

import asyncio
from typing import Any, AsyncIterator

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore

try:
    import openai
except ImportError:
    openai = None  # type: ignore

from core.exceptions import LLMProviderError, wrap_exception


class LLMProvider:
    """
    Unified LLM provider interface supporting multiple backends.

    WHY: Abstracts LLM API calls, enabling provider switching and consistent error handling.
    HOW: Factory pattern determines client, unified interface for all providers.

    Attributes:
        _provider: Provider name ("anthropic" or "openai")
        _model: Model identifier
        _api_key: API key for authentication
        _client: LLM client instance (provider-specific)
        _max_retries: Maximum retry attempts for transient errors
        _token_usage: Token usage tracking
    """

    SUPPORTED_PROVIDERS = ["anthropic", "openai"]

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """
        Initialize LLM Provider.

        WHY: Sets up LLM client with configuration.
        HOW: Validates inputs, creates provider-specific client.

        Args:
            provider: Provider name ("anthropic" or "openai")
            model: Model identifier (e.g., "claude-sonnet-3-5", "gpt-4")
            api_key: API key for authentication
            max_retries: Maximum retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 60)

        Raises:
            ValueError: If provider invalid or API key missing
            ImportError: If provider SDK not installed
        """
        # Validate inputs
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required and cannot be empty")

        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Invalid provider: {provider}. "
                f"Supported providers: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )

        self._provider = provider
        self._model = model
        self._api_key = api_key
        self._max_retries = max_retries
        self._timeout = timeout
        self._client: Any = None
        self._closed = False

        # Token usage tracking
        self._token_usage = {"input_tokens": 0, "output_tokens": 0}

        # Initialize client
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize provider-specific client.

        WHY: Creates appropriate client based on provider selection.
        HOW: Factory pattern for client creation.

        Raises:
            ImportError: If provider SDK not installed
        """
        if self._provider == "anthropic":
            if anthropic is None:
                raise ImportError(
                    "anthropic library not installed. "
                    "Install with: pip install anthropic"
                )
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)

        elif self._provider == "openai":
            if openai is None:
                raise ImportError(
                    "openai library not installed. Install with: pip install openai"
                )
            self._client = openai.AsyncOpenAI(api_key=self._api_key)

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Get completion from LLM (non-streaming).

        WHY: Core functionality - agents need LLM completions.
        HOW: Sends prompt to LLM API, returns text response with retries.

        Args:
            prompt: User prompt/message
            system: System message (optional)
            temperature: Sampling temperature 0.0-1.0 (default: 0.7)
            max_tokens: Maximum tokens in response (default: 2000)

        Returns:
            Text response from LLM

        Raises:
            LLMProviderError: If completion fails after retries
        """
        for attempt in range(self._max_retries + 1):
            try:
                if self._provider == "anthropic":
                    return await self._complete_anthropic(
                        prompt, system, temperature, max_tokens
                    )
                elif self._provider == "openai":
                    return await self._complete_openai(
                        prompt, system, temperature, max_tokens
                    )
                else:
                    raise ValueError(f"Unsupported provider: {self._provider}")

            except Exception as e:
                # Last attempt - raise error
                if attempt == self._max_retries:
                    raise wrap_exception(
                        exc=e,
                        wrapper_class=LLMProviderError,
                        message=f"LLM completion failed after {self._max_retries + 1} attempts",
                        context={
                            "provider": self._provider,
                            "model": self._model,
                            "attempt": attempt + 1,
                        },
                    ) from e

                # Retry on transient errors with exponential backoff
                wait_time = 2**attempt  # 1s, 2s, 4s, 8s...
                await asyncio.sleep(wait_time)

        # Should never reach here
        raise LLMProviderError("Unexpected error in retry logic")

    async def _complete_anthropic(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int
    ) -> str:
        """
        Complete using Anthropic API.

        WHY: Anthropic-specific API call logic.
        HOW: Constructs messages, calls API, extracts response.
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system:
            kwargs["system"] = system

        response = await self._client.messages.create(**kwargs)

        # Track token usage
        if hasattr(response, "usage"):
            self._token_usage["input_tokens"] += response.usage.input_tokens
            self._token_usage["output_tokens"] += response.usage.output_tokens

        # Extract text from response
        if response.content and len(response.content) > 0:
            return response.content[0].text

        return ""

    async def _complete_openai(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int
    ) -> str:
        """
        Complete using OpenAI API.

        WHY: OpenAI-specific API call logic.
        HOW: Constructs messages, calls API, extracts response.
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Track token usage
        if hasattr(response, "usage"):
            self._token_usage["input_tokens"] += response.usage.prompt_tokens
            self._token_usage["output_tokens"] += response.usage.completion_tokens

        # Extract text from response
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or ""

        return ""

    async def stream(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """
        Get streaming completion from LLM.

        WHY: Streaming provides better UX for long responses.
        HOW: Yields text chunks as they arrive from API.

        Args:
            prompt: User prompt/message
            system: System message (optional)
            temperature: Sampling temperature 0.0-1.0 (default: 0.7)
            max_tokens: Maximum tokens in response (default: 2000)

        Yields:
            Text chunks as they arrive

        Raises:
            LLMProviderError: If streaming fails
        """
        try:
            if self._provider == "anthropic":
                async for chunk in self._stream_anthropic(
                    prompt, system, temperature, max_tokens
                ):
                    yield chunk
            elif self._provider == "openai":
                async for chunk in self._stream_openai(
                    prompt, system, temperature, max_tokens
                ):
                    yield chunk
            else:
                raise ValueError(f"Unsupported provider: {self._provider}")

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=LLMProviderError,
                message="LLM streaming failed",
                context={
                    "provider": self._provider,
                    "model": self._model,
                },
            ) from e

    async def _stream_anthropic(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        """
        Stream using Anthropic API.

        WHY: Anthropic-specific streaming logic.
        HOW: Uses Anthropic streaming API, yields text deltas.
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system:
            kwargs["system"] = system

        async with self._client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield event.delta.text

    async def _stream_openai(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        """
        Stream using OpenAI API.

        WHY: OpenAI-specific streaming logic.
        HOW: Uses OpenAI streaming API, yields content deltas.
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

    def get_token_usage(self) -> dict[str, int]:
        """
        Get cumulative token usage.

        WHY: Monitoring and cost tracking require token counts.
        HOW: Returns tracked token usage.

        Returns:
            Dict with "input_tokens" and "output_tokens" counts
        """
        return self._token_usage.copy()

    async def close(self) -> None:
        """
        Close LLM client connection and release resources.

        WHY: Graceful cleanup prevents resource leaks.
        HOW: Closes client, marks as closed for idempotency.
        """
        if self._client is not None and not self._closed:
            try:
                await self._client.close()
            except Exception:
                # Ignore errors during close
                pass
            finally:
                self._closed = True
                self._client = None

    # ========================================================================
    # Async Context Manager Support
    # ========================================================================

    async def __aenter__(self) -> "LLMProvider":
        """
        Enter async context manager.

        WHY: Enables 'async with LLMProvider(...) as provider:' pattern.
        HOW: Returns self.

        Returns:
            LLMProvider instance
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit async context manager.

        WHY: Automatically closes connection on context exit.
        HOW: Calls close() to release resources.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        await self.close()
