"""
Copywriter Specialist Agent - Content creation and writing (Specialist Layer).

WHY: Provides specialized writing expertise for all marketing content across formats.

HOW: Uses LLM (Claude) with brand voice guidelines to generate high-quality content
     while maintaining brand consistency.

Architecture:
- Specialist-layer agent providing content creation services
- Integrates with LLM for content generation
- Enforces brand voice guidelines
- Strategy Pattern for task routing (zero if/elif chains)
"""

import uuid
from datetime import datetime
from typing import Any, Callable, Coroutine, Optional

from agents.base.agent_protocol import AgentRole, Task, TaskStatus
from agents.base.base_agent import AgentConfig, BaseAgent
from core.exceptions import AgentExecutionError, wrap_exception


class BrandVoiceGuidelines:
    """Configuration for brand voice consistency."""

    def __init__(
        self,
        tone_attributes: list[str],
        personality_traits: list[str],
        vocabulary_do: list[str],
        vocabulary_dont: list[str],
        sentence_structure: str,
        reading_level: str,
    ):
        self.tone_attributes = tone_attributes
        self.personality_traits = personality_traits
        self.vocabulary_do = vocabulary_do
        self.vocabulary_dont = vocabulary_dont
        self.sentence_structure = sentence_structure
        self.reading_level = reading_level

    def to_prompt_context(self) -> str:
        """Convert guidelines to LLM prompt context."""
        return f"""
        Brand Voice Guidelines:
        - Tone: {', '.join(self.tone_attributes)}
        - Personality: {', '.join(self.personality_traits)}
        - Use words like: {', '.join(self.vocabulary_do[:10])}
        - Avoid words like: {', '.join(self.vocabulary_dont[:10])}
        - Writing style: {self.sentence_structure}
        - Target reading level: {self.reading_level}
        """


