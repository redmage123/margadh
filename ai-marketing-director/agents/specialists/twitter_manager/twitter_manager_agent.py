"""
Twitter Manager Agent - Specialized agent for Twitter/X social media management.

WHY: Automates Twitter content posting, threading, search, and analytics.
     Enables real-time engagement and thought leadership on Twitter/X.

HOW: Integrates with Twitter API v2 (tweepy), uses LLM for content optimization,
     handles Twitter-specific workflows (280 char limit, threading).

Supported Task Types:
- create_tweet: Create and publish Twitter post (280 char limit)
- create_thread: Create threaded tweets for longer content
- optimize_tweet: Optimize tweet content using LLM
- get_analytics: Retrieve profile analytics and metrics
- search_tweets: Search for relevant tweets

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from agents.specialists.twitter_manager import TwitterManagerAgent
    from agents.base import AgentConfig, AgentRole, Task, TaskPriority

    config = AgentConfig(
        agent_id="twitter_001",
        role=AgentRole.TWITTER_MANAGER,
    )

    agent = TwitterManagerAgent(
        config=config,
        api_key="your_api_key",
        api_secret="your_api_secret",
        access_token="your_access_token",
        access_token_secret="your_access_token_secret"
    )

    task = Task(
        task_id="tweet_001",
        task_type="create_tweet",
        priority=TaskPriority.NORMAL,
        parameters={
            "text": "Excited to share our AI insights!",
            "optimize": True
        },
        assigned_to=AgentRole.TWITTER_MANAGER,
        assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
        created_at=datetime.now()
    )

    result = await agent.execute(task)
"""

from datetime import datetime
from typing import Any, Callable, Coroutine

from agents.base.base_agent import BaseAgent
from agents.base.agent_config import AgentConfig
from agents.base.agent_protocol import Task
from core.exceptions import AgentExecutionError, wrap_exception
from infrastructure.integrations.twitter import TwitterClient
from infrastructure.llm.llm_provider import LLMProvider


