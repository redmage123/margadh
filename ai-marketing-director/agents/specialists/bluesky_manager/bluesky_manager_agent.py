"""
Bluesky Manager Agent - Manages Bluesky social media presence.

WHY: Automates content posting, thread creation, and engagement on Bluesky.
     Bluesky is a decentralized social network built on AT Protocol.

HOW: Inherits from BaseAgent, uses BlueskyClient for API interactions,
     uses LLM for content optimization.

Key Responsibilities:
- Post creation and optimization for Bluesky
- Thread creation (Bluesky supports threaded posts)
- Hashtag research and optimization
- Engagement tracking
- Profile analytics

Usage:
    from agents.specialists.bluesky_manager import BlueskyManagerAgent
    from agents.base import AgentConfig, AgentRole

    config = AgentConfig(
        agent_id="bluesky_mgr_001",
        role=AgentRole.BLUESKY_MANAGER,
    )

    agent = BlueskyManagerAgent(
        config=config,
        bluesky_handle="company.bsky.social",
        bluesky_app_password="app-password"
    )

    task = Task(
        task_id="post_001",
        task_type="create_post",
        parameters={
            "content": "Check out our latest blog post!",
            "tags": ["AI", "Marketing", "Tech"]
        }
    )

    result = await agent.execute(task)
"""

from typing import Any

from agents.base import AgentConfig, BaseAgent, Task
from core.exceptions import AgentExecutionError, wrap_exception
from infrastructure.integrations.bluesky import BlueskyClient


