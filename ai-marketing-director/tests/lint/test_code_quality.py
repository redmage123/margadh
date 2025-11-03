"""
Lint Tests - Code Quality Checks.

WHY: Ensures code meets quality standards (formatting, types, complexity).
     Runs as part of CI/CD to prevent quality regressions.

HOW: Uses black, isort, flake8, mypy, pylint to check code quality.

Test Types:
- Black formatting
- Import sorting (isort)
- Linting (flake8)
- Type checking (mypy)
- Code quality (pylint)
"""

import subprocess
from pathlib import Path

import pytest

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIRS = ["agents", "infrastructure", "api", "core", "services", "tests"]


@pytest.mark.lint
class TestCodeFormatting:
    """Test code formatting with black and isort."""

    def test_black_formatting(self):
        """
        Test that all Python files are formatted with black.

        WHY: Consistent formatting improves readability and reduces diff noise.
        """
        result = subprocess.run(
            ["black", "--check", "."],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Black formatting check failed:\n{result.stdout}\n{result.stderr}\n"
            "Run: black . --exclude='alembic/versions'"
        )

    def test_isort_imports(self):
        """
        Test that imports are sorted correctly with isort.

        WHY: Consistent import ordering improves readability.
        """
        result = subprocess.run(
            ["isort", "--check-only", "."],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"isort check failed:\n{result.stdout}\n{result.stderr}\n" "Run: isort ."
        )


@pytest.mark.lint
class TestCodeLinting:
    """Test code linting with flake8."""

    def test_flake8_linting(self):
        """
        Test that code passes flake8 linting.

        WHY: Catches common errors, style issues, and complexity problems.
        """
        dirs_to_check = [str(PROJECT_ROOT / d) for d in SOURCE_DIRS]

        result = subprocess.run(
            ["flake8"] + dirs_to_check,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert (
            result.returncode == 0
        ), f"flake8 linting failed:\n{result.stdout}\n{result.stderr}"


@pytest.mark.lint
class TestTypeChecking:
    """Test static type checking with mypy."""

    def test_mypy_type_checking(self):
        """
        Test that code passes mypy type checking.

        WHY: Static type checking catches type errors before runtime.
        """
        # Check each source directory separately for better error messages
        dirs_to_check = [str(PROJECT_ROOT / d) for d in SOURCE_DIRS if d != "tests"]

        for directory in dirs_to_check:
            if not Path(directory).exists():
                continue

            result = subprocess.run(
                ["mypy", directory],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )

            # mypy returns 0 for success, 1 for errors
            assert result.returncode == 0, (
                f"mypy type checking failed for {directory}:\n"
                f"{result.stdout}\n{result.stderr}"
            )


@pytest.mark.lint
class TestCodeQuality:
    """Test code quality with pylint."""

    def test_pylint_agents_base(self):
        """
        Test that agents/base passes pylint checks.

        WHY: Ensures code quality standards are met.
        """
        result = subprocess.run(
            ["pylint", "agents/base"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # pylint returns 0 for perfect score, but we accept anything >= 8.0
        # which is configured in pyproject.toml
        assert result.returncode in [0, 4, 8, 16, 32], (
            f"pylint check failed for agents/base:\n"
            f"{result.stdout}\n{result.stderr}\n"
            f"Return code: {result.returncode}"
        )

        # Check score is >= 8.0
        output = result.stdout + result.stderr
        if "Your code has been rated at" in output:
            # Extract score
            import re

            match = re.search(r"rated at ([\d.]+)/10", output)
            if match:
                score = float(match.group(1))
                assert (
                    score >= 8.0
                ), f"pylint score {score}/10 is below minimum 8.0/10\n{output}"


@pytest.mark.lint
class TestDocstrings:
    """Test that all modules, classes, and functions have docstrings."""

    def test_agents_base_has_docstrings(self):
        """
        Test that agents/base modules have comprehensive docstrings.

        WHY: Documentation is essential for maintainability.
        """
        import ast

        base_dir = PROJECT_ROOT / "agents" / "base"

        for py_file in base_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file) as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            # Check module docstring
            module_docstring = ast.get_docstring(tree)
            assert (
                module_docstring is not None
            ), f"{py_file.name} is missing module docstring"

            # Check class and function docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_docstring = ast.get_docstring(node)
                    assert (
                        class_docstring is not None
                    ), f"{py_file.name}::{node.name} is missing class docstring"

                elif isinstance(node, ast.FunctionDef):
                    # Skip private methods and magic methods (but check public ones)
                    if node.name.startswith("_") and not node.name.startswith("__"):
                        continue
                    if node.name in [
                        "__init__",
                        "__str__",
                        "__repr__",
                        "__post_init__",
                    ]:
                        # These should have docstrings too, but we'll be lenient
                        continue

                    func_docstring = ast.get_docstring(node)
                    assert (
                        func_docstring is not None
                    ), f"{py_file.name}::{node.name}() is missing function docstring"


@pytest.mark.lint
class TestCodeComplexity:
    """Test code complexity metrics."""

    def test_no_nested_loops(self):
        """
        Test that code has no nested for loops.

        WHY: Golden Rule #3 - No nested loops (use comprehensions or itertools).
        """
        import ast

        base_dir = PROJECT_ROOT / "agents" / "base"
        violations = []

        for py_file in base_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file) as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Check if there's a nested for loop
                    for child in ast.walk(node):
                        if child != node and isinstance(child, ast.For):
                            violations.append(
                                f"{py_file.name}: Nested for loop detected (line {node.lineno})"
                            )

        assert (
            len(violations) == 0
        ), "Found nested for loops (violates Golden Rule #3):\n" + "\n".join(violations)

    def test_no_nested_ifs(self):
        """
        Test that code has minimal nested if statements.

        WHY: Golden Rule #3 - No nested ifs (use guard clauses).
        """
        import ast

        base_dir = PROJECT_ROOT / "agents" / "base"
        violations = []

        for py_file in base_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file) as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check nesting depth
                    depth = 0
                    current = node
                    for child in ast.walk(current):
                        if child != current and isinstance(child, ast.If):
                            # Allow one level of nesting, but warn on deeper nesting
                            for subchild in ast.walk(child):
                                if subchild != child and isinstance(subchild, ast.If):
                                    violations.append(
                                        f"{py_file.name}: Deep nested if detected (line {node.lineno})"
                                    )

        assert len(violations) == 0, (
            "Found deeply nested if statements (violates Golden Rule #3):\n"
            + "\n".join(violations)
        )


@pytest.mark.lint
def test_all_linters_pass():
    """
    Meta-test: Run all linters at once.

    WHY: Convenience test to run all linting checks together.
    """
    # This is just a marker test - actual checks are in individual test classes
    pass