class TwitterManagerAgent(BaseAgent):
    """
    Specialized agent for Twitter/X social media management.

    WHY: Automates Twitter posting, threading, search, and analytics.
    HOW: Uses Twitter API and LLM for intelligent content management.

    Attributes:
        _api_key: Twitter API key
        _api_secret: Twitter API secret
        _access_token: Twitter OAuth access token
        _access_token_secret: Twitter OAuth access token secret
        _twitter_client: Twitter API client instance
        _llm_provider: LLM provider for content optimization
        _task_handlers: Dictionary mapping task types to handler methods (Strategy Pattern)
    """

    def __init__(
        self,
        config: AgentConfig,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
    ):
        """
        Initialize Twitter Manager Agent.

        WHY: Sets up Twitter client and LLM provider for agent operations.
        HOW: Validates inputs, initializes base agent, creates clients, sets up task handlers.

        Args:
            config: Agent configuration
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter OAuth access token
            access_token_secret: Twitter OAuth access token secret

        Raises:
            ValueError: If any credential missing
        """
        super().__init__(config)

        # Validate required inputs
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required and cannot be empty")

        if not api_secret or not api_secret.strip():
            raise ValueError("api_secret is required and cannot be empty")

        if not access_token or not access_token.strip():
            raise ValueError("access_token is required and cannot be empty")

        if not access_token_secret or not access_token_secret.strip():
            raise ValueError("access_token_secret is required and cannot be empty")

        self._api_key = api_key
        self._api_secret = api_secret
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._twitter_client: TwitterClient | None = None
        self._llm_provider: LLMProvider | None = None

        # Strategy Pattern: Dictionary dispatch for task routing
        # WHY: Eliminates if/elif chains, makes adding new tasks easier (Open/Closed Principle)
        # HOW: Map task types to handler methods
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_tweet": self._create_tweet,
            "create_thread": self._create_thread,
            "optimize_tweet": self._optimize_tweet,
            "get_analytics": self._get_analytics,
            "search_tweets": self._search_tweets,
        }

    @property
    def config(self) -> AgentConfig:
        """
        Get agent configuration.

        WHY: Provides access to agent configuration.
        HOW: Returns stored config.

        Returns:
            Agent configuration
        """
        return self._config

    async def _initialize_clients(self) -> None:
        """
        Initialize Twitter client and LLM provider (lazy initialization).

        WHY: Lazy initialization - only create clients when needed, saves resources.
        HOW: Creates Twitter client and LLM provider instances if not already created.
        """
        # Initialize Twitter client
        if self._twitter_client is None:
            self._twitter_client = TwitterClient(
                api_key=self._api_key,
                api_secret=self._api_secret,
                access_token=self._access_token,
                access_token_secret=self._access_token_secret,
            )
            await self._twitter_client.authenticate()

        # Initialize LLM provider
        # Note: LLM provider initialization skipped in tests when config doesn't have API key
        # In production, API key would be retrieved from environment or secrets manager
        if self._llm_provider is None and self.config.llm_config:
            # LLM provider initialization handled by parent class or dependency injection
            # For now, leave as None - will be mocked in tests
            pass

    async def validate_task(self, task: Task) -> bool:
        """
        Validate whether agent can execute the given task.

        WHY: Pre-execution validation prevents task assignment errors.
        HOW: Uses guard clauses for validation, checks task type and parameters.

        Args:
            task: Task to validate

        Returns:
            True if agent can execute task, False otherwise
        """
        # Guard clause: Check if task type is supported
        if task.task_type not in self._task_handlers:
            return False

        # Validate task-specific parameters using dictionary dispatch
        # WHY: Cleaner than if/elif chain, easier to extend
        validators: dict[str, Callable[[dict[str, Any]], bool]] = {
            "create_tweet": lambda params: "text" in params,
            "create_thread": lambda params: "tweets" in params,
            "optimize_tweet": lambda params: "text" in params,
            "get_analytics": lambda params: True,  # No required params
            "search_tweets": lambda params: "query" in params,
        }

        validator = validators.get(task.task_type)
        if validator is None:
            return True  # No specific validation required

        return validator(task.parameters)

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute Twitter-specific task using Strategy Pattern.

        WHY: Core agent functionality - performs Twitter operations.
        HOW: Uses dictionary dispatch to route to appropriate handler (no if/elif).

        Args:
            task: Task to execute

        Returns:
            Dict with task execution result

        Raises:
            AgentExecutionError: If task execution fails
        """
        # Initialize clients if needed
        await self._initialize_clients()

        # Strategy Pattern: Look up handler in dictionary
        handler = self._task_handlers.get(task.task_type)

        # Guard clause: Unknown task type
        if handler is None:
            raise AgentExecutionError(
                f"Unsupported task type: {task.task_type}",
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

        # Execute handler
        try:
            return await handler(task)
        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=AgentExecutionError,
                message=f"Twitter Manager failed to execute task: {task.task_type}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

    async def _create_tweet(self, task: Task) -> dict[str, Any]:
        """
        Create and publish Twitter post.

        WHY: Primary Twitter functionality - posting content.
        HOW: Optionally optimizes with LLM, then posts via Twitter API.

        Args:
            task: Task with tweet parameters

        Returns:
            Dict with tweet_id and metadata

        Raises:
            AgentExecutionError: If tweet creation fails
        """
        # Extract parameters with defaults
        text = task.parameters["text"]
        optimize = task.parameters.get("optimize", False)

        # Optimize content with LLM if requested
        if optimize and self._llm_provider:
            text = await self._optimize_content_with_llm(
                text=text,
                target_audience="tech-savvy professionals and thought leaders",
            )

        # Create tweet via Twitter API
        assert self._twitter_client is not None
        tweet = await self._twitter_client.create_tweet(text=text)

        return {
            "tweet_id": tweet.get("id"),
            "text": text,
            "optimized": optimize,
            "created_at": tweet.get("created_at"),
            "platform": "twitter",
        }

    async def _create_thread(self, task: Task) -> dict[str, Any]:
        """
        Create threaded tweets for longer content.

        WHY: Twitter's 280 char limit requires threading for longer thoughts.
        HOW: Splits content into tweets, posts as thread via Twitter API.

        Args:
            task: Task with thread tweets

        Returns:
            Dict with tweet_ids and metadata

        Raises:
            AgentExecutionError: If thread creation fails
        """
        # Extract parameters
        tweets = task.parameters["tweets"]

        # Create thread via Twitter API
        assert self._twitter_client is not None
        thread = await self._twitter_client.create_thread(tweets=tweets)

        return {
            "tweet_ids": thread.get("tweet_ids", []),
            "thread_count": thread.get("thread_count", 0),
            "created_at": thread.get("created_at"),
            "platform": "twitter",
            "agent": self.agent_id,
        }

    async def _optimize_tweet(self, task: Task) -> dict[str, Any]:
        """
        Optimize tweet content using LLM.

        WHY: Improve tweet quality and engagement potential.
        HOW: Uses LLM to refine content for Twitter audience.

        Args:
            task: Task with text to optimize

        Returns:
            Dict with optimized_text

        Raises:
            AgentExecutionError: If optimization fails
        """
        text = task.parameters["text"]
        target_audience = task.parameters.get("target_audience", "professionals")

        assert self._llm_provider is not None

        optimized_text = await self._optimize_content_with_llm(
            text=text, target_audience=target_audience
        )

        return {
            "optimized_text": optimized_text.strip(),
            "original_text": text,
            "target_audience": target_audience,
            "agent": self.agent_id,
        }

    async def _get_analytics(self, task: Task) -> dict[str, Any]:
        """
        Get Twitter profile analytics.

        WHY: Track performance and engagement metrics.
        HOW: Fetches profile stats via Twitter API.

        Args:
            task: Task requesting analytics

        Returns:
            Dict with analytics metrics

        Raises:
            AgentExecutionError: If fetching analytics fails
        """
        assert self._twitter_client is not None

        stats = await self._twitter_client.get_profile_stats()

        return {
            **stats,
            "agent": self.agent_id,
            "fetched_at": datetime.now().isoformat(),
        }

    async def _search_tweets(self, task: Task) -> dict[str, Any]:
        """
        Search for relevant tweets.

        WHY: Research and monitoring of relevant content and trends.
        HOW: Uses Twitter search API.

        Args:
            task: Task with search query

        Returns:
            Dict with tweets list

        Raises:
            AgentExecutionError: If search fails
        """
        assert self._twitter_client is not None

        # Extract search parameters
        query = task.parameters["query"]
        limit = task.parameters.get("limit", 10)

        tweets = await self._twitter_client.search_tweets(query=query, limit=limit)

        return {
            "tweets": tweets,
            "count": len(tweets),
            "query": query,
            "agent": self.agent_id,
            "searched_at": datetime.now().isoformat(),
        }

    async def _optimize_content_with_llm(
        self,
        text: str,
        target_audience: str = "professionals",
    ) -> str:
        """
        Optimize content using LLM (helper method).

        WHY: Centralize LLM optimization logic for reuse.
        HOW: Uses prompt engineering to optimize for Twitter (280 char limit).

        Args:
            text: Original content
            target_audience: Target audience description

        Returns:
            Optimized content string
        """
        assert self._llm_provider is not None

        prompt = f"""Optimize the following tweet for maximum engagement on Twitter/X.

Target Audience: {target_audience}
Guidelines:
- Keep it concise and impactful
- Stay within 280 characters
- Use clear, direct language
- Include relevant hashtags if appropriate (max 2-3)
- Maintain authenticity and brand voice

Original tweet:
{text}

Optimized tweet:"""

        return await self._llm_provider.complete(
            prompt=prompt, max_tokens=100, temperature=0.7
        )

    async def stop(self) -> None:
        """
        Gracefully stop the agent.

        WHY: Clean shutdown with resource cleanup.
        HOW: Closes Twitter client and LLM provider connections.
        """
        # Close LLM provider
        if self._llm_provider:
            await self._llm_provider.close()

        # Twitter client cleanup (uses async context manager)
        self._twitter_client = None

        # Call parent stop
        await super().stop()
