"""
Example Agent Implementation Following All Development Standards.

WHY: Demonstrates proper implementation of an AI agent following TDD, SOLID,
     and all coding standards from DEVELOPMENT_STANDARDS.md.

HOW: Copy this template and modify for your specific agent type.

This file demonstrates:
- Type hints everywhere
- SOLID principles (SRP, OCP, LSP, ISP, DIP)
- No nested for loops (use comprehensions)
- No nested ifs (use guard clauses)
- Explicit comments (WHAT, WHY, HOW)
- Pythonic code style
- Dependency injection
- Strategy pattern for extensibility
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Protocol
from itertools import product


# ============================================================================
# PROTOCOLS (Interface Segregation Principle)
# ============================================================================

class LLMProvider(Protocol):
    """
    Protocol for LLM providers.

    WHY: Defines interface for LLM providers without coupling to specific implementation.
    HOW: Any class implementing generate() method satisfies this protocol.
    """

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        ...


class MessageBusProtocol(Protocol):
    """
    Protocol for message bus implementations.

    WHY: Allows different message bus backends (Redis, RabbitMQ, etc.).
    """

    async def publish(self, queue: str, message: Dict[str, Any]) -> None:
        """Publish message to queue."""
        ...

    async def subscribe(self, queue: str) -> Dict[str, Any]:
        """Subscribe to queue and receive next message."""
        ...


class DatabaseProtocol(Protocol):
    """
    Protocol for database implementations.

    WHY: Allows different database backends (PostgreSQL, MongoDB, etc.).
    """

    async def save(self, table: str, data: Dict[str, Any]) -> int:
        """Save data and return ID."""
        ...

    async def get(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """Get data by ID."""
        ...


# ============================================================================
# ENUMS (for type-safe constants)
# ============================================================================

class TaskStatus(Enum):
    """
    Task status values.

    WHY: Type-safe enumeration prevents invalid status strings.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Priority(Enum):
    """Task priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# ============================================================================
# DATA CLASSES (immutable data structures)
# ============================================================================

@dataclass(frozen=True)
class Task:
    """
    Represents a marketing task.

    WHY: Immutable data structure for task information.
    HOW: Use frozen=True for immutability.
    """

    id: int
    type: str
    description: str
    priority: Priority
    status: TaskStatus
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate task after initialization.

        WHY: Ensure data integrity at construction time.
        """
        if not self.description:
            raise ValueError("Task description cannot be empty")

        if len(self.description) < 10:
            raise ValueError("Task description must be at least 10 characters")


@dataclass
class TaskResult:
    """
    Result of task execution.

    WHY: Structured result type for clarity and type safety.
    """

    task_id: int
    status: TaskStatus
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def is_success(self) -> bool:
        """Check if task succeeded."""
        return self.status == TaskStatus.COMPLETED


# ============================================================================
# STRATEGY PATTERN (Open/Closed Principle)
# ============================================================================

class TaskValidator(ABC):
    """
    Abstract base class for task validation strategies.

    WHY: Allows different validation rules without modifying existing code.
    HOW: Implement different validators for different task types.
    """

    @abstractmethod
    def validate(self, task: Task) -> List[str]:
        """
        Validate task and return list of errors.

        Returns empty list if valid.
        """


class ContentTaskValidator(TaskValidator):
    """
    Validates content creation tasks.

    WHY: Content tasks have specific requirements (topic, word count, etc.).
    """

    REQUIRED_FIELDS = ["topic", "content_type", "target_audience"]

    def validate(self, task: Task) -> List[str]:
        """
        Validate content task has required fields.

        WHY: Prevent invalid tasks from being processed.
        HOW: Use list comprehension to collect missing fields.
        """
        # PYTHONIC: Use list comprehension instead of for loop
        missing_fields = [
            field
            for field in self.REQUIRED_FIELDS
            if field not in task.metadata
        ]

        return [
            f"Missing required field: {field}"
            for field in missing_fields
        ] if missing_fields else []


class CampaignTaskValidator(TaskValidator):
    """Validates campaign tasks."""

    def validate(self, task: Task) -> List[str]:
        """Validate campaign task requirements."""
        errors = []

        if "budget" not in task.metadata:
            errors.append("Campaign requires budget")

        if "duration_days" not in task.metadata:
            errors.append("Campaign requires duration")

        return errors


# ============================================================================
# FACTORY PATTERN (for creating validators)
# ============================================================================

class ValidatorFactory:
    """
    Factory for creating task validators.

    WHY: Centralizes validator creation logic.
    HOW: Maps task types to validator classes.
    """

    _validators: Dict[str, type[TaskValidator]] = {
        "content": ContentTaskValidator,
        "campaign": CampaignTaskValidator,
    }

    @classmethod
    def create(cls, task_type: str) -> TaskValidator:
        """
        Create validator for task type.

        WHY: Decouples task type from validator instantiation.
        """
        validator_class = cls._validators.get(task_type)

        if validator_class is None:
            raise ValueError(f"Unknown task type: {task_type}")

        return validator_class()


