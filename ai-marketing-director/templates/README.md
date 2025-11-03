# Development Templates

This directory contains templates and examples for developing the AI Marketing Director following our development standards.

## Overview

All templates demonstrate the mandatory coding standards from `DEVELOPMENT_STANDARDS.md`:
- ✅ Test-Driven Development (TDD)
- ✅ 5 test types: unit, integration, e2e, lint, regression
- ✅ Pythonic code (comprehensions, type hints, no nested loops/ifs)
- ✅ SOLID principles
- ✅ Explicit comments (WHAT, WHY, HOW)

## Files

### Test Templates

#### `tests/test_unit_template.py`
**Purpose**: Template for writing unit tests

**Use when**: Testing individual components in isolation

**Key features**:
- Mock fixtures for dependencies (LLM, database, message bus)
- Test naming convention: `test_<method>_<scenario>_<expected_result>`
- Arrange-Act-Assert (Given-When-Then) structure
- Parametrized tests for multiple scenarios
- Edge case testing patterns

**How to use**:
```bash
# 1. Copy to your tests directory
cp templates/tests/test_unit_template.py tests/test_my_agent.py

# 2. Replace placeholders
# - [MODULE] → your module name
# - [CLASS] → your class name

# 3. Write your tests following the examples
```

---

#### `tests/test_integration_template.py`
**Purpose**: Template for integration tests

**Use when**: Testing components working together with real dependencies

**Key features**:
- Real database, message bus, and services (not mocks)
- Test fixtures for environment setup/teardown
- Async test patterns
- Database cleanup between tests
- Message delivery guarantees
- Concurrent operation testing
- Performance tests

**How to use**:
```bash
# 1. Copy to your tests/integration directory
cp templates/tests/test_integration_template.py tests/integration/test_my_feature.py

# 2. Configure test environment
# - Test database connection
# - Test Redis instance
# - Test API endpoints

# 3. Mark with @pytest.mark.integration
```

---

#### `tests/test_e2e_template.py`
**Purpose**: Template for end-to-end tests

**Use when**: Testing complete user workflows in production-like environment

**Key features**:
- Staging environment setup
- Complete user scenarios
- API client patterns
- Multi-agent workflows
- Campaign execution tests
- Performance/load testing
- Error recovery verification

**How to use**:
```bash
# 1. Copy to your tests/e2e directory
cp templates/tests/test_e2e_template.py tests/e2e/test_my_scenario.py

# 2. Configure staging environment
# - Staging database
# - Test accounts for external services (LinkedIn, Twitter)
# - Realistic test data

# 3. Mark with @pytest.mark.e2e
```

---

### Configuration Files

#### `pytest.ini`
**Purpose**: Pytest configuration

**Features**:
- Test discovery patterns
- Markers for test categorization (unit, integration, e2e, slow, regression)
- Default arguments (coverage, parallel execution, timeouts)
- Asyncio support
- Logging configuration

**How to use**:
```bash
# Copy to project root
cp templates/pytest.ini .

# Run tests
pytest                    # Unit + integration only
pytest -m unit           # Unit tests only
pytest -m e2e            # E2E tests only
pytest -m ""             # All tests including slow/e2e
```

---

#### `.pylintrc`
**Purpose**: Pylint configuration for code quality

**Features**:
- Code quality checks
- Naming conventions (snake_case, PascalCase)
- Complexity limits
- Disabled warnings with justifications

**How to use**:
```bash
# Copy to project root
cp templates/.pylintrc .

# Run pylint
pylint agents/
pylint infrastructure/
```

---

#### `.flake8`
**Purpose**: Flake8 configuration for style checking

**Features**:
- PEP 8 style enforcement
- Line length limits
- Cyclomatic complexity checks
- Compatible with black formatter

**How to use**:
```bash
# Copy to project root
cp templates/.flake8 .

# Run flake8
flake8
flake8 agents/
```

---

#### `mypy.ini`
**Purpose**: Mypy configuration for type checking

**Features**:
- Strict type checking
- Type inference
- Protocol support
- Third-party library stubs

**How to use**:
```bash
# Copy to project root
cp templates/mypy.ini .

# Run mypy
mypy .
mypy agents/
```

---

#### `pyproject.toml`
**Purpose**: Configuration for black, isort, and other tools

**Features**:
- Black formatter settings (line length, target version)
- Isort import sorting
- Coverage configuration
- Can also contain pytest config (alternative to pytest.ini)

**How to use**:
```bash
# Copy to project root
cp templates/pyproject.toml .

# Format code
black .
isort .

# Check without modifying
black --check .
isort --check-only .
```

---

### Code Examples

#### `example_agent.py`
**Purpose**: Complete agent implementation following all standards

