"""
Director of Communications Agent - Executive-layer brand governance.

WHY: Ensures brand voice consistency, leads crisis communications, approves
     messaging strategy, and oversees PR across all marketing channels.

HOW: Reviews content for brand alignment, manages crisis response protocols,
     coordinates messaging across campaigns, monitors brand sentiment, and
     trains agents on brand standards using Strategy Pattern dispatch.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Optional

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig, BaseAgent
from core.exceptions import AgentExecutionError


# TaskResult definition for Strategy Pattern execution
class TaskResult:
    """
    Task result wrapper for strategy pattern handlers.

    WHY: Provides standardized result format for all task handlers.
    HOW: Wraps status and result dict from handler execution.
    """

    def __init__(self, status: TaskStatus, result: dict[str, Any]):
        """Initialize task result."""
        self.status = status
        self.result = result


class DirectorOfCommunicationsAgent(BaseAgent):
    """
    Director of Communications Agent (Executive Layer).

    WHY: Provides brand voice authority, messaging strategy, crisis communications,
         and PR oversight to ensure brand consistency across all channels.

    HOW: Reviews content for brand compliance, approves messaging frameworks,
         manages crisis response, coordinates cross-campaign messaging, monitors
         sentiment, trains agents, audits communications, and reports brand health.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Director of Communications Agent.

        WHY: Sets up brand guidelines, crisis protocols, sentiment tracking,
             and task handler dispatch for Strategy Pattern.

        HOW: Calls super().__init__, initializes brand state (guidelines,
             crisis protocols, sentiment tracking), and creates task handler
             dictionary for Strategy Pattern dispatch.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Brand guidelines and standards
        self._brand_guidelines: dict[str, Any] = {
            "version": "1.0.0",
            "personality": ["professional", "innovative", "trustworthy", "helpful"],
            "tone": {
                "professional_casual_scale": 7,  # 1-10 (1=very casual, 10=very formal)
                "serious_playful_scale": 6,
                "reserved_enthusiastic_scale": 7,
                "respect_irreverent_scale": 8,
            },
            "voice_characteristics": {
                "clarity": "Use simple, clear language",
                "empathy": "Show understanding of customer challenges",
                "expertise": "Demonstrate knowledge without jargon",
                "authenticity": "Be genuine, avoid marketing speak",
            },
            "prohibited_terms": ["revolutionary", "game-changing", "synergy"],
            "preferred_terminology": {
                "customers": "clients",
                "users": "customers",
                "cheap": "cost-effective",
            },
            "messaging_pillars": [
                "Innovation through AI",
                "Customer-first approach",
                "Measurable results",
            ],
        }

        # Approved messaging frameworks
        self._approved_messaging: list[dict[str, Any]] = []

        # Crisis management state
        self._crisis_protocols: dict[str, Any] = {
            "severity_levels": {
                "low": {"response_time": "24h", "approval": "director"},
                "medium": {"response_time": "4h", "approval": "director"},
                "high": {"response_time": "1h", "approval": "cmo"},
                "critical": {"response_time": "15min", "approval": "cmo"},
            },
            "active_crises": [],
            "crisis_history": [],
        }

        # Sentiment tracking
        self._sentiment_tracking: dict[str, float] = {
            "linkedin": 0.75,
            "twitter": 0.68,
            "email": 0.82,
            "blog": 0.79,
            "overall": 0.76,
        }

        # Compliance tracking
        self._compliance_reports: list[dict[str, Any]] = []

        # Training records
        self._training_history: dict[str, list[dict[str, Any]]] = {}

        # Agent references (optional, set via dependency injection)
        self._cmo_agent: Optional[Any] = None
        self._vp_marketing_agent: Optional[Any] = None
        self._content_manager: Optional[Any] = None
        self._copywriter: Optional[Any] = None
        self._llm_client: Optional[Any] = None

        # Strategy Pattern dispatch
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "review_brand_voice": self._review_brand_voice,
            "approve_messaging": self._approve_messaging,
            "manage_crisis": self._manage_crisis,
            "define_brand_guidelines": self._define_brand_guidelines,
            "review_pr_materials": self._review_pr_materials,
            "coordinate_messaging": self._coordinate_messaging,
            "monitor_brand_sentiment": self._monitor_brand_sentiment,
            "train_brand_voice": self._train_brand_voice,
            "audit_communications": self._audit_communications,
            "report_brand_health": self._report_brand_health,
        }

    async def execute(self, task: Task) -> "AgentResult":
        """
        Execute a task with graceful unknown task type handling.

        WHY: Provides graceful error handling for unknown task types.
        HOW: Checks if task type is supported before delegating to BaseAgent.execute.

        Args:
            task: Task to execute

        Returns:
            AgentResult with COMPLETED or FAILED status
        """
        from agents.base.agent_protocol import AgentResult

        # Check if task type is unknown - return FAILED result gracefully
        if task.task_type not in self._task_handlers:
            return AgentResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                result={"error": f"Unknown task type: {task.task_type}"},
                error=f"Unknown task type: {task.task_type}",
                metadata={"agent_id": self.agent_id},
                created_at=datetime.now(),
            )

        # Delegate to BaseAgent.execute for normal processing
        return await super().execute(task)

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute a task using Strategy Pattern dispatch (BaseAgent override).

        WHY: Routes tasks to appropriate handlers without if/elif chains.
        HOW: Looks up handler in dictionary, executes it, wraps exceptions.

        Args:
            task: Task to execute

        Returns:
            dict with task execution results

        Raises:
            AgentExecutionError: If task execution fails
        """
        # Lookup handler (unknown types already handled in execute())
        handler = self._task_handlers[task.task_type]

        try:
            result = await handler(task)
            return result

        except AgentExecutionError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to execute task {task.task_type}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    # ========================================================================
    # Task Handler Implementations
    # ========================================================================

    async def _review_brand_voice(self, task: Task) -> dict[str, Any]:
        """
        Review content for brand voice consistency.

        WHY: Ensures all content meets brand voice standards before publication.
        HOW: Analyzes content using LLM against brand guidelines, scores compliance,
             provides feedback, and determines approval status.

        Args:
            task: Task with content_id, content_type, content_text, review_level

        Returns:
            dict with content_id, review_status, brand_voice_score, feedback,
            violations, recommendations
        """
        # Guard clause: Missing required parameters
        if "content_text" not in task.parameters:
            return {
                "content_id": task.parameters.get("content_id", "unknown"),
                "review_status": "error",
                "error": "Missing required parameter: content_text",
            }

        try:
            content_text = task.parameters["content_text"]
            content_id = task.parameters.get("content_id", "unknown")

            # Check for prohibited terms
            violations = []
            for term in self._brand_guidelines["prohibited_terms"]:
                if term.lower() in content_text.lower():
                    violations.append(f"Prohibited term used: '{term}'")

            # Use LLM for detailed brand voice analysis if available
            brand_voice_score = 85  # Default score
            feedback = "Content demonstrates good brand voice alignment."
            llm_feedback = None

            if self._llm_client:
                prompt = f"""Analyze the following content for brand voice consistency.

