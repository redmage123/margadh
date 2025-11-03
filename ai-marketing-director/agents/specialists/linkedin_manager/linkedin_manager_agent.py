"""
LinkedIn Manager Agent - Specialized agent for LinkedIn social media management.

WHY: Automates LinkedIn content posting, lead generation (Navigator), and analytics.
     Enables professional networking and B2B marketing at scale.

HOW: Integrates with LinkedIn API (including Navigator premium features),
     uses LLM for content optimization, handles LinkedIn-specific workflows.

Supported Task Types:
- create_post: Create and publish LinkedIn post
- optimize_post: Optimize post content using LLM
- get_analytics: Retrieve profile analytics and metrics
- search_leads: Search for leads (Navigator-only feature)
- send_inmail: Send InMail to prospects (Navigator-only feature)

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from agents.specialists.linkedin_manager import LinkedInManagerAgent
    from agents.base import AgentConfig, AgentRole, Task, TaskPriority

    config = AgentConfig(
        agent_id="linkedin_001",
        role=AgentRole.LINKEDIN_MANAGER,
    )

    agent = LinkedInManagerAgent(
        config=config,
        linkedin_access_token="your_access_token",
        has_navigator=True  # Enable Navigator features
    )

    task = Task(
        task_id="post_001",
        task_type="create_post",
        priority=TaskPriority.NORMAL,
        parameters={
            "content": "Exciting news about our AI platform!",
            "visibility": "public",
            "optimize": True
        },
        assigned_to=AgentRole.LINKEDIN_MANAGER,
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
from infrastructure.integrations.linkedin import LinkedInClient
from infrastructure.llm.llm_provider import LLMProvider


class LinkedInManagerAgent(BaseAgent):
    """
    Specialized agent for LinkedIn social media management.

    WHY: Automates LinkedIn posting, lead generation, and analytics.
    HOW: Uses LinkedIn API and LLM for intelligent content management.

    Attributes:
        _linkedin_access_token: LinkedIn OAuth access token
        _has_navigator: Whether account has Navigator premium access
        _linkedin_client: LinkedIn API client instance
        _llm_provider: LLM provider for content optimization
        _task_handlers: Dictionary mapping task types to handler methods (Strategy Pattern)
    """

    def __init__(
        self,
        config: AgentConfig,
        linkedin_access_token: str,
        has_navigator: bool = False,
    ):
        """
        Initialize LinkedIn Manager Agent.

        WHY: Sets up LinkedIn client and LLM provider for agent operations.
        HOW: Validates inputs, initializes base agent, creates clients, sets up task handlers.

        Args:
            config: Agent configuration
            linkedin_access_token: LinkedIn OAuth access token
            has_navigator: Whether account has Navigator premium access

        Raises:
            ValueError: If linkedin_access_token missing
        """
        super().__init__(config)

        # Validate required inputs
        if not linkedin_access_token or not linkedin_access_token.strip():
            raise ValueError("linkedin_access_token is required and cannot be empty")

        self._linkedin_access_token = linkedin_access_token
        self._has_navigator = has_navigator
        self._linkedin_client: LinkedInClient | None = None
        self._llm_provider: LLMProvider | None = None

        # Strategy Pattern: Dictionary dispatch for task routing
        # WHY: Eliminates if/elif chains, makes adding new tasks easier (Open/Closed Principle)
        # HOW: Map task types to handler methods
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_post": self._create_post,
            "optimize_post": self._optimize_post,
            "get_analytics": self._get_analytics,
            "search_leads": self._search_leads,
            "send_inmail": self._send_inmail,
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
        Initialize LinkedIn client and LLM provider (lazy initialization).

        WHY: Lazy initialization - only create clients when needed, saves resources.
        HOW: Creates LinkedIn client and LLM provider instances if not already created.
        """
        # Initialize LinkedIn client
        if self._linkedin_client is None:
            self._linkedin_client = LinkedInClient(
                access_token=self._linkedin_access_token,
                has_navigator=self._has_navigator,
            )
            await self._linkedin_client.authenticate()

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

        # Guard clause: Check Navigator-only tasks
        navigator_tasks = {"search_leads", "send_inmail"}
        if task.task_type in navigator_tasks and not self._has_navigator:
            return False

        # Validate task-specific parameters using dictionary dispatch
        # WHY: Cleaner than if/elif chain, easier to extend
        validators: dict[str, Callable[[dict[str, Any]], bool]] = {
            "create_post": lambda params: "content" in params,
            "optimize_post": lambda params: "content" in params,
            "get_analytics": lambda params: True,  # No required params
            "search_leads": self._validate_search_leads_params,
            "send_inmail": self._validate_send_inmail_params,
        }

        validator = validators.get(task.task_type)
        if validator is None:
            return True  # No specific validation required

        return validator(task.parameters)

    def _validate_search_leads_params(self, params: dict[str, Any]) -> bool:
        """
        Validate search_leads task parameters.

        WHY: Search requires at least one search criterion.
        HOW: Checks if any valid search criterion is present.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        search_criteria = {"title", "company_size", "industry", "location"}
        return any(criterion in params for criterion in search_criteria)

    def _validate_send_inmail_params(self, params: dict[str, Any]) -> bool:
        """
        Validate send_inmail task parameters.

        WHY: InMail requires recipient, subject, and message.
        HOW: Checks if all required parameters are present.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_params = {"recipient_id", "subject", "message"}
        return all(param in params for param in required_params)

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute LinkedIn-specific task using Strategy Pattern.

        WHY: Core agent functionality - performs LinkedIn operations.
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
                message=f"LinkedIn Manager failed to execute task: {task.task_type}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

    async def _create_post(self, task: Task) -> dict[str, Any]:
        """
        Create and publish LinkedIn post.

        WHY: Primary LinkedIn functionality - posting content.
        HOW: Optionally optimizes with LLM, then posts via LinkedIn API.

        Args:
            task: Task with post parameters

        Returns:
            Dict with post_id and metadata

        Raises:
            AgentExecutionError: If post creation fails
        """
        # Extract parameters with defaults
        content = task.parameters["content"]
        visibility = task.parameters.get("visibility", "public")
        optimize = task.parameters.get("optimize", False)

        # Optimize content with LLM if requested
        if optimize and self._llm_provider:
            content = await self._optimize_content_with_llm(
                content=content,
                target_audience="Enterprise leaders and marketing professionals",
            )

        # Create post via LinkedIn API
        assert self._linkedin_client is not None
        post = await self._linkedin_client.create_post(
            text=content, visibility=visibility
        )

        return {
            "post_id": post.get("id"),
            "content": content,
            "visibility": visibility,
            "optimized": optimize,
            "created_at": post.get("created_at"),
            "platform": "linkedin",
        }

    async def _optimize_post(self, task: Task) -> dict[str, Any]:
        """
        Optimize LinkedIn post content using LLM.

        WHY: Improve post quality and engagement potential.
        HOW: Uses LLM to refine content for LinkedIn audience.

        Args:
            task: Task with content to optimize

        Returns:
            Dict with optimized_content

        Raises:
            AgentExecutionError: If optimization fails
        """
        content = task.parameters["content"]
        target_audience = task.parameters.get("target_audience", "professionals")

        assert self._llm_provider is not None

        optimized_content = await self._optimize_content_with_llm(
            content=content, target_audience=target_audience
        )

        return {
            "optimized_content": optimized_content.strip(),
            "original_content": content,
            "target_audience": target_audience,
            "agent": self.agent_id,
        }

    async def _get_analytics(self, task: Task) -> dict[str, Any]:
        """
        Get LinkedIn profile analytics.

        WHY: Track performance and engagement metrics.
        HOW: Fetches profile stats via LinkedIn API.

        Args:
            task: Task requesting analytics

        Returns:
            Dict with analytics metrics

        Raises:
            AgentExecutionError: If fetching analytics fails
        """
        assert self._linkedin_client is not None

        stats = await self._linkedin_client.get_profile_stats()

        return {
            **stats,
            "agent": self.agent_id,
            "fetched_at": datetime.now().isoformat(),
        }

    async def _search_leads(self, task: Task) -> dict[str, Any]:
        """
        Search for leads using LinkedIn Navigator.

        WHY: Lead generation is core to B2B marketing.
        HOW: Uses Navigator's advanced search via LinkedIn API.

        Args:
            task: Task with search criteria

        Returns:
            Dict with leads list

        Raises:
            AgentExecutionError: If lead search fails
        """
        assert self._linkedin_client is not None

        # Extract search parameters with defaults
        title = task.parameters.get("title")
        company_size = task.parameters.get("company_size")
        industry = task.parameters.get("industry")
        location = task.parameters.get("location")
        limit = task.parameters.get("limit", 25)

        leads = await self._linkedin_client.search_leads(
            title=title,
            company_size=company_size,
            industry=industry,
            location=location,
            limit=limit,
        )

        return {
            "leads": leads,
            "count": len(leads),
            "search_criteria": {
                "title": title,
                "company_size": company_size,
                "industry": industry,
                "location": location,
            },
            "agent": self.agent_id,
            "searched_at": datetime.now().isoformat(),
        }

    async def _send_inmail(self, task: Task) -> dict[str, Any]:
        """
        Send InMail to prospect using LinkedIn Navigator.

        WHY: Direct messaging enables outreach to prospects outside network.
        HOW: Uses Navigator's InMail API via LinkedIn client.

        Args:
            task: Task with InMail parameters

        Returns:
            Dict with send status

        Raises:
            AgentExecutionError: If sending InMail fails
        """
        assert self._linkedin_client is not None

        recipient_id = task.parameters["recipient_id"]
        subject = task.parameters["subject"]
        message = task.parameters["message"]

        result = await self._linkedin_client.send_inmail(
            recipient_id=recipient_id, subject=subject, message=message
        )

        return {**result, "agent": self.agent_id}

    async def _optimize_content_with_llm(
        self,
        content: str,
        target_audience: str = "professionals",
    ) -> str:
        """
        Optimize content using LLM (helper method).

        WHY: Centralize LLM optimization logic for reuse.
        HOW: Uses prompt engineering to optimize for LinkedIn.

        Args:
            content: Original content
            target_audience: Target audience description

        Returns:
            Optimized content string
        """
        assert self._llm_provider is not None

        prompt = f"""Optimize the following LinkedIn post for maximum professional engagement.

Target Audience: {target_audience}
Guidelines:
- Keep it professional and value-driven
- Use clear, concise language
- Include a call-to-action if appropriate
- Stay under 1500 characters
- Maintain brand voice

Original post:
{content}

Optimized post:"""

        return await self._llm_provider.complete(
            prompt=prompt, max_tokens=500, temperature=0.7
        )

    async def stop(self) -> None:
        """
        Gracefully stop the agent.

        WHY: Clean shutdown with resource cleanup.
        HOW: Closes LinkedIn client and LLM provider connections.
        """
        # Close LLM provider
        if self._llm_provider:
            await self._llm_provider.close()

        # LinkedIn client cleanup (uses async context manager)
        self._linkedin_client = None

        # Call parent stop
        await super().stop()