**Demonstrates**:
- ✅ Type hints everywhere
- ✅ SOLID principles (SRP, OCP, LSP, ISP, DIP)
- ✅ No nested for loops (use comprehensions/itertools)
- ✅ No nested ifs (use guard clauses)
- ✅ Explicit comments (WHAT, WHY, HOW)
- ✅ Pythonic code patterns
- ✅ Dependency injection
- ✅ Strategy pattern for extensibility
- ✅ Protocol-based interfaces
- ✅ Immutable data classes
- ✅ Enum for type-safe constants

**How to use**:
```bash
# Reference when writing new agents
# Copy patterns for:
# - Class structure
# - Method organization
# - Comment style
# - Type hints
# - Error handling
```

**Key patterns to copy**:

1. **Protocol-based dependencies** (ISP, DIP):
```python
class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str: ...

class MyAgent:
    def __init__(self, llm: LLMProvider):  # Depends on protocol, not concrete
        self.llm = llm
```

2. **Guard clauses instead of nested ifs**:
```python
def process(self, task):
    # Guard clauses
    if not task:
        raise ValueError("Task required")

    if task.status != "pending":
        raise InvalidStateError("Task not pending")

    # Main logic (not nested)
    return self._execute(task)
```

3. **List comprehensions instead of for loops**:
```python
# ❌ BAD
results = []
for item in items:
    if item.valid:
        results.append(item.value)

# ✅ GOOD
results = [item.value for item in items if item.valid]
```

4. **Itertools for nested iterations**:
```python
# ❌ BAD
for agent in agents:
    for task in tasks:
        if agent.can_handle(task):
            # ...

# ✅ GOOD
from itertools import product
for agent, task in product(agents, tasks):
    if agent.can_handle(task):
        # ...
```

---

#### `example_tdd_workflow.md`
**Purpose**: Step-by-step TDD example

**Demonstrates**:
- ✅ Red-Green-Refactor cycle
- ✅ Writing tests first
- ✅ Minimal implementation to pass tests
- ✅ Refactoring with test safety net
- ✅ Test naming and structure
- ✅ Edge case testing

**How to use**:
Follow the cycles when building new features:

**Cycle Template**:
```
1. RED: Write failing test
   - Define expected behavior
   - Run test → ❌ Fails

2. GREEN: Make test pass
   - Write minimal code
   - Run test → ✅ Passes

3. REFACTOR: Improve code
   - Clean up implementation
   - Run test → ✅ Still passes

4. REPEAT: Next feature
```

---

## Quick Start

### New Agent Development

1. **Copy test template**:
```bash
cp templates/tests/test_unit_template.py tests/test_my_agent.py
```

2. **Write first test** (RED):
```python
def test_agent_processes_task_successfully(self):
    # GIVEN: Agent with mocked dependencies
    # WHEN: Processing valid task
    # THEN: Returns success result
    pass
```

3. **Run test** (should fail):
```bash
pytest tests/test_my_agent.py -v
```

4. **Implement minimal code** (GREEN):
```python
# agents/my_agent.py
class MyAgent:
    def process_task(self, task):
        return {"status": "success"}
```

5. **Run test again** (should pass):
```bash
pytest tests/test_my_agent.py -v
```

6. **Refactor and repeat**

7. **Reference `example_agent.py`** for patterns

---

### Setting Up Development Environment

```bash
# 1. Copy all config files to project root
cp templates/pytest.ini .
cp templates/.pylintrc .
cp templates/.flake8 .
cp templates/mypy.ini .
cp templates/pyproject.toml .

# 2. Install dev dependencies
pip install pytest pytest-asyncio pytest-cov pytest-xdist
pip install black isort flake8 pylint mypy
pip install -e .

# 3. Format code
black .
isort .

# 4. Run linters
flake8
pylint agents/ infrastructure/
mypy .

# 5. Run tests
pytest
```

---

## Pre-Commit Checklist

Before committing code, run:

```bash
# 1. Format
black . && isort .

# 2. Lint
flake8 && pylint agents/ infrastructure/

# 3. Type check
mypy .

# 4. Test
pytest

# 5. Check coverage
pytest --cov=agents --cov=infrastructure --cov-report=term-missing

# 6. Commit if all pass
git add .
git commit -m "Your message"
```

Or use the one-liner:
```bash
black . && isort . && flake8 && mypy . && pytest && echo "✅ All checks passed!"
```

---

## CI/CD Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Format check
        run: |
          black --check .
          isort --check-only .

      - name: Lint
        run: |
          flake8
          pylint agents/ infrastructure/

      - name: Type check
        run: mypy .

      - name: Test
        run: pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Resources

- **Main Standards Document**: `../DEVELOPMENT_STANDARDS.md`
- **Architecture**: `../MULTIAGENT_ARCHITECTURE.md`
- **Specification**: `../SPECIFICATION.md`
- **Project README**: `../README.md`

---

## Questions?

Refer to:
1. `DEVELOPMENT_STANDARDS.md` for detailed standards
2. `example_agent.py` for code patterns
3. `example_tdd_workflow.md` for TDD process
4. Test templates for testing patterns