Brand Guidelines:
- Personality: {', '.join(self._brand_guidelines['personality'])}
- Voice Characteristics: {self._brand_guidelines['voice_characteristics']}
- Messaging Pillars: {', '.join(self._brand_guidelines['messaging_pillars'])}

Content:
{content_text}

Provide a score (0-100) and detailed feedback on brand voice alignment.
Format: "Overall Score: XX/100" followed by analysis."""

                llm_response = await self._llm_client.generate(
                    prompt=prompt, temperature=0.3, max_tokens=1000
                )
                llm_feedback = llm_response.text

                # Extract score from LLM response
                score_match = re.search(r"(\d+)/100", llm_feedback)
                if score_match:
                    brand_voice_score = int(score_match.group(1))

                feedback = llm_feedback

            # Adjust score based on violations
            if violations:
                brand_voice_score = max(0, brand_voice_score - (len(violations) * 10))

            # Determine review status
            if brand_voice_score >= 70 and not violations:
                review_status = (
                    "approved" if brand_voice_score >= 85 else "approved_with_notes"
                )
            else:
                review_status = (
                    "revision_needed" if brand_voice_score >= 60 else "rejected"
                )

            return {
                "content_id": content_id,
                "review_status": review_status,
                "brand_voice_score": brand_voice_score,
                "feedback": feedback,
                "violations": violations,
                "recommendations": self._generate_recommendations(
                    brand_voice_score, violations
                ),
                "reviewed_by": self.agent_id,
                "reviewed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to review brand voice",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _approve_messaging(self, task: Task) -> dict[str, Any]:
        """
        Approve messaging strategy for campaigns.

        WHY: Ensures campaign messaging aligns with brand strategy and guidelines.
        HOW: Evaluates messaging framework, checks for strategic alignment,
             determines approval status, and escalates major changes to CMO.

        Args:
            task: Task with campaign_id, messaging_framework, target_audience,
                  channels, key_messages

        Returns:
            dict with campaign_id, approval_status, messaging_score, feedback,
            escalated, escalation_reason
        """
        # Guard clause: Missing required parameters
        if "campaign_id" not in task.parameters:
            return {
                "approval_status": "error",
                "error": "Missing required parameter: campaign_id",
            }

        try:
            campaign_id = task.parameters["campaign_id"]
            messaging_framework = task.parameters.get("messaging_framework", {})
            key_messages = task.parameters.get("key_messages", [])

            # Check if this requires CMO escalation
            escalate_to_cmo = False
            escalation_reason = None

            positioning = messaging_framework.get("positioning", "")
            if any(
                keyword in positioning.lower()
                for keyword in ["rebrand", "repositioning", "brand identity"]
            ):
                escalate_to_cmo = True
                escalation_reason = (
                    "Strategic brand repositioning requires CMO approval"
                )

            # Analyze messaging alignment
            messaging_score = 85
            feedback_points = []

            # Check key messages against brand pillars
            pillar_alignment = sum(
                1
                for message in key_messages
                if any(
                    pillar.lower() in message.lower()
                    for pillar in self._brand_guidelines["messaging_pillars"]
                )
            )

            if pillar_alignment > 0:
                feedback_points.append(
                    f"Strong alignment with {pillar_alignment} brand messaging pillar(s)"
                )
            else:
                messaging_score -= 15
                feedback_points.append(
                    "Consider stronger alignment with brand messaging pillars"
                )

            # Use LLM for detailed analysis if available
            if self._llm_client and not escalate_to_cmo:
                prompt = f"""Analyze this campaign messaging framework for brand alignment.