# ============================================================================
# MAIN AGENT CLASS (demonstrating all principles)
# ============================================================================

class ContentAgent:
    """
    Content creation agent.

    WHY: Autonomous agent for creating marketing content.
    HOW: Uses LLM, message bus, and database via dependency injection.

    PRINCIPLES DEMONSTRATED:
    - Single Responsibility: Only handles content creation
    - Open/Closed: Extensible via strategies, closed for modification
    - Liskov Substitution: Can swap LLM/database implementations
    - Interface Segregation: Depends only on minimal protocols
    - Dependency Inversion: Depends on abstractions (protocols), not concrete classes
    """

    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30

    def __init__(
        self,
        llm: LLMProvider,
        database: DatabaseProtocol,
        message_bus: MessageBusProtocol,
        validator_factory: Optional[ValidatorFactory] = None,
    ) -> None:
        """
        Initialize agent with dependencies.

        WHY: Dependency injection for testability and flexibility.
        HOW: All dependencies passed as arguments (not created internally).

        Args:
            llm: LLM provider for content generation
            database: Database for persistence
            message_bus: Message bus for agent communication
            validator_factory: Factory for task validators
        """
        self.llm = llm
        self.database = database
        self.message_bus = message_bus
        self.validator_factory = validator_factory or ValidatorFactory()

    async def process_task(self, task: Task) -> TaskResult:
        """
        Process a content creation task.

        WHY: Main entry point for task execution.
        HOW: Uses guard clauses for validation, then executes task.

        DEMONSTRATES: Guard clauses instead of nested ifs.
        """
        start_time = datetime.now()

        # GUARD CLAUSES (no nested ifs)
        validation_errors = self._validate_task(task)
        if validation_errors:
            return self._create_error_result(
                task.id,
                f"Validation failed: {', '.join(validation_errors)}",
                start_time
            )

        if task.status != TaskStatus.PENDING:
            return self._create_error_result(
                task.id,
                f"Cannot process task with status: {task.status.value}",
                start_time
            )

        # All validations passed - execute task
        try:
            output = await self._execute_task_with_retry(task)
            await self._save_result(task.id, output)
            await self._notify_completion(task.id)

            return TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                output=output,
                execution_time_ms=self._elapsed_ms(start_time),
            )

        except Exception as error:
            return self._create_error_result(
                task.id,
                str(error),
                start_time
            )

    def _validate_task(self, task: Task) -> List[str]:
        """
        Validate task using appropriate validator.

        WHY: Centralized validation logic.
        HOW: Uses factory to get correct validator.
        """
        try:
            validator = self.validator_factory.create(task.type)
            return validator.validate(task)
        except ValueError:
            return [f"Unknown task type: {task.type}"]

    async def _execute_task_with_retry(self, task: Task) -> str:
        """
        Execute task with retry logic.

        WHY: Handle transient failures (network issues, API rate limits).
        HOW: Retry up to MAX_RETRIES times with exponential backoff.

        DEMONSTRATES: No nested for loops - use simple for with continue.
        """
        last_error: Optional[Exception] = None

        # PYTHONIC: Use range() directly, not nested loops
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return await self._execute_task(task)

            except Exception as error:
                last_error = error

                # Don't retry on last attempt
                if attempt == self.MAX_RETRIES:
                    break

                # Wait before retry (exponential backoff)
                await self._wait_before_retry(attempt)

        # All retries failed
        raise RuntimeError(
            f"Task failed after {self.MAX_RETRIES} attempts: {last_error}"
        )

    async def _execute_task(self, task: Task) -> str:
        """
        Execute the actual task.

        WHY: Core task execution logic.
        HOW: Uses LLM to generate content based on task metadata.
        """
        prompt = self._build_prompt(task)
        content = self.llm.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )

        return content

    def _build_prompt(self, task: Task) -> str:
        """
        Build LLM prompt from task.

        WHY: Converts task metadata into effective LLM prompt.
        HOW: Uses f-string formatting (Pythonic).

        DEMONSTRATES: Pythonic string formatting.
        """
        metadata = task.metadata

        # PYTHONIC: Use f-strings, not format() or %
        prompt = f"""Create marketing content with the following requirements:

Type: {metadata.get('content_type', 'article')}
Topic: {metadata.get('topic', 'general')}
Target Audience: {metadata.get('target_audience', 'general')}
Tone: {metadata.get('tone', 'professional')}
Word Count: {metadata.get('word_count', 500)}

Additional Context:
{metadata.get('context', 'None provided')}
"""

        return prompt

    async def _save_result(self, task_id: int, output: str) -> None:
        """
        Save task result to database.

        WHY: Persist results for later retrieval.
        """
        await self.database.save(
            table="task_results",
            data={
                "task_id": task_id,
                "output": output,
                "created_at": datetime.now().isoformat(),
            }
        )

    async def _notify_completion(self, task_id: int) -> None:
        """
        Notify other agents of task completion.

        WHY: Enable agent collaboration via message bus.
        """
        await self.message_bus.publish(
            queue="task_completions",
            message={
                "task_id": task_id,
                "agent": "content_agent",
                "timestamp": datetime.now().isoformat(),
            }
        )

    def _create_error_result(
        self,
        task_id: int,
        error_message: str,
        start_time: datetime
    ) -> TaskResult:
        """
        Create error result for failed task.

        WHY: Consistent error result creation.
        """
        return TaskResult(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error=error_message,
            execution_time_ms=self._elapsed_ms(start_time),
        )

    @staticmethod
    def _elapsed_ms(start_time: datetime) -> float:
        """Calculate elapsed milliseconds since start time."""
        return (datetime.now() - start_time).total_seconds() * 1000

    @staticmethod
    async def _wait_before_retry(attempt: int) -> None:
        """
        Wait before retry with exponential backoff.

        WHY: Avoid overwhelming failed services.
        """
        import asyncio

        wait_time = 2 ** attempt  # Exponential backoff
        await asyncio.sleep(wait_time)