class BlueskyManagerAgent(BaseAgent):
    """
    Specialized agent for Bluesky social media management.

    WHY: Automates Bluesky content posting and engagement.
    HOW: Uses BlueskyClient for API calls, LLM for content optimization.

    Supported Task Types:
    - create_post: Create a single post on Bluesky
    - create_thread: Create a threaded post series
    - optimize_post: Optimize post text for Bluesky (300 char limit)
    - get_analytics: Retrieve profile analytics
    - research_hashtags: Research relevant hashtags
    """

    def __init__(
        self,
        config: AgentConfig,
        bluesky_handle: str,
        bluesky_app_password: str,
    ):
        """
        Initialize Bluesky Manager Agent.

        WHY: Sets up agent with Bluesky credentials.
        HOW: Initializes BaseAgent and stores Bluesky credentials.

        Args:
            config: Agent configuration
            bluesky_handle: Bluesky handle (e.g., "company.bsky.social")
            bluesky_app_password: Bluesky app password
        """
        super().__init__(config)

        self._bluesky_handle = bluesky_handle
        self._bluesky_app_password = bluesky_app_password
        self._bluesky_client: BlueskyClient | None = None

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute Bluesky management task.

        WHY: Routes task to appropriate handler based on task_type.
        HOW: Matches task_type to handler method.

        Args:
            task: Task to execute

        Returns:
            Task execution result

        Raises:
            AgentExecutionError: If task execution fails
        """
        task_type = task.task_type

        # Initialize Bluesky client if needed
        if self._bluesky_client is None:
            self._bluesky_client = BlueskyClient(
                handle=self._bluesky_handle,
                app_password=self._bluesky_app_password,
            )
            await self._bluesky_client.authenticate()

        try:
            if task_type == "create_post":
                return await self._create_post(task)
            elif task_type == "create_thread":
                return await self._create_thread(task)
            elif task_type == "optimize_post":
                return await self._optimize_post(task)
            elif task_type == "get_analytics":
                return await self._get_analytics(task)
            elif task_type == "research_hashtags":
                return await self._research_hashtags(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=AgentExecutionError,
                message=f"Bluesky Manager failed to execute task: {task_type}",
                context={
                    "agent_id": self.config.agent_id,
                    "task_id": task.task_id,
                    "task_type": task_type,
                    "bluesky_handle": self._bluesky_handle,
                },
            ) from e

    async def _create_post(self, task: Task) -> dict[str, Any]:
        """
        Create a post on Bluesky.

        WHY: Core functionality - publishing content.
        HOW: Uses BlueskyClient to post, optionally optimizes with LLM.

        Expected Parameters:
            content: Post text content
            tags: Optional list of hashtags
            optimize: Whether to optimize with LLM (default: False)

        Returns:
            Post details including URI and CID
        """
        content = task.parameters.get("content", "")
        tags = task.parameters.get("tags", [])
        optimize = task.parameters.get("optimize", False)

        if not content:
            raise ValueError("content parameter is required for create_post")

        # Optimize content with LLM if requested
        if optimize:
            optimized = await self._optimize_content_with_llm(content, tags)
            content = optimized["content"]
            if "tags" in optimized:
                tags = optimized["tags"]

        # Create post via Bluesky API
        post_result = await self._bluesky_client.create_post(
            text=content,
            tags=tags,
        )

        return {
            "status": "posted",
            "post_uri": post_result["uri"],
            "post_cid": post_result["cid"],
            "content": content,
            "tags": tags,
            "platform": "bluesky",
        }

    async def _create_thread(self, task: Task) -> dict[str, Any]:
        """
        Create a threaded post series on Bluesky.

        WHY: Longer content requires threading.
        HOW: Creates multiple posts, each replying to previous.

        Expected Parameters:
            posts: List of post texts for thread
            tags: Optional hashtags (added to first post)

        Returns:
            Thread details with all post URIs
        """
        posts = task.parameters.get("posts", [])
        tags = task.parameters.get("tags", [])

        if not posts:
            raise ValueError("posts parameter is required for create_thread")

        thread_uris = []
        reply_to = None

        # Create first post with tags
        first_post = await self._bluesky_client.create_post(
            text=posts[0],
            tags=tags,
            reply_to=reply_to,
        )
        thread_uris.append(first_post["uri"])
        reply_to = first_post["uri"]

        # Create remaining posts as replies
        for post_text in posts[1:]:
            post = await self._bluesky_client.create_post(
                text=post_text,
                reply_to=reply_to,
            )
            thread_uris.append(post["uri"])
            reply_to = post["uri"]

        return {
            "status": "thread_created",
            "thread_uris": thread_uris,
            "post_count": len(thread_uris),
            "platform": "bluesky",
        }

    async def _optimize_post(self, task: Task) -> dict[str, Any]:
        """
        Optimize post content for Bluesky.

        WHY: Bluesky has 300 character limit and specific best practices.
        HOW: Uses LLM to optimize content, hashtags, and engagement.

        Expected Parameters:
            content: Original post content
            target_audience: Optional audience description
            tone: Optional tone (professional, casual, technical, etc.)

        Returns:
            Optimized content and suggested hashtags
        """
        content = task.parameters.get("content", "")
        target_audience = task.parameters.get("target_audience", "general")
        tone = task.parameters.get("tone", "professional")

        if not content:
            raise ValueError("content parameter is required for optimize_post")

        # Use LLM to optimize
        optimized = await self._optimize_content_with_llm(
            content,
            target_audience=target_audience,
            tone=tone,
        )

        return {
            "original_content": content,
            "optimized_content": optimized["content"],
            "suggested_tags": optimized.get("tags", []),
            "character_count": len(optimized["content"]),
            "platform": "bluesky",
        }

    async def _get_analytics(self, task: Task) -> dict[str, Any]:
        """
        Get Bluesky profile analytics.

        WHY: Track performance and growth metrics.
        HOW: Fetches stats via BlueskyClient.

        Returns:
            Profile analytics including follower count, posts, etc.
        """
        stats = await self._bluesky_client.get_profile_stats()

        return {
            "status": "analytics_retrieved",
            "analytics": stats,
            "platform": "bluesky",
        }

    async def _research_hashtags(self, task: Task) -> dict[str, Any]:
        """
        Research relevant hashtags for Bluesky.

        WHY: Effective hashtags increase reach and engagement.
        HOW: Uses LLM to suggest relevant hashtags based on content and industry.

        Expected Parameters:
            topic: Topic or content theme
            industry: Industry context

        Returns:
            List of suggested hashtags with rationale
        """
        topic = task.parameters.get("topic", "")
        industry = task.parameters.get("industry", "")

        if not topic:
            raise ValueError("topic parameter is required for research_hashtags")

        # Use LLM to research hashtags
        prompt = f"""
        Research and suggest effective hashtags for Bluesky posts about: {topic}
        Industry: {industry}

        Provide 5-10 relevant hashtags that would:
        1. Increase visibility
        2. Reach target audience
        3. Be actively used on Bluesky
        4. Not be oversaturated

        Return as JSON with this format:
        {{
            "hashtags": ["tag1", "tag2", ...],
            "rationale": "Brief explanation of hashtag selection"
        }}
        """

        response = await self._llm.complete(prompt)

        # Parse LLM response
        import json

        result = json.loads(response)

        return {
            "status": "hashtags_researched",
            "topic": topic,
            "industry": industry,
            "suggested_hashtags": result.get("hashtags", []),
            "rationale": result.get("rationale", ""),
            "platform": "bluesky",
        }

    async def _optimize_content_with_llm(
        self,
        content: str,
        tags: list[str] | None = None,
        target_audience: str = "general",
        tone: str = "professional",
    ) -> dict[str, Any]:
        """
        Optimize content using LLM.

        WHY: LLM can improve engagement and effectiveness.
        HOW: Uses prompt engineering to optimize for Bluesky.

        Args:
            content: Original content
            tags: Existing hashtags
            target_audience: Target audience description
            tone: Desired tone

        Returns:
            Dict with optimized content and tags
        """
        prompt = f"""
        Optimize this content for Bluesky (decentralized social network):

        Original: {content}
        Target Audience: {target_audience}
        Tone: {tone}
        Current Tags: {tags or "none"}

        Requirements:
        - Maximum 300 characters (Bluesky limit)
        - Engaging and clear
        - Include 2-4 relevant hashtags
        - Maintain key message

        Return as JSON:
        {{
            "content": "optimized post text",
            "tags": ["tag1", "tag2"]
        }}
        """

        response = await self._llm.complete(prompt)

        # Parse LLM response
        import json

        return json.loads(response)

    async def stop(self) -> None:
        """
        Stop agent and cleanup resources.

        WHY: Graceful shutdown of agent and Bluesky client.
        HOW: Calls parent stop(), Bluesky client auto-cleans.
        """
        await super().stop()
        # Bluesky client doesn't require explicit cleanup
        self._bluesky_client = None