Brand Personality: {', '.join(self._brand_guidelines['personality'])}
Messaging Pillars: {', '.join(self._brand_guidelines['messaging_pillars'])}

Campaign Messaging:
- Positioning: {positioning}
- Key Messages: {', '.join(key_messages)}

Provide a score (0-100) and feedback on messaging alignment."""

                llm_response = await self._llm_client.generate(
                    prompt=prompt, temperature=0.3, max_tokens=800
                )

                score_match = re.search(r"(\d+)/100", llm_response.text)
                if score_match:
                    messaging_score = int(score_match.group(1))

            # Determine approval status
            if escalate_to_cmo:
                approval_status = "escalated"
                if self._cmo_agent:
                    # Log escalation
                    feedback_points.append(f"Escalated to CMO: {escalation_reason}")
            elif messaging_score >= 80:
                approval_status = "approved"
            elif messaging_score >= 65:
                approval_status = "conditional"
            else:
                approval_status = "revision_needed"

            # Store approved messaging
            if approval_status == "approved":
                self._approved_messaging.append(
                    {
                        "campaign_id": campaign_id,
                        "messaging_framework": messaging_framework,
                        "approved_at": datetime.now().isoformat(),
                        "approved_by": self.agent_id,
                    }
                )

            return {
                "campaign_id": campaign_id,
                "approval_status": approval_status,
                "messaging_score": messaging_score,
                "feedback": (
                    " | ".join(feedback_points)
                    if feedback_points
                    else "Messaging framework approved"
                ),
                "escalated": escalate_to_cmo,
                "escalation_reason": escalation_reason,
                "approved_by": self.agent_id,
                "approved_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to approve messaging",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _manage_crisis(self, task: Task) -> dict[str, Any]:
        """
        Lead crisis communications response.

        WHY: Ensures rapid, coordinated response to brand threats and crises.
        HOW: Assesses severity, activates crisis protocols, drafts holding statement,
             coordinates response team, and escalates critical issues to CMO.

        Args:
            task: Task with crisis_id, crisis_type, severity, description,
                  affected_channels, stakeholders

        Returns:
            dict with crisis_id, response_status, holding_statement,
            escalated_to_cmo, response_plan, communication_schedule
        """
        # Guard clause: Missing required parameters
        if "severity" not in task.parameters:
            return {
                "response_status": "error",
                "error": "Missing required parameter: severity",
            }

        try:
            crisis_id = task.parameters.get(
                "crisis_id", f"crisis_{uuid.uuid4().hex[:8]}"
            )
            severity = task.parameters["severity"].lower()
            crisis_type = task.parameters.get("crisis_type", "general")
            description = task.parameters.get("description", "")

            # Check severity level and escalation requirements
            protocol = self._crisis_protocols["severity_levels"].get(severity, {})
            escalate_to_cmo = severity in ["high", "critical"]

            # Generate holding statement
            holding_statement = self._generate_holding_statement(
                crisis_type, description
            )

            # Activate crisis response
            response_status = "escalated" if severity == "critical" else "activated"

            if severity == "critical":
                # Critical crises immediately escalate to CMO
                response_status = "escalated"
                escalated_to_cmo = True

                if self._cmo_agent:
                    # Log escalation
                    self._crisis_protocols["active_crises"].append(
                        {
                            "crisis_id": crisis_id,
                            "severity": severity,
                            "escalated_at": datetime.now().isoformat(),
                            "escalated_to": "cmo",
                        }
                    )
            elif severity == "high":
                # High severity escalates after initial response
                escalated_to_cmo = True
                response_status = "in_progress"
            else:
                escalated_to_cmo = False
                response_status = "activated"

            # Create response plan
            response_plan = {
                "immediate_actions": [
                    "Assess situation and gather facts",
                    "Activate crisis response team",
                    "Issue holding statement",
                    "Monitor social media and news channels",
                ],
                "response_time": protocol.get("response_time", "4h"),
                "approval_required": protocol.get("approval", "director"),
                "communication_channels": task.parameters.get("affected_channels", []),
            }

            # Communication schedule
            communication_schedule = self._create_communication_schedule(severity)

            return {
                "crisis_id": crisis_id,
                "response_status": response_status,
                "holding_statement": holding_statement,
                "escalated_to_cmo": escalated_to_cmo,
                "response_plan": response_plan,
                "communication_schedule": communication_schedule,
                "severity": severity,
                "activated_by": self.agent_id,
                "activated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to manage crisis",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _define_brand_guidelines(self, task: Task) -> dict[str, Any]:
        """
        Create or update brand voice guidelines.

        WHY: Maintains authoritative brand voice standards for all agents.
        HOW: Updates guidelines with new standards, versions, and distributes
             to all content-creating agents.

        Args:
            task: Task with guideline_type, brand_personality, tone_attributes,
                  voice_characteristics, prohibited_terms

        Returns:
            dict with guidelines_id, version, brand_guidelines, updated_sections,
            distribution_list
        """
        try:
            guideline_type = task.parameters.get("guideline_type", "update")
            guidelines_id = f"guidelines_{uuid.uuid4().hex[:8]}"

            # Update brand guidelines
            if "brand_personality" in task.parameters:
                self._brand_guidelines["personality"] = task.parameters[
                    "brand_personality"
                ]

            if "tone_attributes" in task.parameters:
                self._brand_guidelines["tone"].update(
                    task.parameters["tone_attributes"]
                )

            if "voice_characteristics" in task.parameters:
                self._brand_guidelines["voice_characteristics"].update(
                    task.parameters["voice_characteristics"]
                )

            if "prohibited_terms" in task.parameters:
                self._brand_guidelines["prohibited_terms"] = task.parameters[
                    "prohibited_terms"
                ]

            # Increment version
            current_version = self._brand_guidelines["version"]
            major, minor, patch = map(int, current_version.split("."))
            if guideline_type == "major":
                new_version = f"{major + 1}.0.0"
            elif guideline_type == "minor":
                new_version = f"{major}.{minor + 1}.0"
            else:
                new_version = f"{major}.{minor}.{patch + 1}"

            self._brand_guidelines["version"] = new_version
            self._brand_guidelines["updated_at"] = datetime.now().isoformat()

            # Determine what sections were updated
            updated_sections = []
            for key in [
                "brand_personality",
                "tone_attributes",
                "voice_characteristics",
                "prohibited_terms",
            ]:
                if key in task.parameters:
                    updated_sections.append(key)

            # Distribution list for agents that need brand voice training
            distribution_list = [
                "copywriter",
                "content_manager",
                "social_media_manager",
                "email_specialist",
            ]

            return {
                "guidelines_id": guidelines_id,
                "version": new_version,
                "brand_guidelines": self._brand_guidelines.copy(),
                "updated_sections": updated_sections,
                "distribution_list": distribution_list,
                "updated_by": self.agent_id,
                "updated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to define brand guidelines",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _review_pr_materials(self, task: Task) -> dict[str, Any]:
        """
        Review press releases and public statements.

        WHY: Ensures PR materials meet brand standards and minimize risk.
        HOW: Reviews content for brand voice, accuracy, legal compliance,
             risk assessment, and provides approval recommendation.

        Args:
            task: Task with material_id, material_type, material_content,
                  distribution_plan, legal_approved

        Returns:
            dict with material_id, approval_status, brand_voice_score,
            pr_standards_score, risk_assessment, recommendations
        """
        # Guard clause: Missing required parameters
        if "material_content" not in task.parameters:
            return {
                "material_id": task.parameters.get("material_id", "unknown"),
                "approval_status": "error",
                "error": "Missing required parameter: material_content",
            }

        try:
            material_id = task.parameters["material_id"]
            material_content = task.parameters["material_content"]
            material_type = task.parameters.get("material_type", "press_release")
            legal_approved = task.parameters.get("legal_approved", False)

            # Brand voice analysis (similar to content review)
            brand_voice_score = 85
            pr_standards_score = 90

            # Check for prohibited terms
            violations = []
            for term in self._brand_guidelines["prohibited_terms"]:
                if term.lower() in material_content.lower():
                    violations.append(f"Prohibited term: '{term}'")
                    brand_voice_score -= 10

            # Use LLM for PR analysis if available
            if self._llm_client:
                prompt = f"""Analyze this PR material for brand voice and professional standards.

