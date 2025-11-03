"""
Email Specialist Agent for email marketing and automation.

WHY: Provides specialized email campaign management, delivery, A/B testing,
     list segmentation, and performance tracking.

HOW: Integrates with email service providers (SendGrid, Mailchimp) using Strategy
     Pattern for task routing, implements caching for performance data, and ensures
     deliverability best practices.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Optional

from agents.base.agent_protocol import Task, TaskStatus
from agents.base.base_agent import AgentConfig, BaseAgent
from core.exceptions import AgentExecutionError


class EmailTemplate:
    """
    Email template with personalization support.

    WHY: Enables reusable email templates with dynamic personalization.
    HOW: Stores template structure and renders with recipient data.
    """

    def __init__(
        self,
        template_id: str,
        name: str,
        subject_line: str,
        html_content: str,
        text_content: str,
        personalization_fields: list[str],
        category: str,
    ):
        self.template_id = template_id
        self.name = name
        self.subject_line = subject_line
        self.html_content = html_content
        self.text_content = text_content
        self.personalization_fields = personalization_fields
        self.category = category

    def render(self, recipient_data: dict[str, Any]) -> tuple[str, str]:
        """
        Render template with recipient data.

        WHY: Personalizes email content for each recipient.
        HOW: Replaces personalization variables with recipient data.

        Returns:
            Tuple of (rendered_html, rendered_text)
        """
        rendered_html = self.html_content
        rendered_text = self.text_content

        for field in self.personalization_fields:
            value = recipient_data.get(field, "")
            rendered_html = rendered_html.replace(f"{{{{{field}}}}}", value)
            rendered_text = rendered_text.replace(f"{{{{{field}}}}}", value)

        return rendered_html, rendered_text


class EmailSpecialistAgent(BaseAgent):
    """
    Specialist-layer agent for email marketing and automation.

    WHY: Provides specialized email campaign management, delivery, and optimization.
    HOW: Uses email service provider APIs (SendGrid, Mailchimp) with templates,
         segmentation, A/B testing, and performance tracking.
    """

    def __init__(
        self,
        config: AgentConfig,
        sender_name: str = "Company Name",
        sender_email: str = "marketing@example.com",
        reply_to_email: str = "reply@example.com",
    ):
        super().__init__(config)

        # Email service provider clients
        self._esp_client: Optional[Any] = None
        self._template_engine: Optional[Any] = None

        # Sender configuration
        self._sender_name: str = sender_name
        self._sender_email: str = sender_email
        self._reply_to_email: str = reply_to_email

        # Email template cache
        self._template_cache: dict[str, EmailTemplate] = {}

        # Performance tracking cache (30-minute TTL)
        self._performance_cache: dict[str, tuple[dict[str, Any], datetime]] = {}
        self._cache_ttl = timedelta(minutes=30)

        # Campaign cache for validation
        self._campaign_cache: dict[str, Any] = {}

        # Strategy Pattern: Dictionary dispatch for task routing
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_email_campaign": self._create_email_campaign,
            "send_email": self._send_email,
            "schedule_email": self._schedule_email,
            "create_email_template": self._create_email_template,
            "segment_email_list": self._segment_email_list,
            "ab_test_email": self._ab_test_email,
            "track_email_performance": self._track_email_performance,
            "create_drip_campaign": self._create_drip_campaign,
        }

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute email-related task using Strategy Pattern.

        WHY: Routes tasks to appropriate handlers without if/elif chains.
        HOW: Uses dictionary dispatch for clean task delegation.
        """
        # Guard clause: Check if task type is supported
        handler = self._task_handlers.get(task.task_type)
        if not handler:
            raise ValueError(f"Unsupported task type: {task.task_type}")

        # Guard clause: Validate task before execution
        if not await self.validate_task(task):
            raise ValueError(f"Task validation failed for {task.task_id}")

        try:
            # Execute task handler
            result = await handler(task)
            return result

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Email task execution failed: {str(e)}",
                original_exception=e,
            )

    async def validate_task(self, task: Task) -> bool:
        """
        Validate task parameters before execution.

        WHY: Ensures tasks have required parameters for successful execution.
        HOW: Checks for required fields based on task type.
        """
        required_params = {
            "create_email_campaign": [
                "campaign_name",
                "subject_line",
                "recipient_list_id",
            ],
            "send_email": ["campaign_id"],
            "schedule_email": ["campaign_id", "send_time"],
            "create_email_template": ["template_name", "subject_line", "html_content"],
            "segment_email_list": ["list_id", "segment_name", "criteria"],
            "ab_test_email": ["campaign_id", "test_type", "variant_a", "variant_b"],
            "track_email_performance": ["campaign_id"],
            "create_drip_campaign": [
                "campaign_name",
                "trigger_event",
                "email_sequence",
            ],
        }

        # Guard clause: Check if task type is known
        if task.task_type not in required_params:
            return False

        # Check required parameters
        for param in required_params[task.task_type]:
            if param not in task.parameters:
                return False

        return True

    async def _create_email_campaign(self, task: Task) -> dict[str, Any]:
        """
        Create and configure email campaign.

        WHY: Enables structured email campaign creation with templates and segmentation.
        HOW: Uses ESP API to create campaign with template, list, and settings.
        """
        campaign_name = task.parameters["campaign_name"]
        template_id = task.parameters.get("template_id")
        subject_line = task.parameters["subject_line"]
        recipient_list_id = task.parameters["recipient_list_id"]
        html_content = task.parameters.get("html_content")
        text_content = task.parameters.get("text_content")

        # Guard clause: Validate ESP client is available
        if not self._esp_client:
            return {
                "error": "Email service provider not configured",
                "campaign_id": None,
            }

        # Guard clause: Validate either template or content provided
        if not template_id and not html_content:
            return {"error": "Either template_id or html_content required"}

        # Guard clause: Validate template exists if provided
        if template_id and not await self._template_exists(template_id):
            return {"error": f"Template {template_id} not found", "campaign_id": None}

        try:
            # Create campaign via ESP
            campaign = await self._esp_client.create_campaign(
                name=campaign_name,
                subject=subject_line,
                template_id=template_id,
                html_content=html_content,
                text_content=text_content,
                list_id=recipient_list_id,
                from_name=self._sender_name,
                from_email=self._sender_email,
                reply_to=self._reply_to_email,
            )

            # Cache campaign for validation
            self._campaign_cache[campaign.id] = campaign

            # Check spam score
            spam_score = await self._check_spam_score(campaign.preview_html)

            # Validate deliverability
            deliverability_check = await self._validate_deliverability(campaign)

            return {
                "campaign_id": campaign.id,
                "campaign_name": campaign_name,
                "subject_line": subject_line,
                "recipient_count": campaign.recipient_count,
                "spam_score": spam_score,
                "deliverability_status": deliverability_check["status"],
                "preview_url": campaign.preview_url,
                "status": "draft",
            }

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to create email campaign: {str(e)}",
                original_exception=e,
            )

    async def _send_email(self, task: Task) -> dict[str, Any]:
        """
        Send email campaign to recipients.

        WHY: Delivers email to recipient list immediately.
        HOW: Uses ESP API to trigger campaign send.
        """
        campaign_id = task.parameters["campaign_id"]
        test_mode = task.parameters.get("test_mode", False)

        # Guard clause: Validate ESP client
        if not self._esp_client:
            return {"error": "Email service provider not configured"}

        # Guard clause: Validate campaign exists
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        try:
            # Send campaign
            send_result = await self._esp_client.send_campaign(
                campaign_id=campaign_id, test_mode=test_mode
            )

            return {
                "campaign_id": campaign_id,
                "status": "sending",
                "sent_count": send_result.sent_count,
                "send_time": send_result.send_time.isoformat(),
                "estimated_delivery": send_result.estimated_delivery.isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to send email: {str(e)}",
                original_exception=e,
            )

    async def _schedule_email(self, task: Task) -> dict[str, Any]:
        """
        Schedule email campaign for future delivery.

        WHY: Enables planning email sends for optimal times.
        HOW: Uses ESP API to schedule campaign with send time.
        """
        campaign_id = task.parameters["campaign_id"]
        send_time = task.parameters["send_time"]
        timezone = task.parameters.get("timezone", "UTC")

        # Guard clause: Validate ESP client
        if not self._esp_client:
            return {"error": "Email service provider not configured"}

        # Guard clause: Validate campaign exists
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        try:
            # Parse send time
            scheduled_time = datetime.fromisoformat(send_time)

            # Schedule campaign via ESP
            schedule_result = await self._esp_client.schedule_campaign(
                campaign_id=campaign_id, send_time=scheduled_time, timezone=timezone
            )

            return {
                "campaign_id": campaign_id,
                "status": "scheduled",
                "scheduled_send_time": send_time,
                "recipient_count": campaign.recipient_count,
            }

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to schedule email: {str(e)}",
                original_exception=e,
            )

    async def _create_email_template(self, task: Task) -> dict[str, Any]:
        """
        Create reusable email template with personalization.

        WHY: Enables consistent branding and efficient campaign creation.
        HOW: Creates template in ESP with personalization fields.
        """
        template_name = task.parameters["template_name"]
        subject_line = task.parameters["subject_line"]
        html_content = task.parameters["html_content"]
        text_content = task.parameters.get("text_content", "")
        personalization_fields = task.parameters.get("personalization_fields", [])
        category = task.parameters.get("category", "general")

        # Guard clause: Validate ESP client
        if not self._esp_client:
            return {"error": "Email service provider not configured"}

        try:
            # Create template via ESP
            template = await self._esp_client.create_template(
                name=template_name,
                subject=subject_line,
                html_content=html_content,
                text_content=text_content,
                personalization_fields=personalization_fields,
                category=category,
            )

            # Cache template
            email_template = EmailTemplate(
                template_id=template.id,
                name=template_name,
                subject_line=subject_line,
                html_content=html_content,
                text_content=text_content,
                personalization_fields=personalization_fields,
                category=category,
            )
            self._template_cache[template.id] = email_template

            return {
                "template_id": template.id,
                "template_name": template_name,
                "category": category,
                "personalization_fields": personalization_fields,
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to create email template: {str(e)}",
                original_exception=e,
            )

    async def _segment_email_list(self, task: Task) -> dict[str, Any]:
        """
        Segment email list based on criteria.

        WHY: Enables targeted messaging to specific audience segments.
        HOW: Applies filters to subscriber list and creates segment.
        """
        list_id = task.parameters["list_id"]
        segment_name = task.parameters["segment_name"]
        criteria = task.parameters["criteria"]

        # Guard clause: Validate ESP client
        if not self._esp_client:
            return {"error": "Email service provider not configured"}

        # Guard clause: Validate list exists
        email_list = await self._get_list(list_id)
        if not email_list:
            return {"error": f"List {list_id} not found"}

        try:
            # Build segmentation query
            query_conditions = []

            for key, value in criteria.items():
                if key == "engagement":
                    if value == "active":
                        query_conditions.append("opened_last_30_days = true")
                    elif value == "inactive":
                        query_conditions.append("opened_last_90_days = false")
                    elif value == "new":
                        query_conditions.append(
                            "subscription_date > DATE_SUB(NOW(), INTERVAL 30 DAY)"
                        )
                elif key == "location":
                    query_conditions.append(f"country = '{value}'")
                elif key == "industry":
                    query_conditions.append(f"industry = '{value}'")
                else:
                    query_conditions.append(f"{key} = '{value}'")

            # Create segment via ESP
            segment = await self._esp_client.create_segment(
                list_id=list_id, name=segment_name, conditions=query_conditions
            )

            return {
                "segment_id": segment.id,
                "segment_name": segment_name,
                "list_id": list_id,
                "subscriber_count": segment.subscriber_count,
                "criteria": criteria,
                "created_at": segment.created_at.isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to segment email list: {str(e)}",
                original_exception=e,
            )

    async def _ab_test_email(self, task: Task) -> dict[str, Any]:
        """
        Create A/B test for email campaign.

        WHY: Enables data-driven optimization of email performance.
        HOW: Creates variants, sends to test segments, measures results.
        """
        campaign_id = task.parameters["campaign_id"]
        test_type = task.parameters["test_type"]
        variant_a = task.parameters["variant_a"]
        variant_b = task.parameters["variant_b"]
        test_size_percent = task.parameters.get("test_size_percent", 20)

        # Guard clause: Validate ESP client
        if not self._esp_client:
            return {"error": "Email service provider not configured"}

        # Guard clause: Validate campaign exists
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        # Guard clause: Validate test size
        if not 10 <= test_size_percent <= 50:
            return {"error": "Test size must be between 10% and 50%"}

        try:
            # Create variant configurations
            if test_type == "subject_line":
                variant_a_config = {"subject_line": variant_a}
                variant_b_config = {"subject_line": variant_b}
            elif test_type == "content":
                variant_a_config = {"content_id": variant_a}
                variant_b_config = {"content_id": variant_b}
            elif test_type == "send_time":
                variant_a_config = {"send_time": variant_a}
                variant_b_config = {"send_time": variant_b}
            else:
                return {"error": f"Unsupported test type: {test_type}"}

            # Create test via ESP
            ab_test = await self._esp_client.create_ab_test(
                campaign_id=campaign_id,
                test_type=test_type,
                variant_a=variant_a_config,
                variant_b=variant_b_config,
                test_size_percent=test_size_percent,
                winning_metric="open_rate",
            )

            return {
                "ab_test_id": ab_test.id,
                "campaign_id": campaign_id,
                "test_type": test_type,
                "variant_a": variant_a_config,
                "variant_b": variant_b_config,
                "test_size_percent": test_size_percent,
                "test_recipients": ab_test.test_recipients,
                "winner_selection": "automatic",
                "status": "scheduled",
            }

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to create A/B test: {str(e)}",
                original_exception=e,
            )

    async def _track_email_performance(self, task: Task) -> dict[str, Any]:
        """
        Track email campaign performance metrics.

        WHY: Provides insights for optimization and ROI measurement.
        HOW: Fetches analytics from ESP API and calculates key metrics.
        """
        campaign_id = task.parameters["campaign_id"]

        # Check cache first (30-minute TTL)
        cache_key = f"performance_{campaign_id}"
        if cache_key in self._performance_cache:
            cached_data, cached_time = self._performance_cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                cached_data["cached"] = True
                return cached_data

        # Guard clause: Validate ESP client
        if not self._esp_client:
            return {"error": "Email service provider not configured"}

        # Guard clause: Validate campaign exists
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        try:
            # Fetch performance data from ESP
            stats = await self._esp_client.get_campaign_stats(campaign_id)

            # Calculate derived metrics
            open_rate = (
                (stats.opens / stats.delivered) * 100 if stats.delivered > 0 else 0
            )
            click_rate = (
                (stats.clicks / stats.delivered) * 100 if stats.delivered > 0 else 0
            )
            bounce_rate = (stats.bounces / stats.sent) * 100 if stats.sent > 0 else 0
            unsubscribe_rate = (
                (stats.unsubscribes / stats.delivered) * 100
                if stats.delivered > 0
                else 0
            )
            click_to_open_rate = (
                (stats.clicks / stats.opens) * 100 if stats.opens > 0 else 0
            )

            result = {
                "campaign_id": campaign_id,
                "campaign_name": campaign.name,
                "sent": stats.sent,
                "delivered": stats.delivered,
                "opens": stats.opens,
                "unique_opens": stats.unique_opens,
                "clicks": stats.clicks,
                "unique_clicks": stats.unique_clicks,
                "bounces": stats.bounces,
                "spam_complaints": stats.spam_complaints,
                "unsubscribes": stats.unsubscribes,
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "bounce_rate": round(bounce_rate, 2),
                "unsubscribe_rate": round(unsubscribe_rate, 2),
                "click_to_open_rate": round(click_to_open_rate, 2),
                "revenue": stats.revenue if hasattr(stats, "revenue") else 0,
                "timestamp": datetime.now().isoformat(),
                "cached": False,
            }

            # Cache result
            self._performance_cache[cache_key] = (result, datetime.now())

            return result

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to track email performance: {str(e)}",
                original_exception=e,
            )

    async def _create_drip_campaign(self, task: Task) -> dict[str, Any]:
        """
        Create automated drip campaign workflow.

        WHY: Enables automated nurture sequences and onboarding flows.
        HOW: Creates series of timed emails triggered by subscriber actions.
        """
        campaign_name = task.parameters["campaign_name"]
        trigger_event = task.parameters["trigger_event"]
        email_sequence = task.parameters["email_sequence"]

        # Guard clause: Validate ESP client
        if not self._esp_client:
            return {"error": "Email service provider not configured"}

        # Guard clause: Validate email sequence
        if not email_sequence or len(email_sequence) == 0:
            return {"error": "Email sequence cannot be empty"}

        # Guard clause: Validate each email in sequence
        for idx, email in enumerate(email_sequence):
            if "template_id" not in email or "delay_days" not in email:
                return {"error": f"Email {idx} missing required fields"}

        try:
            # Create drip campaign workflow
            workflow_steps = []

            for idx, email in enumerate(email_sequence):
                step = {
                    "step_number": idx + 1,
                    "template_id": email["template_id"],
                    "delay_days": email["delay_days"],
                    "subject_line": email.get("subject_line", ""),
                    "condition": email.get("condition"),
                }
                workflow_steps.append(step)

            # Create automation via ESP
            drip_campaign = await self._esp_client.create_automation(
                name=campaign_name,
                trigger_event=trigger_event,
                workflow_steps=workflow_steps,
            )

            return {
                "drip_campaign_id": drip_campaign.id,
                "campaign_name": campaign_name,
                "trigger_event": trigger_event,
                "email_count": len(email_sequence),
                "workflow_steps": workflow_steps,
                "status": "active",
                "created_at": drip_campaign.created_at.isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Failed to create drip campaign: {str(e)}",
                original_exception=e,
            )

    # Helper methods

    async def _template_exists(self, template_id: str) -> bool:
        """
        Check if template exists.

        WHY: Validates template before using in campaign.
        HOW: Checks template cache and ESP.
        """
        # Check cache first
        if template_id in self._template_cache:
            return True

        # Check ESP if available
        if self._esp_client:
            try:
                template = await self._esp_client.get_template(template_id)
                return template is not None
            except Exception:
                return False

        return False

    async def _get_campaign(self, campaign_id: str) -> Optional[Any]:
        """
        Get campaign by ID.

        WHY: Validates campaign exists before operations.
        HOW: Checks campaign cache and ESP.
        """
        # Check cache first
        if campaign_id in self._campaign_cache:
            return self._campaign_cache[campaign_id]

        # Fetch from ESP if available
        if self._esp_client:
            try:
                campaign = await self._esp_client.get_campaign(campaign_id)
                if campaign:
                    self._campaign_cache[campaign_id] = campaign
                return campaign
            except Exception:
                return None

        return None

    async def _get_list(self, list_id: str) -> Optional[Any]:
        """
        Get email list by ID.

        WHY: Validates list exists before segmentation.
        HOW: Fetches from ESP.
        """
        if not self._esp_client:
            return None

        try:
            email_list = await self._esp_client.get_list(list_id)
            return email_list
        except Exception:
            return None

    async def _check_spam_score(self, html_content: str) -> float:
        """
        Check spam score for email content.

        WHY: Prevents deliverability issues before sending.
        HOW: Analyzes content for spam triggers.
        """
        # Simplified spam score calculation
        # In production, would use SpamAssassin or similar
        spam_score = 0.0

        # Check for spam trigger words
        spam_triggers = ["free", "click here", "act now", "limited time", "buy now"]
        content_lower = html_content.lower()

        for trigger in spam_triggers:
            if trigger in content_lower:
                spam_score += 0.5

        # Check for excessive capitalization
        if sum(1 for c in html_content if c.isupper()) > len(html_content) * 0.3:
            spam_score += 1.0

        # Check for excessive exclamation marks
        exclamation_count = html_content.count("!")
        if exclamation_count > 3:
            spam_score += 0.5 * exclamation_count

        return round(min(spam_score, 10.0), 1)

    async def _validate_deliverability(self, campaign: Any) -> dict[str, Any]:
        """
        Validate email deliverability before sending.

        WHY: Prevents deliverability issues and protects sender reputation.
        HOW: Checks spam score, authentication, content, and compliance.
        """
        issues = []
        warnings = []

        # Check spam score
        spam_score = await self._check_spam_score(campaign.preview_html)
        if spam_score > 5:
            issues.append(f"High spam score: {spam_score}/10")
        elif spam_score > 3:
            warnings.append(f"Moderate spam score: {spam_score}/10")

        # Check for unsubscribe link
        if "unsubscribe" not in campaign.preview_html.lower():
            issues.append("Missing unsubscribe link (CAN-SPAM violation)")

        # Determine status
        if issues:
            status = "failed"
        elif warnings:
            status = "warning"
        else:
            status = "passed"

        return {
            "status": status,
            "spam_score": spam_score,
            "issues": issues,
            "warnings": warnings,
        }