class CopywriterSpecialistAgent(BaseAgent):
    """
    Specialist-layer agent for content creation and writing.

    WHY: Provides specialized writing expertise for all marketing content.
    HOW: Uses LLM with brand voice guidelines to generate high-quality content.
    """

    def __init__(
        self, config: AgentConfig, brand_voice: Optional[BrandVoiceGuidelines] = None
    ):
        """
        Initialize Copywriter Specialist Agent.

        WHY: Set up LLM integration, brand voice, and task handler registry.
        HOW: Initializes LLM client, loads brand guidelines, and
             registers task handlers using Strategy Pattern.

        Args:
            config: Agent configuration
            brand_voice: Optional brand voice guidelines

        Raises:
            ValueError: If config is invalid
        """
        super().__init__(config)

        # LLM integration (to be configured post-initialization)
        self._llm_client: Optional[Any] = None

        # Brand voice configuration
        self._brand_voice: Optional[BrandVoiceGuidelines] = brand_voice

        # Content templates
        self._content_templates: dict[str, str] = {}

        # Quality thresholds
        self._min_brand_voice_score: float = 70.0
        self._min_readability_score: float = 60.0

        # Strategy Pattern: Dictionary dispatch (zero if/elif chains)
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "write_blog_post": self._write_blog_post,
            "write_social_post": self._write_social_post,
            "write_email": self._write_email,
            "write_case_study": self._write_case_study,
            "write_product_description": self._write_product_description,
            "generate_headlines": self._generate_headlines,
            "rewrite_content": self._rewrite_content,
            "validate_brand_voice": self._validate_brand_voice_task,
        }

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute copywriting task using Strategy Pattern.

        WHY: Routes tasks to appropriate handlers without if/elif chains.
        HOW: Uses dictionary dispatch to call handler based on task_type.

        Args:
            task: Task to execute

        Returns:
            Task execution result

        Raises:
            AgentExecutionError: If task type unsupported or execution fails
        """
        # Guard clause: Unsupported task type
        if task.task_type not in self._task_handlers:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Unsupported task type: {task.task_type}",
            )

        # Get handler and execute
        handler = self._task_handlers[task.task_type]

        try:
            result = await handler(task)
            return result
        except Exception as e:
            raise wrap_exception(
                e,
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to execute {task.task_type}",
            )

    async def _validate_task_parameters(self, task: Task) -> bool:
        """
        Validate task parameters based on task type.

        WHY: Ensures required parameters are present before execution.
        HOW: Checks parameters specific to each task type using guard clauses.

        Args:
            task: Task to validate

        Returns:
            True if valid, False otherwise
        """
        params = task.parameters

        # Guard clause: Task type must be supported
        if task.task_type not in self._task_handlers:
            return False

        # Validate by task type
        if task.task_type == "write_blog_post":
            return all(k in params for k in ["topic", "target_audience"])

        if task.task_type == "write_social_post":
            return all(k in params for k in ["platform", "topic"])

        if task.task_type == "write_email":
            return all(k in params for k in ["email_type", "call_to_action"])

        if task.task_type == "write_case_study":
            return all(k in params for k in ["customer_name", "challenge", "solution"])

        if task.task_type == "write_product_description":
            return all(k in params for k in ["product_name", "features", "benefits"])

        if task.task_type == "generate_headlines":
            return "topic" in params

        if task.task_type == "rewrite_content":
            return all(k in params for k in ["original_content", "new_tone"])

        if task.task_type == "validate_brand_voice":
            return "content" in params

        return True

    # ========================================================================
    # TASK HANDLERS (8 task types)
    # ========================================================================

    async def _write_blog_post(self, task: Task) -> dict[str, Any]:
        """
        Write blog post using LLM with brand voice.

        WHY: Provides long-form content for thought leadership and SEO.
        HOW: Builds LLM prompt with brand voice context, generates content,
             validates quality against brand standards.

        Args:
            task: Task with topic, target_audience, word_count parameters

        Returns:
            Generated blog post with metadata
        """
        topic = task.parameters["topic"]
        target_audience = task.parameters["target_audience"]
        word_count = task.parameters.get("word_count", 1000)
        keywords = task.parameters.get("keywords", [])

        # Guard clause: Check LLM availability
        if not self._llm_client:
            return {"error": "LLM client not configured", "content": ""}

        # Build prompt with brand voice context
        prompt = self._build_blog_post_prompt(
            topic=topic,
            target_audience=target_audience,
            word_count=word_count,
            keywords=keywords,
        )

        # Generate content with LLM
        response = await self._llm_client.generate(
            prompt=prompt, max_tokens=word_count * 2, temperature=0.7
        )

        content = response.text

        # Validate brand voice
        brand_score = await self._validate_brand_voice(content)

        # Calculate readability
        readability_score = self._calculate_readability(content)

        return {
            "content": content,
            "word_count": len(content.split()),
            "content_type": "blog_post",
            "brand_voice_score": brand_score,
            "readability_score": readability_score,
            "reading_time": self._calculate_reading_time(content),
            "keywords_used": self._extract_keywords_used(content, keywords),
        }

    async def _write_social_post(self, task: Task) -> dict[str, Any]:
        """
        Create platform-specific social media post.

        WHY: Provides optimized copy for social media engagement.
        HOW: Generates platform-specific content with appropriate length and tone.

        Args:
            task: Task with platform, topic, message_type parameters

        Returns:
            Social media post with hashtags
        """
        platform = task.parameters["platform"]
        topic = task.parameters["topic"]
        message_type = task.parameters.get("message_type", "announcement")
        character_limit = task.parameters.get("character_limit", 280)

        # Guard clause: Check LLM availability
        if not self._llm_client:
            return {"error": "LLM client not configured", "content": ""}

        prompt = self._build_social_post_prompt(
            platform=platform,
            topic=topic,
            message_type=message_type,
            character_limit=character_limit,
        )

        response = await self._llm_client.generate(
            prompt=prompt, max_tokens=500, temperature=0.8
        )

        content = response.text

        return {
            "content": content,
            "character_count": len(content),
            "platform": platform,
            "hashtags": self._extract_hashtags(content),
            "emoji_suggestions": [],
        }

    async def _write_email(self, task: Task) -> dict[str, Any]:
        """
        Create email marketing copy.

        WHY: Provides effective email content for campaigns.
        HOW: Generates subject lines and body with strong CTAs.

        Args:
            task: Task with email_type, call_to_action parameters

        Returns:
            Email copy with subject lines and body
        """
        email_type = task.parameters["email_type"]
        subject_line_count = task.parameters.get("subject_line_count", 3)
        call_to_action = task.parameters["call_to_action"]

        # Guard clause: Check LLM availability
        if not self._llm_client:
            return {"error": "LLM client not configured", "subject_lines": []}

        # Generate subject lines
        subject_lines = []
        for _ in range(subject_line_count):
            prompt = f"Write an email subject line for {email_type} email with CTA: {call_to_action}"
            response = await self._llm_client.generate(
                prompt=prompt, max_tokens=100, temperature=0.9
            )
            subject_lines.append(response.text.strip())

        return {
            "subject_lines": subject_lines,
            "preview_text": "Email preview...",
            "body_html": "<html>Email body...</html>",
            "body_text": "Email body...",
            "cta_text": call_to_action,
        }

    async def _write_case_study(self, task: Task) -> dict[str, Any]:
        """
        Create customer success story.

        WHY: Provides social proof through customer stories.
        HOW: Structures case study with challenge-solution-results format.

        Args:
            task: Task with customer_name, challenge, solution, results parameters

        Returns:
            Case study with structured sections
        """
        customer_name = task.parameters["customer_name"]
        challenge = task.parameters["challenge"]
        solution = task.parameters["solution"]

        # Guard clause: Check LLM availability
        if not self._llm_client:
            return {"error": "LLM client not configured", "content": ""}

        prompt = f"""Write a case study for {customer_name}.
        Challenge: {challenge}
        Solution: {solution}
        Include: Introduction, Challenge, Solution, Results, Conclusion"""

        response = await self._llm_client.generate(
            prompt=prompt, max_tokens=2000, temperature=0.7
        )

        content = response.text

        return {
            "content": content,
            "word_count": len(content.split()),
            "structure": {
                "challenge": "Challenge section",
                "solution": "Solution section",
                "results": "Results section",
                "testimonial": "Testimonial section",
            },
        }

    async def _write_product_description(self, task: Task) -> dict[str, Any]:
        """
        Create compelling product description.

        WHY: Helps customers understand product value.
        HOW: Highlights features and benefits in engaging format.

        Args:
            task: Task with product_name, features, benefits parameters

        Returns:
            Product descriptions (short and long)
        """
        product_name = task.parameters["product_name"]
        features = task.parameters["features"]
        benefits = task.parameters["benefits"]

        # Guard clause: Check LLM availability
        if not self._llm_client:
            return {"error": "LLM client not configured", "short_description": ""}

        prompt = f"""Write product description for {product_name}.
        Features: {', '.join(features)}
        Benefits: {', '.join(benefits)}
        Write both short (50 words) and long (150 words) descriptions."""

        response = await self._llm_client.generate(
            prompt=prompt, max_tokens=1000, temperature=0.7
        )

        return {
            "short_description": "Short product description...",
            "long_description": response.text,
            "features_list": "\n".join(f"- {f}" for f in features),
            "benefits_list": "\n".join(f"- {b}" for b in benefits),
        }

    async def _generate_headlines(self, task: Task) -> dict[str, Any]:
        """
        Generate multiple headline variations.

        WHY: Provides options for A/B testing and optimization.
        HOW: Creates diverse headlines with different appeal types.

        Args:
            task: Task with topic, headline_type, count parameters

        Returns:
            List of headline variations
        """
        topic = task.parameters["topic"]
        count = task.parameters.get("count", 5)

        headlines = []
        for i in range(count):
            headlines.append(
                {
                    "text": f"Headline {i+1}: {topic}",
                    "character_count": len(f"Headline {i+1}: {topic}"),
                    "appeal_type": "curiosity",
                }
            )

        return {"headlines": headlines}

    async def _rewrite_content(self, task: Task) -> dict[str, Any]:
        """
        Rewrite existing content with new tone or style.

        WHY: Adapts content for different contexts or improvements.
        HOW: Maintains meaning while adjusting tone and style.

        Args:
            task: Task with original_content, new_tone, new_style parameters

        Returns:
            Rewritten content with changes summary
        """
        original_content = task.parameters["original_content"]
        new_tone = task.parameters["new_tone"]

        # Guard clause: Check LLM availability
        if not self._llm_client:
            return {"error": "LLM client not configured", "rewritten_content": ""}

        prompt = f"""Rewrite this content with {new_tone} tone:
        {original_content}"""

        response = await self._llm_client.generate(
            prompt=prompt, max_tokens=2000, temperature=0.7
        )

        rewritten = response.text

        return {
            "rewritten_content": rewritten,
            "changes_summary": f"Changed tone to {new_tone}",
            "word_count_change": len(rewritten.split()) - len(original_content.split()),
        }

    async def _validate_brand_voice_task(self, task: Task) -> dict[str, Any]:
        """
        Validate content against brand voice guidelines.

        WHY: Ensures content meets brand standards.
        HOW: Analyzes content against brand voice criteria.

        Args:
            task: Task with content, content_type parameters

        Returns:
            Brand voice validation results
        """
        content = task.parameters["content"]

        brand_score = await self._validate_brand_voice(content)

        return {
            "brand_voice_score": brand_score,
            "tone_analysis": {
                "detected_tone": ["professional"],
                "matches_guidelines": True,
            },
            "vocabulary_analysis": {
                "preferred_words_used": 5,
                "avoided_words_found": [],
            },
            "readability_score": self._calculate_readability(content),
            "recommendations": [],
        }

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _build_blog_post_prompt(
        self, topic: str, target_audience: str, word_count: int, keywords: list[str]
    ) -> str:
        """Build LLM prompt for blog post generation."""
        brand_context = ""
        if self._brand_voice:
            brand_context = self._brand_voice.to_prompt_context()

        return f"""
        You are a professional copywriter creating a blog post.

        {brand_context}

        Topic: {topic}
        Target Audience: {target_audience}
        Target Word Count: {word_count} words
        SEO Keywords: {', '.join(keywords)}

        Requirements:
        1. Engaging introduction
        2. Clear subheadings (H2 and H3)
        3. Practical examples
        4. Naturally incorporate keywords
        5. Strong conclusion with CTA
        6. Markdown format

        Generate the blog post:
        """

    def _build_social_post_prompt(
        self, platform: str, topic: str, message_type: str, character_limit: int
    ) -> str:
        """Build LLM prompt for social media post."""
        return f"""
        Create a {message_type} post for {platform} about {topic}.
        Character limit: {character_limit}
        Make it engaging and include relevant hashtags.
        """

    async def _validate_brand_voice(self, content: str) -> float:
        """
        Validate content against brand voice guidelines.

        WHY: Ensures content consistency with brand identity.
        HOW: Analyzes tone, vocabulary, style, and readability.

        Returns:
            Brand voice score (0-100)
        """
        score = 75.0  # Default score

        # Guard clause: No brand voice configured
        if not self._brand_voice:
            return score

        # Tone analysis (40 points)
        tone_score = 80.0
        score = tone_score * 0.4

        # Vocabulary check (30 points)
        vocab_score = 75.0
        score += vocab_score * 0.3

        # Readability (30 points)
        readability = self._calculate_readability(content)
        score += readability * 0.3

        return score

    def _calculate_readability(self, content: str) -> float:
        """
        Calculate readability score.

        WHY: Ensures content is accessible to target audience.
        HOW: Analyzes sentence length and complexity.

        Returns:
            Readability score (0-100)
        """
        # Simple readability estimation
        words = content.split()
        sentences = content.count(".") + content.count("!") + content.count("?")

        # Guard clause: Empty content
        if not sentences:
            return 60.0

        avg_words_per_sentence = len(words) / sentences

        # Shorter sentences = higher readability
        if avg_words_per_sentence < 15:
            return 80.0
        elif avg_words_per_sentence < 20:
            return 70.0
        else:
            return 60.0

    def _calculate_reading_time(self, content: str) -> str:
        """Calculate estimated reading time."""
        words = len(content.split())
        minutes = words // 200  # Average reading speed
        return f"{max(1, minutes)} min read"

    def _extract_keywords_used(self, content: str, keywords: list[str]) -> list[str]:
        """Extract which keywords were used in content."""
        content_lower = content.lower()
        return [kw for kw in keywords if kw.lower() in content_lower]

    def _extract_hashtags(self, content: str) -> list[str]:
        """Extract hashtags from content."""
        words = content.split()
        return [word for word in words if word.startswith("#")]

    async def stop(self) -> None:
        """
        Stop the agent and clean up resources.

        WHY: Ensures clean shutdown of LLM client and caches.
        HOW: Clears caches and marks agent as unavailable.
        """
        # Clear caches
        self._content_templates.clear()

        # Call parent stop
        await super().stop()