# ============================================================================
# UTILITY FUNCTIONS (demonstrating Pythonic code)
# ============================================================================

def filter_tasks_by_priority(
    tasks: List[Task],
    min_priority: Priority
) -> List[Task]:
    """
    Filter tasks by minimum priority.

    WHY: Common operation to find high-priority tasks.
    HOW: Use filter() or list comprehension (Pythonic).

    DEMONSTRATES: No for loops - use list comprehension.
    """
    # PYTHONIC: List comprehension instead of for loop
    return [
        task
        for task in tasks
        if task.priority.value >= min_priority.value
    ]


def group_tasks_by_type(tasks: List[Task]) -> Dict[str, List[Task]]:
    """
    Group tasks by type.

    WHY: Organize tasks for batch processing.
    HOW: Use dict comprehension with set of types.

    DEMONSTRATES: No nested for loops - use comprehensions.
    """
    # Get unique task types
    task_types = {task.type for task in tasks}

    # PYTHONIC: Dict comprehension instead of nested for loops
    return {
        task_type: [task for task in tasks if task.type == task_type]
        for task_type in task_types
    }


def find_task_pairs(
    tasks1: List[Task],
    tasks2: List[Task],
    match_type: bool = True
) -> List[tuple[Task, Task]]:
    """
    Find all pairs of tasks from two lists.

    WHY: Find related tasks for batch operations.
    HOW: Use itertools.product() instead of nested for loops.

    DEMONSTRATES: No nested for loops - use itertools.
    """
    # PYTHONIC: Use itertools.product instead of nested for loops
    if match_type:
        return [
            (t1, t2)
            for t1, t2 in product(tasks1, tasks2)
            if t1.type == t2.type
        ]

    return list(product(tasks1, tasks2))


def calculate_task_stats(tasks: List[Task]) -> Dict[str, Any]:
    """
    Calculate statistics about tasks.

    WHY: Provide insights into task distribution.
    HOW: Use Pythonic aggregation patterns.

    DEMONSTRATES: map(), sum(), len() instead of for loops.
    """
    if not tasks:
        return {"total": 0, "by_status": {}, "by_priority": {}}

    # PYTHONIC: Use sum() with generator expression
    total_tasks = len(tasks)

    # PYTHONIC: Use Counter from collections
    from collections import Counter

    status_counts = Counter(task.status.value for task in tasks)
    priority_counts = Counter(task.priority.value for task in tasks)

    return {
        "total": total_tasks,
        "by_status": dict(status_counts),
        "by_priority": dict(priority_counts),
    }


# ============================================================================
# EXAMPLE USAGE (for documentation)
# ============================================================================

async def example_usage() -> None:
    """
    Example of how to use ContentAgent.

    WHY: Demonstrates proper initialization and usage.
    """
    # Import real implementations
    from infrastructure.claude_llm import ClaudeLLM
    from infrastructure.postgres_db import PostgresDatabase
    from infrastructure.redis_bus import RedisMessageBus

    # Initialize dependencies
    llm = ClaudeLLM(api_key="your-api-key", model="claude-sonnet")
    database = PostgresDatabase(connection_string="postgresql://localhost/db")
    message_bus = RedisMessageBus(redis_url="redis://localhost:6379")

    # Create agent with dependency injection
    agent = ContentAgent(
        llm=llm,
        database=database,
        message_bus=message_bus
    )

    # Create task
    task = Task(
        id=1,
        type="content",
        description="Create blog post about AI marketing",
        priority=Priority.HIGH,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        metadata={
            "topic": "AI Marketing ROI",
            "content_type": "blog_post",
            "target_audience": "B2B SaaS companies",
            "word_count": 1500,
        }
    )

    # Process task
    result = await agent.process_task(task)

    if result.is_success():
        print(f"Task completed successfully in {result.execution_time_ms}ms")
        print(f"Output: {result.output}")
    else:
        print(f"Task failed: {result.error}")