Material Type: {material_type}
Content: {material_content}

Evaluate:
1. Brand voice consistency (professional, credible, clear)
2. PR standards (newsworthy, factual, properly structured)
3. Potential risks or concerns

Provide scores and analysis."""

                llm_response = await self._llm_client.generate(
                    prompt=prompt, temperature=0.3, max_tokens=1000
                )

                # Extract scores if present
                scores = re.findall(r"(\d+)/100", llm_response.text)
                if len(scores) >= 2:
                    brand_voice_score = int(scores[0])
                    pr_standards_score = int(scores[1])

            # Risk assessment
            risk_level = "low"
            risk_factors = []

            if not legal_approved:
                risk_level = "medium"
                risk_factors.append("Legal review not completed")

            if violations:
                risk_level = "medium" if risk_level == "low" else "high"
                risk_factors.append(f"{len(violations)} brand guideline violation(s)")

            # Determine approval status
            if brand_voice_score >= 80 and pr_standards_score >= 80 and legal_approved:
                approval_status = "approved"
            elif brand_voice_score >= 70 and pr_standards_score >= 70:
                approval_status = "conditional"
            else:
                approval_status = "revision_needed"

            return {
                "material_id": material_id,
                "approval_status": approval_status,
                "brand_voice_score": brand_voice_score,
                "pr_standards_score": pr_standards_score,
                "risk_assessment": {
                    "level": risk_level,
                    "factors": risk_factors,
                    "legal_approved": legal_approved,
                },
                "recommendations": self._generate_pr_recommendations(
                    brand_voice_score, pr_standards_score, risk_factors
                ),
                "reviewed_by": self.agent_id,
                "reviewed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to review PR materials",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _coordinate_messaging(self, task: Task) -> dict[str, Any]:
        """
        Coordinate messaging across campaigns.

        WHY: Ensures consistent, unified messaging across all campaigns and channels.
        HOW: Creates unified messaging framework, identifies conflicts, resolves
             inconsistencies, and creates coordination plan with timelines.

        Args:
            task: Task with coordination_scope, campaigns, timeframe, channels,
                  primary_message

        Returns:
            dict with coordination_id, unified_messaging_framework,
            coordination_plan, conflicts_resolved, channel_strategies
        """
        # Guard clause: Missing required parameters
        if "campaigns" not in task.parameters:
            return {
                "coordination_id": f"coord_{uuid.uuid4().hex[:8]}",
                "error": "Missing required parameter: campaigns",
            }

        try:
            coordination_id = f"coord_{uuid.uuid4().hex[:8]}"
            campaigns = task.parameters["campaigns"]
            primary_message = task.parameters.get(
                "primary_message", "AI-powered marketing excellence"
            )
            channels = task.parameters.get("channels", [])

            # Create unified messaging framework
            unified_messaging_framework = {
                "primary_message": primary_message,
                "supporting_messages": [
                    f"Message aligned with {pillar}"
                    for pillar in self._brand_guidelines["messaging_pillars"]
                ],
                "tone": self._brand_guidelines["tone"],
                "voice": self._brand_guidelines["voice_characteristics"],
                "campaigns": campaigns,
                "channels": channels,
            }

            # Create coordination plan
            coordination_plan = {
                "timeline": {
                    "start_date": task.parameters.get("timeframe", {}).get(
                        "start_date"
                    ),
                    "end_date": task.parameters.get("timeframe", {}).get("end_date"),
                },
                "campaign_alignment": [
                    {
                        "campaign": campaign,
                        "primary_message": primary_message,
                        "status": "aligned",
                    }
                    for campaign in campaigns
                ],
                "channel_strategies": {
                    channel: {
                        "message_adaptation": f"Adapt for {channel} audience",
                        "frequency": "3x per week",
                    }
                    for channel in channels
                },
                "checkpoints": [
                    "Weekly alignment review",
                    "Mid-campaign messaging audit",
                    "End-of-campaign analysis",
                ],
            }

            # Identify and resolve conflicts
            conflicts_resolved = []
            if len(campaigns) > 2:
                conflicts_resolved.append(
                    {
                        "conflict": "Multiple campaigns running concurrently",
                        "resolution": "Staggered messaging schedule to avoid overlap",
                    }
                )

            return {
                "coordination_id": coordination_id,
                "unified_messaging_framework": unified_messaging_framework,
                "coordination_plan": coordination_plan,
                "conflicts_resolved": conflicts_resolved,
                "campaigns_coordinated": len(campaigns),
                "channels_included": len(channels),
                "coordinated_by": self.agent_id,
                "coordinated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to coordinate messaging",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _monitor_brand_sentiment(self, task: Task) -> dict[str, Any]:
        """
        Monitor brand sentiment across channels.

        WHY: Tracks brand perception and identifies potential reputation issues.
        HOW: Analyzes sentiment data across channels, identifies trends,
             detects anomalies, and provides recommendations.

        Args:
            task: Task with monitoring_scope, channels, timeframe, keywords,
                  alert_threshold

        Returns:
            dict with overall_sentiment, channel_sentiment, trending_topics,
            sentiment_trends, alerts, recommendations
        """
        try:
            channels = task.parameters.get(
                "channels", ["linkedin", "twitter", "email", "blog"]
            )
            alert_threshold = task.parameters.get("alert_threshold", -0.10)

            # Get current sentiment from tracking
            channel_sentiment = {}
            for channel in channels:
                channel_sentiment[channel] = self._sentiment_tracking.get(channel, 0.70)

            # Calculate overall sentiment
            overall_sentiment = sum(channel_sentiment.values()) / len(channel_sentiment)

            # Identify trending topics (simulated)
            trending_topics = [
                {
                    "topic": "AI marketing automation",
                    "sentiment": 0.78,
                    "volume": "high",
                },
                {"topic": "marketing ROI", "sentiment": 0.82, "volume": "medium"},
                {"topic": "customer engagement", "sentiment": 0.75, "volume": "medium"},
            ]

            # Detect alerts
            alerts = []
            for channel, sentiment in channel_sentiment.items():
                if sentiment < (self._sentiment_tracking["overall"] + alert_threshold):
                    alerts.append(
                        {
                            "channel": channel,
                            "sentiment": sentiment,
                            "severity": "medium",
                            "message": f"Sentiment drop detected on {channel}",
                        }
                    )

            # Generate sentiment trends
            sentiment_trends = {
                "week_over_week": "+2.5%",
                "month_over_month": "+5.1%",
                "direction": "improving" if overall_sentiment > 0.75 else "stable",
            }

            # Recommendations
            recommendations = self._generate_sentiment_recommendations(
                overall_sentiment, channel_sentiment, alerts
            )

            return {
                "overall_sentiment": round(overall_sentiment, 2),
                "channel_sentiment": channel_sentiment,
                "trending_topics": trending_topics,
                "sentiment_trends": sentiment_trends,
                "alerts": alerts,
                "recommendations": recommendations,
                "monitored_by": self.agent_id,
                "monitored_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to monitor brand sentiment",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _train_brand_voice(self, task: Task) -> dict[str, Any]:
        """
        Train agents on brand voice standards.

        WHY: Ensures all agents understand and apply brand voice consistently.
        HOW: Provides training materials, examples, assessments, and tracks
             completion and proficiency.

        Args:
            task: Task with training_type, target_agents, focus_areas,
                  assessment_required

        Returns:
            dict with training_session_id, agents_trained, training_materials,
            assessment_results, completion_status
        """
        try:
            training_session_id = f"training_{uuid.uuid4().hex[:8]}"
            target_agents = task.parameters.get("target_agents", [])
            focus_areas = task.parameters.get(
                "focus_areas", ["tone", "voice_characteristics"]
            )
            assessment_required = task.parameters.get("assessment_required", False)

            # Create training materials
            training_materials = {
                "guidelines_version": self._brand_guidelines["version"],
                "focus_areas": focus_areas,
                "personality": self._brand_guidelines["personality"],
                "tone": {
                    k: v
                    for k, v in self._brand_guidelines["tone"].items()
                    if k in focus_areas or "tone" in focus_areas
                },
                "voice_characteristics": self._brand_guidelines[
                    "voice_characteristics"
                ],
                "examples": {
                    "good": [
                        "Our AI-powered platform helps you achieve measurable marketing results.",
                        "We understand the challenges marketers face in today's digital landscape.",
                    ],
                    "avoid": [
                        "Revolutionary game-changing synergy!",
                        "Best marketing tool ever created!",
                    ],
                },
                "prohibited_terms": self._brand_guidelines["prohibited_terms"],
            }

            # Record training
            for agent in target_agents:
                if agent not in self._training_history:
                    self._training_history[agent] = []

                self._training_history[agent].append(
                    {
                        "session_id": training_session_id,
                        "trained_at": datetime.now().isoformat(),
                        "focus_areas": focus_areas,
                    }
                )

            # Assessment results (if required)
            assessment_results = {}
            if assessment_required:
                for agent in target_agents:
                    assessment_results[agent] = {
                        "score": 85,  # Simulated score
                        "status": "passed",
                        "areas_for_improvement": [],
                    }

            return {
                "training_session_id": training_session_id,
                "agents_trained": target_agents,
                "training_materials": training_materials,
                "assessment_results": (
                    assessment_results if assessment_required else None
                ),
                "completion_status": "completed",
                "trained_by": self.agent_id,
                "trained_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to train brand voice",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _audit_communications(self, task: Task) -> dict[str, Any]:
        """
        Audit communications for brand compliance.

        WHY: Ensures ongoing adherence to brand standards and identifies issues.
        HOW: Reviews sample of communications, identifies violations, assesses
             compliance rate, and provides corrective recommendations.

        Args:
            task: Task with audit_scope, audit_target, timeframe, sample_size

        Returns:
            dict with audit_id, compliance_summary, violations, recommendations,
            audit_score
        """
        try:
            audit_id = f"audit_{uuid.uuid4().hex[:8]}"
            audit_scope = task.parameters.get("audit_scope", "campaign")
            audit_target = task.parameters.get("audit_target", "all")
            sample_size = task.parameters.get("sample_size", 50)

            # Simulate audit results
            total_reviewed = sample_size
            violations_found = 3  # Simulated
            compliance_rate = (
                (total_reviewed - violations_found) / total_reviewed
            ) * 100

            # Identify violations
            violations = [
                {
                    "content_id": "content_001",
                    "violation_type": "prohibited_term",
                    "severity": "medium",
                    "details": "Use of 'game-changing' in content",
                },
                {
                    "content_id": "content_015",
                    "violation_type": "tone_mismatch",
                    "severity": "low",
                    "details": "Overly casual tone for enterprise audience",
                },
                {
                    "content_id": "content_032",
                    "violation_type": "messaging_misalignment",
                    "severity": "medium",
                    "details": "Does not reference brand messaging pillars",
                },
            ]

            # Compliance summary
            compliance_summary = {
                "total_reviewed": total_reviewed,
                "compliant": total_reviewed - violations_found,
                "violations": violations_found,
                "compliance_rate": round(compliance_rate, 1),
                "audit_period": task.parameters.get("timeframe", {}),
            }

            # Generate recommendations
            recommendations = [
                "Provide refresher training on prohibited terminology",
                "Review tone guidelines for enterprise audience targeting",
                "Enhance messaging pillar integration in content briefs",
            ]

            # Store compliance report
            self._compliance_reports.append(
                {
                    "audit_id": audit_id,
                    "audit_date": datetime.now().isoformat(),
                    "compliance_rate": compliance_rate,
                    "violations": len(violations),
                }
            )

            return {
                "audit_id": audit_id,
                "compliance_summary": compliance_summary,
                "violations": violations,
                "recommendations": recommendations,
                "audit_score": round(compliance_rate, 1),
                "audited_by": self.agent_id,
                "audited_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to audit communications",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    async def _report_brand_health(self, task: Task) -> dict[str, Any]:
        """
        Generate brand health report for CMO.

        WHY: Provides executive visibility into brand consistency and health.
        HOW: Aggregates sentiment data, compliance metrics, crisis activity,
             and provides strategic recommendations for CMO.

        Args:
            task: Task with report_type, timeframe, include_sentiment,
                  include_compliance, include_crisis

        Returns:
            dict with report_id, executive_summary, brand_metrics,
            recommendations, key_highlights
        """
        try:
            report_id = f"brand_health_{uuid.uuid4().hex[:8]}"
            report_type = task.parameters.get("report_type", "quarterly")
            include_sentiment = task.parameters.get("include_sentiment", True)
            include_compliance = task.parameters.get("include_compliance", True)
            include_crisis = task.parameters.get("include_crisis", True)

            # Brand metrics
            brand_metrics = {}

            if include_sentiment:
                brand_metrics["sentiment"] = {
                    "overall": self._sentiment_tracking["overall"],
                    "by_channel": self._sentiment_tracking,
                    "trend": "improving",
                }

            if include_compliance:
                recent_audits = (
                    self._compliance_reports[-3:] if self._compliance_reports else []
                )
                avg_compliance = (
                    sum(r["compliance_rate"] for r in recent_audits)
                    / len(recent_audits)
                    if recent_audits
                    else 95.0
                )
                brand_metrics["compliance"] = {
                    "average_compliance_rate": round(avg_compliance, 1),
                    "recent_audits": len(recent_audits),
                    "violations_trend": "decreasing",
                }

            if include_crisis:
                brand_metrics["crisis_management"] = {
                    "active_crises": len(self._crisis_protocols["active_crises"]),
                    "resolved_crises": len(self._crisis_protocols["crisis_history"]),
                    "average_response_time": "45 minutes",
                }

            # Executive summary
            executive_summary = f"""Brand health report for {report_type} period.

