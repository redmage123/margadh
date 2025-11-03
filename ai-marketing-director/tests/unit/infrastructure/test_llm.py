"""
Unit Tests for LLM Provider - Written FIRST (TDD RED).

WHY: Following TDD - write tests before implementation to define behavior.
     This test defines the expected interface and behavior of LLM Provider.

HOW: Tests are written first, will fail initially (RED), then we implement
     the minimal code to pass (GREEN), then refactor.

Test Coverage:
- Initialization and configuration
- Prompt completion (non-streaming)
- Streaming responses
- Error handling (API errors, rate limits, timeouts)
- Retry logic
- Token usage tracking
- Provider-specific behavior
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.exceptions import LLMProviderError


@pytest.mark.unit
class TestLLMProviderInitialization:
    """Test LLM Provider initialization and configuration."""

    @pytest.mark.asyncio
    async def test_llm_provider_initializes_with_anthropic(self):
        """
        TDD RED: LLM Provider should initialize with Anthropic configuration.

        WHY: Validates provider setup for Anthropic.
        EXPECTED: Provider initializes without error.
        """
        from infrastructure.llm import LLMProvider

        provider = LLMProvider(
            provider="anthropic",
            model="claude-sonnet-3-5",
            api_key="test_api_key",
        )

        assert provider is not None
        assert hasattr(provider, "complete")
        assert hasattr(provider, "stream")
        assert hasattr(provider, "close")

    @pytest.mark.asyncio
    async def test_llm_provider_initializes_with_openai(self):
        """
        TDD RED: LLM Provider should initialize with OpenAI configuration.

        WHY: Validates provider setup for OpenAI.
        EXPECTED: Provider initializes without error.
        """
        from infrastructure.llm import LLMProvider

        provider = LLMProvider(
            provider="openai",
            model="gpt-4",
            api_key="test_api_key",
        )

        assert provider is not None

    @pytest.mark.asyncio
    async def test_llm_provider_with_missing_api_key_raises_error(self):
        """
        TDD RED: LLM Provider should require API key.

        WHY: API key is mandatory for LLM providers.
        EXPECTED: Raises ValueError when api_key is missing.
        """
        from infrastructure.llm import LLMProvider

        with pytest.raises(ValueError) as exc_info:
            LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="",  # Empty API key
            )

        assert "api_key" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_llm_provider_with_invalid_provider_raises_error(self):
        """
        TDD RED: LLM Provider should validate provider name.

        WHY: Only supported providers should be allowed.
        EXPECTED: Raises ValueError for invalid provider.
        """
        from infrastructure.llm import LLMProvider

        with pytest.raises(ValueError) as exc_info:
            LLMProvider(
                provider="invalid_provider",
                model="some-model",
                api_key="test_api_key",
            )

        assert "provider" in str(exc_info.value).lower()


@pytest.mark.unit
class TestLLMProviderCompletion:
    """Test LLM completion functionality (non-streaming)."""

    @pytest.fixture
    async def mock_provider(self):
        """Create LLM Provider with mocked client."""
        from infrastructure.llm import LLMProvider

        with patch("infrastructure.llm.llm_provider.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            provider = LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="test_api_key",
            )
            provider._client = mock_client

            yield provider

            await provider.close()

    @pytest.mark.asyncio
    async def test_complete_returns_text_response(self, mock_provider):
        """
        TDD RED: complete() should return text response from LLM.

        WHY: Core functionality - agents need to get LLM completions.
        EXPECTED: Returns string response from LLM.
        """
        # Mock Anthropic response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is the LLM response.")]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)

        mock_provider._client.messages.create = AsyncMock(return_value=mock_response)

        prompt = "Write a blog post about AI."
        response = await mock_provider.complete(prompt)

        assert response is not None
        assert isinstance(response, str)
        assert response == "This is the LLM response."

    @pytest.mark.asyncio
    async def test_complete_with_system_message(self, mock_provider):
        """
        TDD RED: complete() should support system message.

        WHY: System messages guide LLM behavior.
        EXPECTED: System message included in API call.
        """
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)

        mock_provider._client.messages.create = AsyncMock(return_value=mock_response)

        prompt = "Write a blog."
        system = "You are a professional copywriter."

        await mock_provider.complete(prompt, system=system)

        # Verify system message was passed
        call_kwargs = mock_provider._client.messages.create.call_args[1]
        assert "system" in call_kwargs
        assert call_kwargs["system"] == system

    @pytest.mark.asyncio
    async def test_complete_with_temperature_parameter(self, mock_provider):
        """
        TDD RED: complete() should accept temperature parameter.

        WHY: Temperature controls randomness of output.
        EXPECTED: Temperature passed to API.
        """
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)

        mock_provider._client.messages.create = AsyncMock(return_value=mock_response)

        await mock_provider.complete("Test prompt", temperature=0.8)

        call_kwargs = mock_provider._client.messages.create.call_args[1]
        assert call_kwargs["temperature"] == 0.8

    @pytest.mark.asyncio
    async def test_complete_with_max_tokens_parameter(self, mock_provider):
        """
        TDD RED: complete() should accept max_tokens parameter.

        WHY: Max tokens controls response length.
        EXPECTED: Max tokens passed to API.
        """
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)

        mock_provider._client.messages.create = AsyncMock(return_value=mock_response)

        await mock_provider.complete("Test prompt", max_tokens=1000)

        call_kwargs = mock_provider._client.messages.create.call_args[1]
        assert call_kwargs["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_complete_tracks_token_usage(self, mock_provider):
        """
        TDD RED: complete() should track token usage.

        WHY: Token tracking needed for monitoring and cost control.
        EXPECTED: Returns token usage information.
        """
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.usage = MagicMock(input_tokens=50, output_tokens=100)

        mock_provider._client.messages.create = AsyncMock(return_value=mock_response)

        response = await mock_provider.complete("Test prompt")

        # Should have token usage tracking
        assert hasattr(mock_provider, "get_token_usage")
        usage = mock_provider.get_token_usage()
        assert usage["input_tokens"] >= 50
        assert usage["output_tokens"] >= 100


@pytest.mark.unit
class TestLLMProviderStreaming:
    """Test LLM streaming functionality."""

    @pytest.fixture
    async def mock_provider(self):
        """Create LLM Provider with mocked client."""
        from infrastructure.llm import LLMProvider

        with patch("infrastructure.llm.llm_provider.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            provider = LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="test_api_key",
            )
            provider._client = mock_client

            yield provider

            await provider.close()

    @pytest.mark.asyncio
    async def test_stream_yields_text_chunks(self, mock_provider):
        """
        TDD RED: stream() should yield text chunks as they arrive.

        WHY: Streaming provides better UX for long responses.
        EXPECTED: Async generator yields text chunks.
        """

        # Mock streaming response
        async def mock_stream():
            chunks = ["Hello", " ", "world", "!"]
            for chunk_text in chunks:
                chunk = MagicMock()
                chunk.type = "content_block_delta"
                chunk.delta = MagicMock(text=chunk_text)
                yield chunk

            # Final message
            final = MagicMock()
            final.type = "message_stop"
            yield final

        mock_stream_manager = AsyncMock()
        mock_stream_manager.__aenter__.return_value = mock_stream()

        mock_provider._client.messages.stream = MagicMock(
            return_value=mock_stream_manager
        )

        # Collect streamed chunks
        chunks = []
        async for chunk in mock_provider.stream("Test prompt"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert "".join(chunks) == "Hello world!"

    @pytest.mark.asyncio
    async def test_stream_handles_empty_response(self, mock_provider):
        """
        TDD RED: stream() should handle empty streaming response.

        WHY: Edge case - empty responses should be handled gracefully.
        EXPECTED: No chunks yielded, no error.
        """

        async def mock_empty_stream():
            final = MagicMock()
            final.type = "message_stop"
            yield final

        mock_stream_manager = AsyncMock()
        mock_stream_manager.__aenter__.return_value = mock_empty_stream()

        mock_provider._client.messages.stream = MagicMock(
            return_value=mock_stream_manager
        )

        chunks = []
        async for chunk in mock_provider.stream("Test prompt"):
            chunks.append(chunk)

        assert len(chunks) == 0


@pytest.mark.unit
class TestLLMProviderErrorHandling:
    """Test LLM error handling."""

    @pytest.fixture
    async def mock_provider(self):
        """Create LLM Provider with mocked client."""
        from infrastructure.llm import LLMProvider

        with patch("infrastructure.llm.llm_provider.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            provider = LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="test_api_key",
            )
            provider._client = mock_client

            yield provider

            await provider.close()

    @pytest.mark.asyncio
    async def test_complete_wraps_api_errors(self, mock_provider):
        """
        TDD RED: complete() should wrap API errors in LLMProviderError.

        WHY: Exception wrapping standard (Golden Rule #7).
        EXPECTED: API errors wrapped in LLMProviderError.
        """
        mock_provider._client.messages.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        with pytest.raises(LLMProviderError) as exc_info:
            await mock_provider.complete("Test prompt")

        assert exc_info.value.original_exception is not None
        assert "api error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_complete_handles_rate_limit_error(self, mock_provider):
        """
        TDD RED: complete() should handle rate limit errors.

        WHY: Rate limits are common, need graceful handling.
        EXPECTED: Raises LLMProviderError with rate limit context.
        """

        class MockRateLimitError(Exception):
            pass

        mock_provider._client.messages.create = AsyncMock(
            side_effect=MockRateLimitError("Rate limit exceeded")
        )

        with pytest.raises(LLMProviderError) as exc_info:
            await mock_provider.complete("Test prompt")

        error_msg = str(exc_info.value).lower()
        assert "rate limit" in error_msg or "error" in error_msg

    @pytest.mark.asyncio
    async def test_complete_handles_timeout(self, mock_provider):
        """
        TDD RED: complete() should handle timeout errors.

        WHY: Network timeouts can occur, need handling.
        EXPECTED: Raises LLMProviderError with timeout context.
        """
        import asyncio

        mock_provider._client.messages.create = AsyncMock(
            side_effect=asyncio.TimeoutError("Request timed out")
        )

        with pytest.raises(LLMProviderError) as exc_info:
            await mock_provider.complete("Test prompt")

        assert exc_info.value.original_exception is not None


@pytest.mark.unit
class TestLLMProviderRetryLogic:
    """Test LLM retry logic for transient failures."""

    @pytest.fixture
    async def mock_provider(self):
        """Create LLM Provider with mocked client."""
        from infrastructure.llm import LLMProvider

        with patch("infrastructure.llm.llm_provider.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            provider = LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="test_api_key",
                max_retries=3,
            )
            provider._client = mock_client

            yield provider

            await provider.close()

    @pytest.mark.asyncio
    async def test_complete_retries_on_transient_error(self, mock_provider):
        """
        TDD RED: complete() should retry on transient errors.

        WHY: Transient errors (network issues) should be retried.
        EXPECTED: Retries up to max_retries times.
        """
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Success after retry")]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)

        # Fail first 2 times, succeed on 3rd
        mock_provider._client.messages.create = AsyncMock(
            side_effect=[
                Exception("Transient error 1"),
                Exception("Transient error 2"),
                mock_response,
            ]
        )

        response = await mock_provider.complete("Test prompt")

        assert response == "Success after retry"
        assert mock_provider._client.messages.create.call_count == 3

    @pytest.mark.asyncio
    async def test_complete_respects_max_retries(self, mock_provider):
        """
        TDD RED: complete() should respect max_retries limit.

        WHY: Prevent infinite retry loops.
        EXPECTED: Raises error after max_retries attempts.
        """
        mock_provider._client.messages.create = AsyncMock(
            side_effect=Exception("Persistent error")
        )

        with pytest.raises(LLMProviderError):
            await mock_provider.complete("Test prompt")

        # Should try original + 3 retries = 4 total
        assert mock_provider._client.messages.create.call_count == 4


@pytest.mark.unit
class TestLLMProviderResourceManagement:
    """Test resource management and cleanup."""

    @pytest.mark.asyncio
    async def test_close_closes_client_connection(self):
        """
        TDD RED: close() should close API client connection.

        WHY: Resource cleanup prevents leaks.
        EXPECTED: Client closed, resources released.
        """
        from infrastructure.llm import LLMProvider

        with patch("infrastructure.llm.llm_provider.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            provider = LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="test_api_key",
            )
            provider._client = mock_client

            await provider.close()

            # Verify client was closed
            mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self):
        """
        TDD RED: close() can be called multiple times safely.

        WHY: Prevents errors in cleanup code.
        EXPECTED: Second close() doesn't raise exception.
        """
        from infrastructure.llm import LLMProvider

        with patch("infrastructure.llm.llm_provider.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            provider = LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="test_api_key",
            )
            provider._client = mock_client

            # Close twice - should not raise
            await provider.close()
            await provider.close()

            # Verify close called at least once
            assert mock_client.close.call_count >= 1

    @pytest.mark.asyncio
    async def test_context_manager_support(self):
        """
        TDD RED: LLM Provider should support async context manager.

        WHY: Enables 'async with' pattern for automatic cleanup.
        EXPECTED: Context manager closes resources on exit.
        """
        from infrastructure.llm import LLMProvider

        with patch("infrastructure.llm.llm_provider.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            async with LLMProvider(
                provider="anthropic",
                model="claude-sonnet-3-5",
                api_key="test_api_key",
            ) as provider:
                assert provider is not None
                provider._client = mock_client

            # After context exit, client should be closed
            mock_client.close.assert_called_once()


@pytest.mark.unit
def test_llm_provider_protocol_interface():
    """
    TDD RED: LLM Provider should satisfy expected interface.

    WHY: Type safety and contract validation.
    EXPECTED: LLM Provider has all required methods.
    """
    from infrastructure.llm import LLMProvider

    required_methods = ["complete", "stream", "close", "get_token_usage"]

    for method in required_methods:
        assert hasattr(LLMProvider, method), f"LLMProvider missing method: {method}"
