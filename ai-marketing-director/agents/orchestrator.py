"""Orchestrator Agent that coordinates all marketing agents"""
from openai import OpenAI
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from config.settings import settings
from core.brand_voice import brand_voice


class TaskType(str, Enum):
    """Types of marketing tasks"""

    MARKET_RESEARCH = "market_research"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    CONTENT_CREATION = "content_creation"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    ANALYTICS_REVIEW = "analytics_review"
    STRATEGY_RECOMMENDATION = "strategy_recommendation"


class TaskPriority(str, Enum):
    """Task priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OrchestratorAgent:
    """
    Orchestrator Agent that:
    - Receives high-level marketing objectives
    - Breaks them down into specific tasks
    - Routes tasks to appropriate specialized agents
    - Manages task dependencies and workflow
    - Consolidates results and provides summaries
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = settings.default_model
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []

    def plan_marketing_initiative(self, objective: str, timeframe: str = "1 month") -> Dict:
        """
        Plan a marketing initiative by breaking it down into specific tasks

        Args:
            objective: High-level marketing objective
            timeframe: Time window for execution

        Returns:
            Dict containing planned tasks, timeline, and dependencies
        """
        system_prompt = f"""You are the Orchestrator Agent for AI Elevate's marketing automation system.

Your role is to:
1. Analyze high-level marketing objectives
2. Break them into specific, actionable tasks
3. Assign tasks to appropriate agents (Strategy, Content, Social Media, Campaign, Analytics)
4. Define task dependencies and timeline
5. Prioritize tasks

Available agents and their capabilities:
- **Strategy Agent**: Market research, competitor analysis, trend identification, topic suggestions
- **Content Agent**: Blog posts, case studies, whitepapers, thought leadership articles
- **Social Media Agent**: LinkedIn/Twitter posts, engagement, scheduling
- **Campaign Agent**: Email sequences, audience segmentation, nurture campaigns
- **Analytics Agent**: Performance tracking, insights, optimization recommendations

AI Elevate's context:
- Enterprise AI training company
- 5000+ professionals trained
- Target: Fortune 500 companies and enterprises
- Focus: Prompt engineering, LLM training, AI implementation"""

        user_prompt = f"""Marketing Objective: {objective}
Timeframe: {timeframe}

Create a detailed execution plan with:
1. **Overall Strategy**: High-level approach to achieve the objective
2. **Task Breakdown**: Specific tasks with assigned agent, priority, and estimated time
3. **Timeline**: Week-by-week schedule
4. **Dependencies**: Which tasks must complete before others can start
5. **Success Metrics**: How to measure if objective is achieved
6. **Resource Requirements**: API calls, budget considerations, human review points

Format as structured JSON."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            # GPT-5 only supports default temperature=1
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        plan = {
            "objective": objective,
            "timeframe": timeframe,
            "plan": response.choices[0].message.content,
            "created_at": datetime.now().isoformat(),
            "agent": "orchestrator",
        }

        return plan

    def create_task(
        self,
        task_type: TaskType,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_agent: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> Dict:
        """
        Create a new task and add to queue

        Args:
            task_type: Type of marketing task
            description: Detailed task description
            priority: Task priority level
            assigned_agent: Which agent should handle this
            context: Additional context for the task

        Returns:
            Dict containing task details
        """
        task = {
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": task_type.value,
            "description": description,
            "priority": priority.value,
            "assigned_agent": assigned_agent or self._determine_agent(task_type),
            "context": context or {},
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
        }

        self.task_queue.append(task)
        return task

    def _determine_agent(self, task_type: TaskType) -> str:
        """Determine which agent should handle a given task type"""
        agent_mapping = {
            TaskType.MARKET_RESEARCH: "strategy_agent",
            TaskType.COMPETITOR_ANALYSIS: "strategy_agent",
            TaskType.STRATEGY_RECOMMENDATION: "strategy_agent",
            TaskType.CONTENT_CREATION: "content_agent",
            TaskType.SOCIAL_MEDIA: "social_agent",
            TaskType.EMAIL_CAMPAIGN: "campaign_agent",
            TaskType.ANALYTICS_REVIEW: "analytics_agent",
        }
        return agent_mapping.get(task_type, "strategy_agent")

    def get_next_task(self) -> Optional[Dict]:
        """Get the next highest priority task from queue"""
        if not self.task_queue:
            return None

        # Sort by priority (urgent > high > medium > low)
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        self.task_queue.sort(key=lambda t: priority_order.get(t["priority"], 4))

        return self.task_queue[0] if self.task_queue else None

    def mark_task_complete(self, task_id: str, result: Any) -> None:
        """Mark a task as completed and move to completed_tasks"""
        for i, task in enumerate(self.task_queue):
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                task["result"] = result
                self.completed_tasks.append(task)
                self.task_queue.pop(i)
                break

    def get_status_summary(self) -> Dict:
        """Get summary of all tasks and their status"""
        return {
            "queued_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "queue": self.task_queue,
            "recent_completions": self.completed_tasks[-5:],  # Last 5 completed
            "timestamp": datetime.now().isoformat(),
        }

    def suggest_next_actions(self, current_context: str) -> Dict:
        """
        Based on current context, suggest next marketing actions

        Args:
            current_context: Description of current marketing situation

        Returns:
            Dict containing suggested actions with rationale
        """
        system_prompt = """You are the Orchestrator Agent analyzing the current marketing situation
and suggesting the most impactful next actions for AI Elevate.

Consider:
- Current market trends
- AI Elevate's strengths and positioning
- Available resources and channels
- ROI potential of different actions"""

        user_prompt = f"""Current Context:
{current_context}

Based on this, suggest the top 3-5 most impactful marketing actions AI Elevate should take next.

For each action provide:
1. **Action**: What to do
2. **Rationale**: Why this action matters now
3. **Expected Impact**: What outcomes to expect
4. **Agent(s) Required**: Which agents would execute this
5. **Effort Level**: Low/Medium/High
6. **Priority**: Urgent/High/Medium/Low

Format as JSON array, ordered by priority."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            # GPT-5 only supports default temperature=1
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        return {
            "context": current_context,
            "suggestions": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat(),
            "agent": "orchestrator",
        }


# CLI interface for testing
if __name__ == "__main__":
    import json

    orchestrator = OrchestratorAgent()

    print("🎬 AI Elevate Orchestrator Agent")
    print("=" * 50)

    # Example: Plan a marketing initiative
    objective = "Increase LinkedIn engagement and generate 50 qualified leads for Q1 2025"
    print(f"\n📋 Planning initiative: {objective}")

    plan = orchestrator.plan_marketing_initiative(objective, timeframe="3 months")
    print(json.dumps(plan, indent=2))

    # Example: Create some tasks
    print("\n✅ Creating tasks...")
    orchestrator.create_task(
        TaskType.MARKET_RESEARCH, "Analyze Q1 2025 enterprise AI training trends", TaskPriority.HIGH
    )
    orchestrator.create_task(
        TaskType.CONTENT_CREATION,
        "Write blog post: 'Why 80% of AI Implementations Fail'",
        TaskPriority.MEDIUM,
    )
    orchestrator.create_task(
        TaskType.SOCIAL_MEDIA, "Create 5 LinkedIn posts about prompt engineering ROI", TaskPriority.HIGH
    )

    # Show status
    print("\n📊 Status Summary:")
    print(json.dumps(orchestrator.get_status_summary(), indent=2))