Overall brand sentiment: {brand_metrics.get('sentiment', {}).get('overall', 0.76):.0%}
Compliance rate: {brand_metrics.get('compliance', {}).get('average_compliance_rate', 95)}%
Active crises: {brand_metrics.get('crisis_management', {}).get('active_crises', 0)}

The brand demonstrates strong consistency and positive sentiment across channels.
Compliance remains high with minor violations addressed through training."""

            # Key highlights
            key_highlights = [
                "Brand sentiment trending positive across all channels",
                "95%+ compliance rate with brand guidelines maintained",
                "Zero critical crises in reporting period",
                "Messaging coordination improved cross-campaign consistency",
            ]

            # Strategic recommendations
            recommendations = [
                {
                    "priority": "high",
                    "area": "brand_voice",
                    "recommendation": "Expand brand voice training to new specialist agents",
                },
                {
                    "priority": "medium",
                    "area": "sentiment",
                    "recommendation": "Focus on improving Twitter sentiment through engagement",
                },
                {
                    "priority": "low",
                    "area": "compliance",
                    "recommendation": "Update prohibited terms list quarterly",
                },
            ]

            return {
                "report_id": report_id,
                "report_type": report_type,
                "executive_summary": executive_summary,
                "brand_metrics": brand_metrics,
                "key_highlights": key_highlights,
                "recommendations": recommendations,
                "report_period": task.parameters.get("timeframe", {}),
                "generated_by": self.agent_id,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise AgentExecutionError(
                message="Failed to generate brand health report",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            ) from e

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _generate_recommendations(self, score: int, violations: list[str]) -> list[str]:
        """Generate content recommendations based on score and violations."""
        recommendations = []

        if score < 70:
            recommendations.append(
                "Significant revision needed for brand voice alignment"
            )
        elif score < 85:
            recommendations.append(
                "Minor adjustments recommended for optimal brand voice"
            )

        if violations:
            recommendations.append(f"Remove {len(violations)} prohibited term(s)")

        if not recommendations:
            recommendations.append("Content meets brand voice standards")

        return recommendations

    def _generate_holding_statement(self, crisis_type: str, description: str) -> str:
        """Generate crisis holding statement."""
        return f"""We are aware of {description} and are actively investigating the situation.
