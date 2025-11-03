# Development Standards & Coding Guidelines

**Project**: AI Marketing Director
**Version**: 2.2
**Status**: Mandatory for all code generation
**Last Updated**: 2025-11-03 (Added Exception Wrapping Requirement)

---

## 📋 Table of Contents

1. [Core Principles](#core-principles)
2. [Test-Driven Development (TDD)](#test-driven-development-tdd)
3. [Testing Requirements](#testing-requirements)
4. [Code Style & Standards](#code-style--standards)
5. [Design Patterns & SOLID](#design-patterns--solid)
6. [Anti-Patterns (FORBIDDEN)](#anti-patterns-forbidden)
7. [Code Examples](#code-examples)
8. [Test Templates](#test-templates)
9. [Adherence to Specifications](#adherence-to-specifications)
10. [Code Review Checklist](#code-review-checklist)

---

## Core Principles

### 1. Test-Driven Development (TDD)

**MANDATORY**: All code MUST be written using TDD methodology.

**TDD Cycle** (Red-Green-Refactor):
```
1. RED: Write a failing test first
2. GREEN: Write minimal code to make test pass
3. REFACTOR: Improve code while keeping tests green
4. REPEAT
```

**No exceptions**: Code without tests will NOT be accepted.

### 2. Pythonic Code

All code must follow Python idioms and best practices:
- Use list/dict/set comprehensions over loops
- Use `map()` and `filter()` for transformations
- Use context managers (`with` statements)
- Use f-strings for string formatting
- Use `pathlib` for file paths
- Use type hints everywhere

### 3. SOLID Principles

Every class and function must adhere to:
- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

### 4. Functional Design Patterns

**MANDATORY**: Always use functional programming patterns where applicable.

**Core Functional Principles**:
- **Pure Functions**: Functions should have no side effects
- **Immutability**: Prefer immutable data structures
- **Higher-Order Functions**: Use functions as first-class citizens
- **Function Composition**: Build complex operations from simple functions
- **Declarative over Imperative**: Focus on WHAT, not HOW

**Benefits**:
- Easier to test (pure functions are deterministic)
- Easier to reason about (no hidden state)
- Better for concurrent/parallel execution
- More maintainable and composable

### 5. Explicit Documentation

**All code must have comments explaining**:
- **WHAT** the code does
- **WHY** it does it (business logic, design decision)
- **HOW** it works (for complex algorithms)

---

## Test-Driven Development (TDD)

### TDD Workflow

**Step 1: Write Test First**
```python
# test_agent.py
def test_cmo_agent_sets_marketing_strategy():
    """
    Test that CMO agent can create and set marketing strategy.

    WHY: CMO is responsible for overall strategy direction.
    Ensures agent can process strategic inputs and create actionable plans.
    """
    # GIVEN: A CMO agent with access to market data
    cmo = CMOAgent(market_data=sample_market_data)

    # WHEN: Setting a marketing strategy for Q4
    strategy = cmo.set_strategy(
        objective="Increase enterprise leads by 50%",
        timeframe="Q4 2025"
    )

    # THEN: Strategy should be created with specific tactics
    assert strategy is not None
    assert strategy.objective == "Increase enterprise leads by 50%"
    assert len(strategy.tactics) > 0
    assert strategy.budget_allocation is not None
```

**Step 2: Run Test (Should Fail)**
```bash
pytest test_agent.py::test_cmo_agent_sets_marketing_strategy
# Expected: FAILED (CMOAgent not implemented)
```

**Step 3: Write Minimal Code**
```python
# agent.py
class CMOAgent:
    """
    CMO (Chief Marketing Officer) Agent.

    WHY: Provides strategic leadership for the marketing department.
    Acts as the highest-level decision maker in the agent hierarchy.

    Responsibilities:
    - Set overall marketing strategy
    - Allocate budget across channels
    - Monitor high-level performance metrics
    """

    def __init__(self, market_data: Dict[str, Any]):
        """
        Initialize CMO agent with market context.

        WHY: CMO needs market data to make informed strategic decisions.

        Args:
            market_data: Historical performance and market intelligence
        """
        self.market_data = market_data
        self.llm = self._initialize_llm()  # Claude Opus for strategic thinking

    def set_strategy(
        self,
        objective: str,
        timeframe: str
    ) -> MarketingStrategy:
        """
        Create marketing strategy based on objective.

        WHY: CMO's primary responsibility is setting strategic direction.
        Uses market data and LLM to generate data-driven strategy.

        Args:
            objective: Strategic goal (e.g., "Increase leads by 50%")
            timeframe: Time period (e.g., "Q4 2025")

        Returns:
            MarketingStrategy with tactics and budget allocation
        """
        # Use LLM to analyze market data and create strategy
        # (Minimal implementation to pass test)
        prompt = self._build_strategy_prompt(objective, timeframe)
        llm_response = self.llm.generate(prompt)
        strategy = self._parse_strategy_response(llm_response)

        return strategy
```

**Step 4: Run Test (Should Pass)**
```bash
pytest test_agent.py::test_cmo_agent_sets_marketing_strategy
# Expected: PASSED
```

**Step 5: Refactor**
```python
# Refactor: Extract methods, improve readability, add type hints
class CMOAgent:
    """CMO Agent - Strategic leadership for marketing department."""

    def __init__(self, market_data: MarketData):  # Better type hint
        self.market_data = market_data
        self.llm = self._initialize_llm()
        self._validator = StrategyValidator()  # Added validation

    def set_strategy(
        self,
        objective: str,
        timeframe: str
    ) -> MarketingStrategy:
        """Create data-driven marketing strategy."""
        # WHAT: Generate strategy using LLM and market data
        # WHY: CMO uses AI + data to create optimal strategy
        # HOW: Prompt engineering + validation + parsing

        prompt = self._build_strategy_prompt(objective, timeframe)
        llm_response = self._generate_with_retry(prompt)  # Added retry logic
        strategy = self._parse_strategy_response(llm_response)

        # Validate before returning (defensive programming)
        self._validator.validate(strategy)

        return strategy

    def _build_strategy_prompt(self, objective: str, timeframe: str) -> str:
        """
        Build LLM prompt for strategy generation.

        WHY: Separates prompt engineering from main logic (SRP).
        """
        # ... implementation

    def _generate_with_retry(self, prompt: str) -> str:
        """
        Generate LLM response with retry logic.

        WHY: LLM APIs can fail; retry ensures reliability.
        """
        # ... implementation
```

---

## Testing Requirements

### Required Test Types

Every feature MUST have all of the following test types:

#### 1. Unit Tests
**Purpose**: Test individual functions/methods in isolation

**Requirements**:
- Mock all external dependencies
- Test edge cases and error conditions
- Test happy path and sad path
- Achieve 90%+ code coverage

**Example**:
```python
# tests/unit/test_cmo_agent.py
import pytest
from unittest.mock import Mock, patch
from agents.cmo_agent import CMOAgent

class TestCMOAgent:
    """
    Unit tests for CMO Agent.

    WHY: Ensures CMO agent logic works correctly in isolation.
    """

    @pytest.fixture
    def cmo_agent(self):
        """
        Fixture providing CMO agent with mocked dependencies.

        WHY: Avoids real LLM API calls in unit tests (fast, deterministic).
        """
        market_data = Mock()
        agent = CMOAgent(market_data=market_data)
        agent.llm = Mock()  # Mock LLM to avoid API calls
        return agent

    def test_set_strategy_with_valid_objective(self, cmo_agent):
        """Test strategy creation with valid inputs."""
        # GIVEN: Mock LLM returns valid strategy
        cmo_agent.llm.generate.return_value = """
        {
            "objective": "Increase leads 50%",
            "tactics": ["LinkedIn ads", "Content marketing"],
            "budget": {"linkedin": 5000, "content": 3000}
        }
        """

        # WHEN: Setting strategy
        strategy = cmo_agent.set_strategy("Increase leads 50%", "Q4")

        # THEN: Strategy is created correctly
        assert strategy.objective == "Increase leads 50%"
        assert len(strategy.tactics) == 2
        assert strategy.budget["linkedin"] == 5000

    def test_set_strategy_handles_llm_failure(self, cmo_agent):
        """
        Test that agent handles LLM API failures gracefully.

        WHY: LLM APIs can fail; agent must not crash.
        """
        # GIVEN: LLM raises exception
        cmo_agent.llm.generate.side_effect = Exception("API timeout")

        # WHEN/THEN: Should raise specific exception
        with pytest.raises(StrategyGenerationError):
            cmo_agent.set_strategy("Increase leads", "Q4")

    def test_set_strategy_validates_output(self, cmo_agent):
        """
        Test that invalid LLM output is rejected.

        WHY: LLMs can hallucinate; must validate all outputs.
        """
        # GIVEN: LLM returns invalid strategy (missing budget)
        cmo_agent.llm.generate.return_value = """
        {
            "objective": "Increase leads",
            "tactics": ["LinkedIn"]
        }
        """

        # WHEN/THEN: Should raise validation error
        with pytest.raises(ValidationError):
            cmo_agent.set_strategy("Increase leads", "Q4")
```

#### 2. Integration Tests
**Purpose**: Test interaction between components

**Requirements**:
- Test real integrations (database, message bus, external APIs)
- Use test databases/services (not production)
- Clean up after each test
- Test failure scenarios

**Example**:
```python
# tests/integration/test_agent_collaboration.py
import pytest
from agents.cmo_agent import CMOAgent
from agents.vp_marketing_agent import VPMarketingAgent
from messaging.message_bus import MessageBus

@pytest.fixture
def message_bus():
    """
    Integration test fixture for message bus.

    WHY: Tests need real message bus for integration testing.
    Uses test Redis instance (not production).
    """
    bus = MessageBus(redis_url="redis://localhost:6379/1")  # Test DB
    yield bus
    bus.clear()  # Cleanup after test

@pytest.mark.integration
class TestAgentCollaboration:
    """
    Integration tests for agent-to-agent collaboration.

    WHY: Ensures agents can communicate and collaborate correctly.
    """

    async def test_cmo_delegates_to_vp_marketing(self, message_bus):
        """
        Test that CMO can delegate strategy execution to VP Marketing.

        WHY: Core collaboration pattern in the system.
        """
        # GIVEN: CMO and VP Marketing agents on same message bus
        cmo = CMOAgent(message_bus=message_bus)
        vp = VPMarketingAgent(message_bus=message_bus)

        # Start VP listening for messages
        await vp.start_listening()

        # WHEN: CMO delegates strategy execution
        strategy = await cmo.set_strategy("Increase leads 50%", "Q4")
        await cmo.delegate_to_vp(strategy)

        # Wait for VP to process message
        await asyncio.sleep(0.5)

        # THEN: VP should receive and acknowledge strategy
        messages = await message_bus.get_messages("vp_marketing")
        assert len(messages) == 1
        assert messages[0]["type"] == "strategy_delegation"
        assert messages[0]["from"] == "cmo"
```

#### 3. End-to-End (E2E) Tests
**Purpose**: Test complete user workflows

**Requirements**:
- Test realistic user scenarios
- Use production-like environment
- Test across all system layers
- Verify business outcomes

**Example**:
```python
# tests/e2e/test_blog_post_workflow.py
import pytest
from tests.e2e.helpers import SystemTestHarness

@pytest.mark.e2e
class TestBlogPostWorkflow:
    """
    E2E tests for complete blog post creation workflow.

    WHY: Validates entire system works together for real use cases.
    """

    @pytest.fixture
    async def system(self):
        """
        E2E test harness with all agents running.

        WHY: E2E tests need fully operational system.
        """
        harness = SystemTestHarness()
        await harness.start_all_agents()
        yield harness
        await harness.stop_all_agents()
        await harness.cleanup()

    async def test_complete_blog_post_creation(self, system):
        """
        Test complete workflow from strategy to published blog post.

        WHY: Core business workflow that must work end-to-end.
        """
        # GIVEN: System is running with all 14 agents
        assert await system.verify_all_agents_healthy()

        # WHEN: User requests blog post creation
        request = {
            "type": "create_blog_post",
            "topic": "Why 80% of AI Projects Fail",
            "target_audience": "enterprise_ctos",
            "keywords": ["AI implementation", "AI ROI"]
        }

        task_id = await system.submit_task(request)

        # Wait for workflow to complete (with timeout)
        result = await system.wait_for_completion(
            task_id,
            timeout=60  # 60 seconds max
        )

        # THEN: Blog post should be created, reviewed, approved, and published
        assert result.status == "published"
        assert result.blog_post is not None
        assert result.blog_post.title is not None
        assert result.blog_post.seo_score > 80
        assert result.blog_post.brand_voice_score > 85

        # Verify agent collaboration happened
        collaboration_log = await system.get_collaboration_log(task_id)
        assert "content_manager" in collaboration_log
        assert "copywriter" in collaboration_log
        assert "seo_specialist" in collaboration_log
        assert "vp_marketing" in collaboration_log

        # Verify blog post was actually published to CMS
        published_post = await system.cms.get_post(result.blog_post.id)
        assert published_post.status == "published"
```

#### 4. Linting Tests
**Purpose**: Enforce code quality and style

**Requirements**:
- Use `pylint`, `flake8`, `mypy`, `black`
- Must pass all linters before commit
- Configure in `pyproject.toml`

**Configuration**:
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py312']

[tool.pylint]
max-line-length = 100
disable = ["C0111"]  # Missing docstring (we enforce via custom check)

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**CI/CD Integration**:
```bash
# .github/workflows/lint.yml
- name: Run linting
  run: |
    black --check .
    pylint ai_marketing_director/
    flake8 ai_marketing_director/
    mypy ai_marketing_director/
```

#### 5. Regression Tests
**Purpose**: Ensure fixes don't reintroduce bugs

**Requirements**:
- Create regression test for every bug fix
- Tag with `@pytest.mark.regression` and bug ID
- Never delete regression tests

**Example**:
```python
# tests/regression/test_bug_fixes.py
import pytest

@pytest.mark.regression
@pytest.mark.bug_id("AIMD-142")
def test_bug_142_seo_specialist_handles_empty_keywords():
    """
    Regression test for bug AIMD-142.

    BUG: SEO Specialist crashed when given empty keyword list.
    FIX: Added validation and default keywords.

    WHY: Ensure this bug never happens again.
    """
    # GIVEN: SEO specialist with no keywords
    seo = SEOSpecialist()

    # WHEN: Optimizing content with empty keywords
    result = seo.optimize_content(
        content="Sample blog post",
        keywords=[]  # Empty list that caused crash
    )

    # THEN: Should not crash and should use default keywords
    assert result is not None
    assert len(result.keywords) > 0  # Default keywords added
    assert "optimization" in result.metadata  # Optimization ran
```

### Test Coverage Requirements

| Test Type | Coverage Target | Purpose |
|-----------|----------------|---------|
| **Unit** | 90%+ line coverage | Ensure all code paths tested |
| **Integration** | 80%+ integration points | Ensure components work together |
| **E2E** | 100% critical paths | Ensure key workflows work |
| **Regression** | 100% fixed bugs | Prevent bug reintroduction |

---

## Code Style & Standards

### 1. No Nested For Loops ❌

**FORBIDDEN**:
```python
# ❌ BAD: Nested for loops
def find_matching_agents(agents, tasks):
    matches = []
    for agent in agents:
        for task in tasks:
            if agent.can_handle(task):
                matches.append((agent, task))
    return matches
```

**REQUIRED**:
```python
# ✅ GOOD: Use comprehensions or functional approach
def find_matching_agents(agents: List[Agent], tasks: List[Task]) -> List[Tuple[Agent, Task]]:
    """
    Find agents that can handle each task.

    WHY: Matches agents to tasks based on capabilities.
    HOW: Uses list comprehension with itertools for cartesian product.
    """
    from itertools import product

    # WHAT: Generate all agent-task pairs and filter by capability
    # WHY: Comprehension is more Pythonic and often faster than nested loops
    return [
        (agent, task)
        for agent, task in product(agents, tasks)
        if agent.can_handle(task)
    ]
```

**Alternative with map/filter**:
```python
# ✅ ALSO GOOD: Using map and filter
def find_matching_agents(agents: List[Agent], tasks: List[Task]) -> List[Tuple[Agent, Task]]:
    """Find agents that can handle each task using functional approach."""
    from itertools import product

    # WHAT: Create all combinations, then filter
    # WHY: Functional approach is declarative and composable
    all_combinations = product(agents, tasks)
    can_handle = lambda pair: pair[0].can_handle(pair[1])

    return list(filter(can_handle, all_combinations))
```

### 2. No Nested Ifs ❌

**FORBIDDEN**:
```python
# ❌ BAD: Nested if statements
def approve_content(content, user):
    if user.is_authenticated:
        if user.has_permission("approve"):
            if content.status == "pending":
                if content.quality_score > 80:
                    content.approve()
                    return True
    return False
```

**REQUIRED**: Use guard clauses or strategy pattern
```python
# ✅ GOOD: Guard clauses (early returns)
def approve_content(content: Content, user: User) -> bool:
    """
    Approve content if all conditions met.

    WHY: Implements approval workflow with proper authorization.
    HOW: Uses guard clauses to validate preconditions.
    """
    # Guard clauses: fail fast on invalid conditions
    # WHY: Reduces nesting and improves readability

    if not user.is_authenticated:
        raise AuthenticationError("User must be authenticated")

    if not user.has_permission("approve"):
        raise PermissionError(f"User {user.id} lacks approval permission")

    if content.status != "pending":
        raise InvalidStateError(f"Cannot approve {content.status} content")

    if content.quality_score <= 80:
        raise QualityError(f"Quality score {content.quality_score} below threshold")

    # All validations passed
    content.approve()
    return True
```

**Alternative**: Strategy pattern for complex conditions
```python
# ✅ ALSO GOOD: Strategy pattern for complex logic
class ApprovalRule(ABC):
    """Base class for approval rules."""

    @abstractmethod
    def check(self, content: Content, user: User) -> None:
        """Check if rule passes. Raise exception if fails."""
        pass

class AuthenticationRule(ApprovalRule):
    """Ensures user is authenticated."""

    def check(self, content: Content, user: User) -> None:
        if not user.is_authenticated:
            raise AuthenticationError()

class PermissionRule(ApprovalRule):
    """Ensures user has approval permission."""

    def check(self, content: Content, user: User) -> None:
        if not user.has_permission("approve"):
            raise PermissionError()

# ... more rules

class ApprovalWorkflow:
    """
    Orchestrates content approval with pluggable rules.

    WHY: Separates approval logic into testable, reusable components.
    Follows Open/Closed Principle (can add rules without modifying workflow).
    """

    def __init__(self):
        # WHY: Rules are composable and can be configured per deployment
        self.rules = [
            AuthenticationRule(),
            PermissionRule(),
            ContentStatusRule(),
            QualityScoreRule(threshold=80),
        ]

    def approve(self, content: Content, user: User) -> bool:
        """
        Approve content by running all approval rules.

        WHY: Single method validates all rules and approves.
        HOW: Iterates rules; any failure raises exception.
        """
        # Run all rules (will raise exception if any fail)
        for rule in self.rules:
            rule.check(content, user)

        # All rules passed
        content.approve()
        return True
```

### 3. Use Comprehensions

**REQUIRED**: Always prefer comprehensions over loops

```python
# ❌ BAD: Traditional loop
approved_content = []
for content in all_content:
    if content.status == "approved":
        approved_content.append(content)

# ✅ GOOD: List comprehension
approved_content = [
    content
    for content in all_content
    if content.status == "approved"
]

# ✅ GOOD: Dict comprehension
content_by_id = {
    content.id: content
    for content in all_content
}

# ✅ GOOD: Set comprehension
unique_tags = {
    tag
    for content in all_content
    for tag in content.tags
}
```

### 4. Use map() and filter()

```python
# ❌ BAD: Loop for transformation
titles = []
for content in all_content:
    titles.append(content.title.upper())

# ✅ GOOD: map for transformation
titles = list(map(lambda c: c.title.upper(), all_content))

# ✅ BETTER: Comprehension (more Pythonic than map for simple cases)
titles = [content.title.upper() for content in all_content]

# ✅ GOOD: filter for filtering
high_quality = filter(lambda c: c.quality_score > 80, all_content)

# ✅ GOOD: Chaining map and filter
high_quality_titles = map(
    lambda c: c.title,
    filter(lambda c: c.quality_score > 80, all_content)
)

# ✅ BEST: Comprehension for complex operations
high_quality_titles = [
    content.title
    for content in all_content
    if content.quality_score > 80
]
```

### 5. Functional Design Patterns ⭐ **MANDATORY**

**REQUIRED**: Always use functional programming patterns where applicable.

#### 5.1 Pure Functions

**Definition**: Functions that:
1. Always return the same output for the same inputs
2. Have no side effects (don't modify external state)
3. Don't depend on external state

```python
# ❌ BAD: Impure function with side effects
class ContentAnalyzer:
    def __init__(self):
        self.total_score = 0  # Mutable state

    def analyze(self, content):
        """
        Analyze content and update internal state.

        PROBLEM: Side effect (modifies self.total_score)
        Makes testing harder, not thread-safe
        """
        score = content.quality_score + content.engagement_score
        self.total_score += score  # Side effect!
        return score

# ✅ GOOD: Pure function
def analyze_content(content: Content) -> float:
    """
    Analyze content and return score.

    WHY: Pure function - same input always produces same output.
    No side effects, easy to test, thread-safe.
    HOW: Takes input, performs calculation, returns result.

    Args:
        content: Content to analyze

    Returns:
        Combined quality and engagement score
    """
    # WHAT: Calculate combined score
    # WHY: Provides unified metric for content evaluation
    return content.quality_score + content.engagement_score

# ✅ GOOD: Using pure functions
def analyze_all_content(contents: List[Content]) -> List[float]:
    """
    Analyze all content using pure functions.

    WHY: Functional approach - composable, testable, parallel-friendly.
    """
    # WHAT: Map pure function over all content
    # WHY: No shared state, can run in parallel
    return [analyze_content(content) for content in contents]

    # Or using map (functional style)
    return list(map(analyze_content, contents))
```

#### 5.2 Immutability

**REQUIRED**: Prefer immutable data structures.

```python
# ❌ BAD: Mutable data structures
def update_strategy(strategy, new_tactics):
    """
    Update strategy in place.

    PROBLEM: Mutates input, hard to track changes, not thread-safe.
    """
    strategy.tactics.extend(new_tactics)  # Mutation!
    strategy.updated_at = datetime.now()  # Mutation!
    return strategy

# ✅ GOOD: Immutable approach
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)  # frozen=True makes it immutable
class Strategy:
    """
    Immutable marketing strategy.

    WHY: Immutability prevents bugs from unexpected mutations.
    Makes code easier to reason about and enables optimizations.
    """
    objective: str
    tactics: tuple[str, ...]  # Tuple instead of list (immutable)
    budget: float
    updated_at: datetime

def update_strategy(strategy: Strategy, new_tactics: tuple[str, ...]) -> Strategy:
    """
    Create new strategy with updated tactics.

    WHY: Returns new object instead of mutating.
    Original strategy unchanged - safer and more predictable.
    HOW: Uses dataclass replace() to create modified copy.

    Args:
        strategy: Original strategy (unchanged)
        new_tactics: Tactics to add

    Returns:
        New strategy with combined tactics
    """
    # WHAT: Create new strategy with updated tactics
    # WHY: Functional approach - no mutation, thread-safe
    combined_tactics = strategy.tactics + new_tactics

    return replace(
        strategy,
        tactics=combined_tactics,
        updated_at=datetime.now()
    )

# Usage
original_strategy = Strategy(
    objective="Increase leads",
    tactics=("Content marketing", "LinkedIn ads"),
    budget=10000,
    updated_at=datetime.now()
)

# Creates NEW strategy, original unchanged
updated_strategy = update_strategy(
    original_strategy,
    ("Twitter campaign", "Webinars")
)

assert original_strategy.tactics == ("Content marketing", "LinkedIn ads")
assert updated_strategy.tactics == ("Content marketing", "LinkedIn ads", "Twitter campaign", "Webinars")
```

#### 5.3 Higher-Order Functions

**Definition**: Functions that take functions as arguments or return functions.

```python
# ✅ GOOD: Higher-order function
from typing import Callable, List

def apply_content_filters(
    contents: List[Content],
    filters: List[Callable[[Content], bool]]
) -> List[Content]:
    """
    Apply multiple filters to content list.

    WHY: Higher-order function - accepts functions as arguments.
    Makes filtering logic composable and reusable.
    HOW: Reduces over filters, applying each sequentially.

    Args:
        contents: Content to filter
        filters: List of filter functions (Content -> bool)

    Returns:
        Content passing all filters
    """
    from functools import reduce

    # WHAT: Apply each filter function to content list
    # WHY: Composable filters - easy to add/remove/reorder
    def apply_filter(items, filter_fn):
        return [item for item in items if filter_fn(item)]

    return reduce(apply_filter, filters, contents)

# Define reusable filter functions
def is_high_quality(content: Content) -> bool:
    """Filter for high quality content."""
    return content.quality_score > 80

def is_published(content: Content) -> bool:
    """Filter for published content."""
    return content.status == "published"

def is_recent(content: Content) -> bool:
    """Filter for recent content (last 30 days)."""
    cutoff = datetime.now() - timedelta(days=30)
    return content.published_at > cutoff

# Usage: Compose filters functionally
recent_high_quality_content = apply_content_filters(
    all_content,
    [is_published, is_high_quality, is_recent]
)
```

#### 5.4 Function Composition

**REQUIRED**: Build complex operations from simple functions.

```python
# ✅ GOOD: Function composition
from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

def compose(
    f: Callable[[U], V],
    g: Callable[[T], U]
) -> Callable[[T], V]:
    """
    Compose two functions: (f ∘ g)(x) = f(g(x))

    WHY: Enables building complex operations from simple ones.
    Follows functional programming principle of composition.

    Args:
        f: Function to apply second
        g: Function to apply first

    Returns:
        Composed function
    """
    return lambda x: f(g(x))

# Simple, reusable functions
def extract_keywords(content: Content) -> List[str]:
    """Extract keywords from content."""
    return content.keywords

def filter_common_keywords(keywords: List[str]) -> List[str]:
    """Remove common keywords like 'the', 'and', etc."""
    common = {"the", "and", "or", "but", "in", "on", "at"}
    return [kw for kw in keywords if kw.lower() not in common]

def count_keywords(keywords: List[str]) -> int:
    """Count number of keywords."""
    return len(keywords)

# Compose functions to create pipeline
count_unique_keywords = compose(
    count_keywords,
    compose(filter_common_keywords, extract_keywords)
)

# Usage
keyword_count = count_unique_keywords(content)

# ✅ BETTER: Pipeline pattern (more readable)
from typing import Any

class Pipeline:
    """
    Functional pipeline for composing operations.

    WHY: Makes function composition readable and chainable.
    """

    def __init__(self, value: Any):
        self._value = value

    def pipe(self, func: Callable) -> 'Pipeline':
        """
        Apply function to current value.

        WHY: Enables chaining operations functionally.
        """
        return Pipeline(func(self._value))

    def value(self) -> Any:
        """Get final value."""
        return self._value

# Usage: Readable pipeline
keyword_count = (
    Pipeline(content)
    .pipe(extract_keywords)
    .pipe(filter_common_keywords)
    .pipe(count_keywords)
    .value()
)
```

#### 5.5 Declarative vs Imperative

**REQUIRED**: Write declarative code (WHAT) not imperative (HOW).

```python
# ❌ BAD: Imperative style (focuses on HOW)
def calculate_campaign_metrics(campaigns):
    """Calculate metrics for all campaigns."""
    metrics = {}

    for campaign in campaigns:
        if campaign.status == "active":
            total_spend = 0
            total_conversions = 0

            for ad in campaign.ads:
                total_spend += ad.spend
                total_conversions += ad.conversions

            if total_spend > 0:
                cpa = total_spend / total_conversions
                metrics[campaign.id] = cpa

    return metrics

# ✅ GOOD: Declarative style (focuses on WHAT)
def calculate_campaign_metrics(campaigns: List[Campaign]) -> dict[str, float]:
    """
    Calculate cost-per-acquisition for active campaigns.

    WHY: Declarative approach - describes WHAT we want, not HOW.
    More readable, easier to optimize, less error-prone.
    """
    from itertools import chain

    # WHAT: Get active campaigns
    active_campaigns = [c for c in campaigns if c.status == "active"]

    # WHAT: Calculate metrics for each campaign
    def campaign_cpa(campaign: Campaign) -> tuple[str, float]:
        """Calculate CPA for a single campaign."""
        total_spend = sum(ad.spend for ad in campaign.ads)
        total_conversions = sum(ad.conversions for ad in campaign.ads)

        cpa = total_spend / total_conversions if total_conversions > 0 else 0.0
        return (campaign.id, cpa)

    # WHAT: Map campaign to CPA, convert to dict
    return dict(map(campaign_cpa, active_campaigns))

# ✅ EVEN BETTER: More functional with explicit steps
def calculate_campaign_metrics(campaigns: List[Campaign]) -> dict[str, float]:
    """
    Calculate cost-per-acquisition for active campaigns.

    WHY: Declarative functional approach using composable functions.
    """
    # Step 1: Filter active campaigns
    active = filter(lambda c: c.status == "active", campaigns)

    # Step 2: Calculate CPA for each
    def calculate_cpa(campaign: Campaign) -> tuple[str, float]:
        total_spend = sum(ad.spend for ad in campaign.ads)
        total_conversions = sum(ad.conversions for ad in campaign.ads)
        cpa = total_spend / total_conversions if total_conversions > 0 else 0.0
        return (campaign.id, cpa)

    # Step 3: Create mapping
    return dict(map(calculate_cpa, active))
```

#### 5.6 Partial Application & Currying

**Use when**: Creating specialized versions of general functions.

```python
from functools import partial

# ✅ GOOD: Using partial application
def filter_content(
    content: Content,
    min_quality: float,
    min_engagement: float,
    status: str
) -> bool:
    """
    Generic content filter.

    WHY: General-purpose filter that can be specialized.
    """
    return (
        content.quality_score >= min_quality and
        content.engagement_score >= min_engagement and
        content.status == status
    )

# Create specialized filters using partial application
# WHY: Reusable filters without code duplication
filter_high_quality_published = partial(
    filter_content,
    min_quality=80.0,
    min_engagement=50.0,
    status="published"
)

filter_medium_quality_draft = partial(
    filter_content,
    min_quality=60.0,
    min_engagement=30.0,
    status="draft"
)

# Usage
high_quality = [c for c in all_content if filter_high_quality_published(c)]
medium_drafts = [c for c in all_content if filter_medium_quality_draft(c)]
```

#### 5.7 Benefits of Functional Patterns

**Why use functional patterns**:

1. **Testability**: Pure functions are trivial to test (no setup/teardown)
2. **Composability**: Small functions combine into complex operations
3. **Parallelization**: Pure functions can run concurrently safely
4. **Reasoning**: Easier to understand (no hidden state)
5. **Debugging**: Immutable data makes bugs easier to track
6. **Maintenance**: Declarative code is self-documenting

```python
# Example: Functional approach makes testing trivial
def test_analyze_content():
    """
    Test pure function.

    WHY: No mocks needed, no state to set up.
    """
    # GIVEN
    content = Content(quality_score=80, engagement_score=20)

    # WHEN
    score = analyze_content(content)

    # THEN
    assert score == 100  # Pure function, deterministic result

# Compare to testing impure function:
def test_impure_analyzer():
    """
    Test impure class.

    PROBLEM: Must manage state, reset between tests.
    """
    analyzer = ContentAnalyzer()

    # First call
    content1 = Content(quality_score=80, engagement_score=20)
    score1 = analyzer.analyze(content1)
    assert score1 == 100
    assert analyzer.total_score == 100  # State changed!

    # Second call - state carries over
    content2 = Content(quality_score=60, engagement_score=40)
    score2 = analyzer.analyze(content2)
    assert score2 == 100
    assert analyzer.total_score == 200  # Accumulated state!
```

### 6. Type Hints Everywhere

**REQUIRED**: All functions must have type hints

```python
# ❌ BAD: No type hints
def create_agent(name, role, config):
    return Agent(name, role, config)

# ✅ GOOD: Complete type hints
def create_agent(
    name: str,
    role: AgentRole,
    config: AgentConfig
) -> Agent:
    """
    Create and initialize an agent.

    WHY: Factory function for agent creation with validation.

    Args:
        name: Human-readable agent name
        role: Agent's role in organization
        config: Configuration including LLM settings

    Returns:
        Initialized agent ready for use

    Raises:
        ValidationError: If config is invalid
    """
    _validate_agent_config(config)

    return Agent(
        name=name,
        role=role,
        config=config,
        llm=_initialize_llm_for_role(role)
    )
```

### 7. Exception Handling ⭐ **MANDATORY**

**REQUIRED**: Always wrap base exceptions in custom exceptions.

**WHY**:
- Provides context-specific error information
- Enables better error tracking and logging
- Allows domain-specific error handling
- Prevents leaking implementation details

#### Custom Exception Hierarchy

```python
# core/exceptions.py
"""
Custom exception hierarchy for AI Marketing Director.

WHY: Wraps base exceptions with domain context.
HOW: All exceptions inherit from base MarketingDirectorError.
"""

class MarketingDirectorError(Exception):
    """
    Base exception for all AI Marketing Director errors.

    WHY: Provides common interface for all custom exceptions.
    """

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
        context: dict[str, Any] | None = None
    ):
        """
        Initialize exception with context.

        Args:
            message: Human-readable error message
            original_exception: Original exception being wrapped
            context: Additional context (agent_id, content_id, etc.)
        """
        super().__init__(message)
        self.original_exception = original_exception
        self.context = context or {}
        self.timestamp = datetime.now()

# Infrastructure exceptions
class DatabaseError(MarketingDirectorError):
    """Database operation errors."""

class MessageBusError(MarketingDirectorError):
    """Message bus communication errors."""

class LLMProviderError(MarketingDirectorError):
    """LLM provider errors (API failures, rate limits)."""

class CacheError(MarketingDirectorError):
    """Cache operation errors."""

class IntegrationError(MarketingDirectorError):
    """Third-party integration errors."""

# Agent exceptions
class AgentError(MarketingDirectorError):
    """Base exception for agent errors."""

class AgentValidationError(AgentError):
    """Agent input/output validation errors."""

class AgentExecutionError(AgentError):
    """Agent execution failures."""

# Business logic exceptions
class ContentError(MarketingDirectorError):
    """Content-related errors."""

class CampaignError(MarketingDirectorError):
    """Campaign-related errors."""

class WorkflowError(MarketingDirectorError):
    """Workflow execution errors."""
```

#### Exception Wrapping Pattern

```python
# ❌ BAD: Exposing base exceptions
def get_content(content_id: str) -> Content:
    """Get content by ID."""
    try:
        return db.query(Content).filter_by(id=content_id).first()
    except Exception as e:
        # Leaks implementation details (SQLAlchemy exception)
        raise e

# ✅ GOOD: Wrap in custom exception
from core.exceptions import DatabaseError

def get_content(content_id: str) -> Content:
    """
    Get content by ID.

    WHY: Wraps database exceptions with domain context.

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        return db.query(Content).filter_by(id=content_id).first()

    except SQLAlchemyError as e:
        # WHAT: Wrap base exception with context
        # WHY: Provides domain-specific error with original exception preserved
        raise DatabaseError(
            message=f"Failed to retrieve content: {content_id}",
            original_exception=e,
            context={"content_id": content_id, "operation": "get"}
        ) from e

    except Exception as e:
        # WHAT: Catch unexpected errors
        # WHY: Prevents silent failures, logs unexpected errors
        logger.error("Unexpected error retrieving content", exc_info=e)
        raise DatabaseError(
            message=f"Unexpected error retrieving content: {content_id}",
            original_exception=e,
            context={"content_id": content_id}
        ) from e
```

#### Exception Wrapping in Different Layers

**Infrastructure Layer**:
```python
# infrastructure/llm/claude_provider.py
from core.exceptions import LLMProviderError
import anthropic

async def generate(self, prompt: str) -> str:
    """
    Generate text using Claude API.

    WHY: Wraps Anthropic SDK exceptions with our domain context.
    """
    try:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    except anthropic.RateLimitError as e:
        raise LLMProviderError(
            message="Claude API rate limit exceeded",
            original_exception=e,
            context={
                "provider": "anthropic",
                "model": self.model,
                "error_type": "rate_limit"
            }
        ) from e

    except anthropic.APIError as e:
        raise LLMProviderError(
            message="Claude API error",
            original_exception=e,
            context={
                "provider": "anthropic",
                "model": self.model,
                "error_type": "api_error"
            }
        ) from e

    except Exception as e:
        logger.error("Unexpected LLM provider error", exc_info=e)
        raise LLMProviderError(
            message="Unexpected error calling LLM provider",
            original_exception=e,
            context={"provider": "anthropic", "model": self.model}
        ) from e
```

**Agent Layer**:
```python
# agents/specialists/copywriter/agent.py
from core.exceptions import AgentExecutionError, LLMProviderError

async def create_blog_post(self, topic: str) -> BlogPost:
    """
    Create blog post on given topic.

    WHY: Wraps lower-level exceptions with agent context.
    """
    try:
        # Validate input
        self._validate_topic(topic)

        # Generate content
        content = await self.llm.generate(prompt)

        # Parse and validate output
        return self._parse_blog_post(content)

    except LLMProviderError as e:
        # WHAT: Re-wrap with agent context
        # WHY: Adds agent-specific information to error
        raise AgentExecutionError(
            message=f"Copywriter failed to generate blog post: {topic}",
            original_exception=e,
            context={
                "agent": "copywriter",
                "operation": "create_blog_post",
                "topic": topic,
                "llm_error": str(e)
            }
        ) from e

    except ValidationError as e:
        raise AgentValidationError(
            message="Invalid blog post generated",
            original_exception=e,
            context={"agent": "copywriter", "topic": topic}
        ) from e

    except Exception as e:
        logger.error("Unexpected error in copywriter", exc_info=e)
        raise AgentExecutionError(
            message="Unexpected error creating blog post",
            original_exception=e,
            context={"agent": "copywriter", "topic": topic}
        ) from e
```

#### Benefits of Exception Wrapping

1. **Context Preservation**:
```python
# Original exception buried deep:
# SQLAlchemyError: (psycopg2.errors.UniqueViolation) ...

# Wrapped exception with context:
# DatabaseError: Failed to save content: blog_123
#   context: {"content_id": "blog_123", "operation": "save"}
#   original: SQLAlchemyError(...)
```

2. **Better Logging**:
```python
try:
    content = await save_content(content)
except DatabaseError as e:
    logger.error(
        "Database error",
        extra={
            "error_message": str(e),
            "context": e.context,
            "original_error": str(e.original_exception),
            "timestamp": e.timestamp
        }
    )
```

3. **Abstraction**:
```python
# API layer doesn't need to know about SQLAlchemy
try:
    content = await content_service.save(content)
except DatabaseError as e:
    # Handle domain error, not infrastructure error
    return JSONResponse(
        status_code=500,
        content={"error": "Failed to save content"}
    )
```

### 8. Explicit Comments

**Every function/method must have**:
- Docstring explaining WHAT it does
- Comments explaining WHY design decisions were made
- Comments explaining HOW complex algorithms work

```python
def calculate_engagement_score(metrics: ContentMetrics) -> float:
    """
    Calculate content engagement score from metrics.

    WHAT: Combines likes, comments, shares into single score.
    WHY: Provides unified metric for comparing content performance.

    Formula: (likes * 1) + (comments * 3) + (shares * 5) / views

    WHY these weights:
    - Shares are most valuable (5x) - indicates strong resonance
    - Comments show engagement (3x) - user took time to respond
    - Likes are passive (1x) - lowest engagement signal

    Args:
        metrics: Raw engagement metrics from platform

    Returns:
        Engagement score between 0 and 1
    """
    # Prevent division by zero
    # WHY: Content with zero views has undefined engagement
    if metrics.views == 0:
        return 0.0

    # Calculate weighted engagement
    # WHY: Different actions indicate different levels of engagement
    weighted_engagement = (
        (metrics.likes * 1) +      # Passive engagement
        (metrics.comments * 3) +   # Active engagement
        (metrics.shares * 5)       # Strong endorsement
    )

    # Normalize by views
    # WHY: Accounts for content reach; popular content isn't always engaging
    score = weighted_engagement / metrics.views

    # Cap at 1.0 for consistency
    # WHY: Viral content can have score > 1; cap for consistency
    return min(score, 1.0)
```

---

## Design Patterns & SOLID

### SOLID Principles

#### S - Single Responsibility Principle

**Rule**: Each class should have ONE reason to change

```python
# ❌ BAD: Agent doing too much
class Agent:
    def create_content(self): ...
    def publish_to_linkedin(self): ...
    def send_email(self): ...
    def analyze_performance(self): ...
    # TOO MANY RESPONSIBILITIES!

# ✅ GOOD: Separate classes for separate concerns
class ContentCreator:
    """
    Creates marketing content.

    WHY: Single responsibility - content creation only.
    Follows SRP by focusing solely on content generation.
    """
    def create_blog_post(self, topic: str) -> BlogPost: ...
    def create_social_post(self, topic: str) -> SocialPost: ...

class ContentPublisher:
    """
    Publishes content to platforms.

    WHY: Single responsibility - content distribution only.
    Separate from creation so publishing logic can evolve independently.
    """
    def publish_to_linkedin(self, content: SocialPost) -> PublishResult: ...
    def publish_to_twitter(self, content: SocialPost) -> PublishResult: ...

class PerformanceAnalyzer:
    """
    Analyzes content performance.

    WHY: Single responsibility - analytics only.
    Separates analysis from creation and publishing.
    """
    def analyze_engagement(self, content_id: str) -> Metrics: ...
    def generate_report(self, timeframe: str) -> Report: ...
```

#### O - Open/Closed Principle

**Rule**: Open for extension, closed for modification

```python
# ✅ GOOD: Using strategy pattern for extensibility
class ContentScorer(ABC):
    """
    Base class for content scoring strategies.

    WHY: Allows adding new scoring algorithms without modifying existing code.
    Follows Open/Closed Principle.
    """

    @abstractmethod
    def score(self, content: Content) -> float:
        """Calculate content score."""
        pass

class SEOScorer(ContentScorer):
    """Scores content based on SEO factors."""

    def score(self, content: Content) -> float:
        """
        Calculate SEO score.

        WHY: Separate class for SEO scoring logic.
        Can be modified/replaced without affecting other scorers.
        """
        # ... SEO scoring logic
        return seo_score

class BrandVoiceScorer(ContentScorer):
    """Scores content based on brand voice consistency."""

    def score(self, content: Content) -> float:
        """Calculate brand voice score."""
        # ... brand voice scoring logic
        return brand_score

class CompositeScorer:
    """
    Combines multiple scoring strategies.

    WHY: Allows flexible composition of scoring logic.
    New scorers can be added without modifying this class.
    """

    def __init__(self, scorers: List[ContentScorer]):
        self.scorers = scorers

    def score(self, content: Content) -> float:
        """
        Calculate weighted average of all scorer scores.

        WHY: Provides overall content quality metric.
        """
        scores = [scorer.score(content) for scorer in self.scorers]
        return sum(scores) / len(scores)
```

#### L - Liskov Substitution Principle

**Rule**: Subtypes must be substitutable for base types

```python
# ✅ GOOD: Proper inheritance
class Agent(ABC):
    """Base agent class."""

    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """
        Process a task.

        WHY: All agents must be able to process tasks.
        Subclasses can override but must maintain contract.
        """
        pass

class CMOAgent(Agent):
    """
    CMO agent - strategic leadership.

    WHY: Extends base Agent with strategic capabilities.
    Maintains contract: can process tasks like any agent.
    """

    def process_task(self, task: Task) -> TaskResult:
        """
        Process strategic task.

        WHY: CMO processes strategic tasks specifically.
        Still returns TaskResult like base class (LSP compliance).
        """
        if task.type != TaskType.STRATEGIC:
            raise InvalidTaskError("CMO only handles strategic tasks")

        # Process strategic task
        result = self._execute_strategic_task(task)
        return result  # Returns TaskResult as expected

class CopywriterAgent(Agent):
    """Copywriter agent - content creation."""

    def process_task(self, task: Task) -> TaskResult:
        """
        Process content creation task.

        WHY: Copywriter processes writing tasks specifically.
        Returns TaskResult like base class (LSP compliance).
        """
        if task.type != TaskType.CONTENT_CREATION:
            raise InvalidTaskError("Copywriter only handles writing tasks")

        # Process writing task
        result = self._create_content(task)
        return result  # Returns TaskResult as expected
```

#### I - Interface Segregation Principle

**Rule**: Don't force clients to depend on methods they don't use

```python
# ❌ BAD: Fat interface
class Agent(ABC):
    @abstractmethod
    def create_content(self): ...
    @abstractmethod
    def publish_content(self): ...
    @abstractmethod
    def analyze_performance(self): ...
    # Not all agents need all these methods!

# ✅ GOOD: Segregated interfaces
class ContentCreator(ABC):
    """Interface for content creation."""
    @abstractmethod
    def create_content(self, topic: str) -> Content: ...

class ContentPublisher(ABC):
    """Interface for content publishing."""
    @abstractmethod
    def publish_content(self, content: Content) -> PublishResult: ...

class PerformanceAnalyzer(ABC):
    """Interface for performance analysis."""
    @abstractmethod
    def analyze_performance(self, content_id: str) -> Metrics: ...

# Agents implement only what they need
class CopywriterAgent(ContentCreator):
    """
    Copywriter only creates content.

    WHY: Doesn't need publishing or analysis capabilities.
    Implements only ContentCreator interface (ISP compliance).
    """
    def create_content(self, topic: str) -> Content:
        # ... implementation
        pass

class PublisherAgent(ContentPublisher):
    """
    Publisher only publishes content.

    WHY: Doesn't create or analyze content.
    Implements only ContentPublisher interface (ISP compliance).
    """
    def publish_content(self, content: Content) -> PublishResult:
        # ... implementation
        pass
```

#### D - Dependency Inversion Principle

**Rule**: Depend on abstractions, not concretions

```python
# ❌ BAD: Depending on concrete implementation
class CMOAgent:
    def __init__(self):
        self.llm = ClaudeOpusLLM()  # Concrete dependency!

# ✅ GOOD: Depending on abstraction
class LLMProvider(ABC):
    """
    Abstract LLM provider.

    WHY: Allows swapping LLM implementations without changing agent code.
    Follows Dependency Inversion Principle.
    """
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class ClaudeOpusLLM(LLMProvider):
    """Claude Opus implementation."""
    def generate(self, prompt: str) -> str:
        # ... Claude API call
        pass

class CMOAgent:
    """
    CMO agent with injected dependencies.

    WHY: Depends on LLMProvider abstraction, not concrete implementation.
    Can use any LLM provider (Claude, GPT, local model, mock for testing).
    """

    def __init__(self, llm: LLMProvider):  # Inject dependency
        """
        Initialize CMO with LLM provider.

        WHY: Dependency injection allows flexibility and testability.
        """
        self.llm = llm

    def set_strategy(self, objective: str) -> Strategy:
        """Create strategy using injected LLM."""
        prompt = f"Create strategy for: {objective}"
        response = self.llm.generate(prompt)  # Uses abstraction
        return self._parse_strategy(response)

# Factory for creating agents with real dependencies
def create_cmo_agent() -> CMOAgent:
    """
    Factory for creating CMO agent with production dependencies.

    WHY: Centralized dependency configuration.
    Makes it easy to swap implementations.
    """
    llm = ClaudeOpusLLM()  # Production LLM
    return CMOAgent(llm=llm)

# Testing with mock dependencies
def test_cmo_agent():
    """Test CMO with mock LLM."""
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate.return_value = "Mock strategy"

    cmo = CMOAgent(llm=mock_llm)  # Inject mock
    strategy = cmo.set_strategy("Test objective")

    assert strategy is not None
```

---

## Anti-Patterns (FORBIDDEN)

### 1. ❌ Nested For Loops

**Never use nested for loops**. Use:
- Comprehensions
- `itertools.product()` for Cartesian products
- `map()` and `filter()` for transformations
- Generator expressions for memory efficiency

### 2. ❌ Nested If Statements

**Never nest if statements**. Use:
- Guard clauses (early returns)
- Strategy pattern for complex conditions
- Polymorphism to replace conditionals
- Look-up tables/dictionaries

### 3. ❌ Long Functions

**Never write functions > 50 lines**. If longer:
- Extract helper methods
- Use composition
- Break into smaller functions

### 4. ❌ Global State

**Never use global variables**. Use:
- Dependency injection
- Configuration objects
- Context managers

### 5. ❌ Magic Numbers

**Never use magic numbers**. Use:
- Named constants
- Configuration
- Enums

```python
# ❌ BAD
if score > 80:  # What is 80?
    approve()

# ✅ GOOD
APPROVAL_THRESHOLD = 80  # Minimum score for auto-approval

if score > APPROVAL_THRESHOLD:
    approve()
```

---

## Code Examples

### Example: Complete Agent Class Following All Standards

```python
# agents/cmo_agent.py
"""
CMO (Chief Marketing Officer) Agent.

WHY: Provides strategic leadership for the AI marketing department.
Acts as highest-level decision maker in agent hierarchy.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

# Domain models
@dataclass
class MarketingStrategy:
    """
    Marketing strategy with tactics and budget.

    WHY: Encapsulates strategic plan created by CMO.
    Immutable data class for safety.
    """
    objective: str
    timeframe: str
    tactics: List[str]
    budget_allocation: Dict[str, float]
    kpis: Dict[str, float]

class StrategyValidationError(Exception):
    """Raised when strategy validation fails."""
    pass

# Abstract dependencies (Dependency Inversion Principle)
class LLMProvider(ABC):
    """Abstract LLM provider."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        pass

class MarketDataProvider(ABC):
    """Abstract market data provider."""

    @abstractmethod
    def get_performance_data(self, timeframe: str) -> Dict[str, Any]:
        """Get historical performance data."""
        pass

# CMO Agent (Single Responsibility Principle)
class CMOAgent:
    """
    CMO Agent - Strategic marketing leadership.

    Responsibilities (SRP):
    - Create marketing strategies
    - Allocate budget across channels
    - Monitor high-level KPIs

    Does NOT:
    - Execute tactics (delegates to VP Marketing)
    - Create content (delegates to specialists)
    - Publish content (delegates to publishers)
    """

    # Configuration constants
    MIN_BUDGET_ALLOCATION = 1000  # Minimum budget per channel (USD)
    STRATEGY_CONFIDENCE_THRESHOLD = 0.8  # Minimum confidence for auto-approval

    def __init__(
        self,
        llm: LLMProvider,
        market_data: MarketDataProvider,
        agent_id: str = "cmo"
    ):
        """
        Initialize CMO agent.

        WHY: Uses dependency injection for testability and flexibility.

        Args:
            llm: LLM provider for strategy generation
            market_data: Market data provider for informed decisions
            agent_id: Unique identifier for this agent
        """
        self.llm = llm
        self.market_data = market_data
        self.agent_id = agent_id
        self._validator = StrategyValidator()  # Composition over inheritance

    def create_strategy(
        self,
        objective: str,
        timeframe: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> MarketingStrategy:
        """
        Create marketing strategy based on objective.

        WHY: CMO's primary responsibility is setting strategic direction.
        Uses market data and LLM to generate data-driven strategies.

        Args:
            objective: Strategic goal (e.g., "Increase enterprise leads 50%")
            timeframe: Time period (e.g., "Q4 2025")
            constraints: Optional budget/resource constraints

        Returns:
            MarketingStrategy with tactics and budget allocation

        Raises:
            StrategyValidationError: If generated strategy is invalid

        Example:
            >>> cmo = create_cmo_agent()
            >>> strategy = cmo.create_strategy(
            ...     objective="Increase leads 50%",
            ...     timeframe="Q4 2025"
            ... )
            >>> assert strategy.objective == "Increase leads 50%"
        """
        # Guard clauses for validation (no nested ifs)
        self._validate_inputs(objective, timeframe)

        # Get market data for informed strategy
        # WHY: Strategies should be data-driven, not arbitrary
        performance_data = self.market_data.get_performance_data(timeframe)

        # Build LLM prompt
        # WHY: Separated into method for reusability and testing
        prompt = self._build_strategy_prompt(
            objective=objective,
            timeframe=timeframe,
            performance_data=performance_data,
            constraints=constraints
        )

        # Generate strategy using LLM
        # WHY: LLM provides creative strategic thinking based on data
        llm_response = self._generate_with_retry(prompt)

        # Parse and validate strategy
        # WHY: LLMs can hallucinate; must validate all outputs
        strategy = self._parse_strategy_response(llm_response)
        self._validator.validate(strategy)

        return strategy

    def _validate_inputs(self, objective: str, timeframe: str) -> None:
        """
        Validate strategy inputs.

        WHY: Fail fast on invalid inputs rather than processing bad data.
        HOW: Uses guard clauses instead of nested ifs.
        """
        if not objective or not objective.strip():
            raise ValueError("Objective cannot be empty")

        if not timeframe or not timeframe.strip():
            raise ValueError("Timeframe cannot be empty")

        # Additional validations...

    def _build_strategy_prompt(
        self,
        objective: str,
        timeframe: str,
        performance_data: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build LLM prompt for strategy generation.

        WHY: Separates prompt engineering from main logic (SRP).
        Allows testing prompt generation independently.

        Returns:
            Formatted prompt for LLM
        """
        # Build prompt using data
        # (Implementation details...)
        return prompt

    def _generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3
    ) -> str:
        """
        Generate LLM response with retry logic.

        WHY: LLM APIs can fail; retry ensures reliability.
        HOW: Exponential backoff for retries.
        """
        # Retry logic
        # (Implementation details...)
        return response

    def _parse_strategy_response(self, response: str) -> MarketingStrategy:
        """
        Parse LLM response into MarketingStrategy.

        WHY: Converts unstructured LLM output to structured data.
        """
        # Parsing logic
        # (Implementation details...)
        return strategy

# Validator (Single Responsibility Principle)
class StrategyValidator:
    """
    Validates marketing strategies.

    WHY: Separate class for validation logic (SRP).
    Allows reuse and independent testing.
    """

    def validate(self, strategy: MarketingStrategy) -> None:
        """
        Validate strategy meets business rules.

        WHY: Ensures strategies are feasible and complete.

        Raises:
            StrategyValidationError: If strategy invalid
        """
        # Validation rules using guard clauses (no nested ifs)
        self._validate_tactics(strategy.tactics)
        self._validate_budget(strategy.budget_allocation)
        self._validate_kpis(strategy.kpis)

    def _validate_tactics(self, tactics: List[str]) -> None:
        """Validate tactics are specified."""
        if not tactics:
            raise StrategyValidationError("Strategy must have at least one tactic")

    def _validate_budget(self, budget: Dict[str, float]) -> None:
        """Validate budget allocation."""
        if not budget:
            raise StrategyValidationError("Strategy must allocate budget")

        # Check minimum budget per channel
        insufficient = [
            channel
            for channel, amount in budget.items()
            if amount < CMOAgent.MIN_BUDGET_ALLOCATION
        ]

        if insufficient:
            raise StrategyValidationError(
                f"Channels {insufficient} below minimum budget"
            )

    def _validate_kpis(self, kpis: Dict[str, float]) -> None:
        """Validate KPIs are defined."""
        if not kpis:
            raise StrategyValidationError("Strategy must define KPIs")

# Factory function (Dependency Inversion Principle)
def create_cmo_agent(
    llm_provider: Optional[LLMProvider] = None,
    market_data_provider: Optional[MarketDataProvider] = None
) -> CMOAgent:
    """
    Factory for creating CMO agent with dependencies.

    WHY: Centralizes dependency configuration.
    Allows easy swapping of implementations.

    Args:
        llm_provider: Optional custom LLM provider (uses default if None)
        market_data_provider: Optional custom market data (uses default if None)

    Returns:
        Configured CMO agent ready for use
    """
    # Use default implementations if not provided
    llm = llm_provider or ClaudeOpusLLM()
    market_data = market_data_provider or PostgreSQLMarketData()

    return CMOAgent(
        llm=llm,
        market_data=market_data
    )
```

---

## Test Templates

### Unit Test Template

```python
# tests/unit/test_<module>.py
"""Unit tests for <module>."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from <module> import <ClassUnderTest>

class Test<ClassName>:
    """
    Unit tests for <ClassName>.

    WHY: Ensures <ClassName> works correctly in isolation.
    """

    @pytest.fixture
    def <object_name>(self):
        """
        Fixture providing <ClassName> with mocked dependencies.

        WHY: Isolates unit under test from external dependencies.
        """
        # Mock all external dependencies
        mock_dependency = Mock()

        # Create object under test
        obj = <ClassName>(dependency=mock_dependency)

        return obj

    def test_<method>_with_valid_input(self, <object_name>):
        """
        Test <method> with valid inputs.

        WHY: Validates happy path works correctly.
        """
        # GIVEN: Valid inputs
        input_value = "valid_input"

        # WHEN: Calling method
        result = <object_name>.<method>(input_value)

        # THEN: Should return expected result
        assert result is not None
        assert result.property == expected_value

    def test_<method>_with_invalid_input(self, <object_name>):
        """
        Test <method> with invalid inputs.

        WHY: Ensures proper error handling.
        """
        # GIVEN: Invalid input
        invalid_input = None

        # WHEN/THEN: Should raise appropriate exception
        with pytest.raises(ValueError):
            <object_name>.<method>(invalid_input)

    def test_<method>_handles_dependency_failure(self, <object_name>):
        """
        Test <method> when dependency fails.

        WHY: Ensures graceful handling of external failures.
        """
        # GIVEN: Dependency raises exception
        <object_name>.dependency.method.side_effect = Exception("Dependency failed")

        # WHEN/THEN: Should handle error appropriately
        with pytest.raises(<CustomException>):
            <object_name>.<method>("input")
```

### Integration Test Template

```python
# tests/integration/test_<module>_integration.py
"""Integration tests for <module>."""

import pytest
from <module> import <ClassUnderTest>

@pytest.fixture
async def test_infrastructure():
    """
    Setup test infrastructure (database, message bus, etc.).

    WHY: Integration tests need real infrastructure.
    Uses separate test instances to avoid affecting production.
    """
    # Setup test database, message bus, etc.
    db = TestDatabase()
    await db.connect()

    yield db

    # Cleanup
    await db.cleanup()
    await db.disconnect()

@pytest.mark.integration
class Test<ClassName>Integration:
    """
    Integration tests for <ClassName>.

    WHY: Validates <ClassName> works with real dependencies.
    """

    async def test_<workflow>(self, test_infrastructure):
        """
        Test complete workflow with real infrastructure.

        WHY: Ensures components integrate correctly.
        """
        # GIVEN: System with real infrastructure
        obj = <ClassName>(database=test_infrastructure)

        # WHEN: Running workflow
        result = await obj.execute_workflow()

        # THEN: Workflow should complete successfully
        assert result.status == "success"

        # Verify data was persisted
        persisted_data = await test_infrastructure.get_data()
        assert persisted_data is not None
```

### E2E Test Template

```python
# tests/e2e/test_<workflow>_e2e.py
"""E2E tests for <workflow>."""

import pytest
from tests.helpers import SystemTestHarness

@pytest.mark.e2e
@pytest.mark.slow
class Test<Workflow>E2E:
    """
    E2E tests for <workflow>.

    WHY: Validates complete system works for real use cases.
    """

    @pytest.fixture
    async def system(self):
        """
        Full system test harness.

        WHY: E2E tests need complete running system.
        """
        harness = SystemTestHarness()
        await harness.start()

        yield harness

        await harness.stop()
        await harness.cleanup()

    async def test_complete_<workflow>(self, system):
        """
        Test complete <workflow> end-to-end.

        WHY: Validates real user scenario works.
        """
        # GIVEN: System is running
        assert await system.is_healthy()

        # WHEN: User performs workflow
        result = await system.perform_user_action(<action>)

        # Wait for workflow to complete
        final_result = await system.wait_for_completion(
            result.id,
            timeout=60
        )

        # THEN: Workflow should complete successfully
        assert final_result.status == "completed"
        assert final_result.output is not None

        # Verify side effects
        assert await system.verify_side_effect(<expected_side_effect>)
```

---

## Adherence to Specifications

### Required Reading Before Coding

**ALL code must follow**:
1. **SPECIFICATION.md** - Software specification
2. **MULTIAGENT_ARCHITECTURE.md** - System architecture
3. **ADRs** (Architecture Decision Records) - Design decisions
4. **This document** (DEVELOPMENT_STANDARDS.md)

### Verification Checklist

Before submitting code, verify:

- [ ] Follows TDD (tests written first)
- [ ] All 5 test types present (unit, integration, e2e, lint, regression)
- [ ] No nested for loops
- [ ] No nested if statements
- [ ] Uses comprehensions/map/filter
- [ ] Follows SOLID principles
- [ ] Follows SRP
- [ ] Type hints on all functions
- [ ] Explicit comments (WHAT, WHY, HOW)
- [ ] Follows specifications and ADRs
- [ ] Passes all linters (black, pylint, flake8, mypy)
- [ ] 90%+ test coverage
- [ ] All tests pass

---

## Code Review Checklist

### Automated Checks (CI/CD)

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      # Linting
      - name: Black
        run: black --check .

      - name: Pylint
        run: pylint ai_marketing_director/

      - name: Flake8
        run: flake8 ai_marketing_director/

      - name: MyPy
        run: mypy ai_marketing_director/

      # Testing
      - name: Unit Tests
        run: pytest tests/unit/ --cov --cov-report=xml

      - name: Integration Tests
        run: pytest tests/integration/

      - name: E2E Tests
        run: pytest tests/e2e/

      # Coverage
      - name: Coverage Check
        run: |
          coverage report --fail-under=90
```

### Manual Review Checklist

Reviewer must verify:

**Code Quality**:
- [ ] No code smells or anti-patterns
- [ ] Functions are small and focused
- [ ] Naming is clear and consistent
- [ ] No magic numbers or strings
- [ ] No nested for loops (use comprehensions/itertools)
- [ ] No nested if statements (use guard clauses)

**Functional Patterns**:
- [ ] Functions are pure where possible (no side effects)
- [ ] Immutable data structures used (frozen dataclasses, tuples)
- [ ] Declarative over imperative style
- [ ] Higher-order functions used appropriately
- [ ] Function composition for complex operations
- [ ] No unnecessary stateful classes

**Exception Handling**:
- [ ] All base exceptions wrapped in custom exceptions
- [ ] Exception hierarchy follows domain model
- [ ] Context information included in exceptions
- [ ] Original exception preserved with `from e`
- [ ] Unexpected errors logged before raising
- [ ] Exceptions documented in docstrings

**Testing**:
- [ ] Tests are comprehensive
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Tests are independent
- [ ] Mocks are used appropriately

**Documentation**:
- [ ] All functions have docstrings
- [ ] Complex logic is commented
- [ ] WHY is explained, not just WHAT

**Architecture**:
- [ ] Follows system architecture
- [ ] Consistent with ADRs
- [ ] Follows design patterns
- [ ] Maintains separation of concerns

---

## Summary

### The Golden Rules

1. **TDD Always**: Red-Green-Refactor
2. **5 Test Types**: Unit, Integration, E2E, Lint, Regression
3. **No Nesting**: No nested loops or nested ifs
4. **Pythonic**: Comprehensions, map, filter
5. **Functional**: Pure functions, immutability, composition
6. **SOLID**: All principles, especially SRP
7. **Exception Wrapping**: Always wrap base exceptions in custom exceptions
8. **Explicit**: Comment WHAT, WHY, and HOW
9. **Type Safe**: Type hints everywhere
10. **Spec Compliant**: Follow all specifications and ADRs

### Remember

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand." - Martin Fowler

> "The best code is no code at all." - Jeff Atwood

> "First, solve the problem. Then, write the code." - John Johnson

---

**This document is mandatory for all code generation in the AI Marketing Director project.**

**Violations will result in code rejection.**

**When in doubt, refer to this document.**

---

*Last Updated: 2025-11-03 (Added Functional Design Patterns)*
*Version: 2.1*
*Status: Active*