The security and trust of our customers is our top priority.
We will provide updates as more information becomes available.
For immediate concerns, please contact support@company.com."""

    def _create_communication_schedule(self, severity: str) -> list[dict[str, Any]]:
        """Create crisis communication schedule based on severity."""
        if severity == "critical":
            return [
                {
                    "timing": "immediate",
                    "audience": "all_stakeholders",
                    "channel": "all",
                },
                {"timing": "+30min", "audience": "customers", "channel": "email"},
                {"timing": "+1hour", "audience": "media", "channel": "press_release"},
            ]
        elif severity == "high":
            return [
                {
                    "timing": "+1hour",
                    "audience": "affected_customers",
                    "channel": "email",
                },
                {
                    "timing": "+4hours",
                    "audience": "all_customers",
                    "channel": "website",
                },
            ]
        else:
            return [
                {
                    "timing": "+24hours",
                    "audience": "affected_customers",
                    "channel": "email",
                }
            ]

    def _generate_pr_recommendations(
        self, brand_score: int, pr_score: int, risk_factors: list[str]
    ) -> list[str]:
        """Generate PR material recommendations."""
        recommendations = []

        if brand_score < 80:
            recommendations.append("Strengthen brand voice alignment")

        if pr_score < 80:
            recommendations.append("Enhance PR standards compliance")

        if risk_factors:
            recommendations.append(
                "Address identified risk factors before distribution"
            )

        if not recommendations:
            recommendations.append("PR material meets all standards")

        return recommendations

    def _generate_sentiment_recommendations(
        self, overall: float, by_channel: dict[str, float], alerts: list[dict[str, Any]]
    ) -> list[str]:
        """Generate sentiment monitoring recommendations."""
        recommendations = []

        if overall < 0.70:
            recommendations.append(
                "Overall sentiment below target - investigate root causes"
            )

        for channel, sentiment in by_channel.items():
            if sentiment < 0.65:
                recommendations.append(
                    f"Urgent: Address declining sentiment on {channel}"
                )

        if alerts:
            recommendations.append(
                f"{len(alerts)} alert(s) require immediate attention"
            )

        if not recommendations:
            recommendations.append("Brand sentiment healthy across all channels")

        return recommendations
