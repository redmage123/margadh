"""
Unit Test Template.

HOW TO USE:
1. Copy this file to your tests/ directory
2. Replace [MODULE] with the module you're testing
3. Replace [CLASS] with the class you're testing
4. Follow the TDD Red-Green-Refactor cycle

WHY: Unit tests verify individual components in isolation with mocked dependencies.
"""

from unittest.mock import Mock, MagicMock, patch
import pytest
from typing import List, Dict, Any

# Import the module/class you're testing
# from agents.[module] import [Class]


class Test[CLASS]:
    """
    Unit tests for [CLASS].

    WHY: Verify [CLASS] behavior in isolation.
    HOW: Mock all external dependencies (LLM, database, message bus, etc.)
    """

    # Fixtures provide reusable test data and mocked dependencies
    @pytest.fixture
    def mock_llm(self) -> Mock:
        """
        Mock LLM provider.

        WHY: Tests should not make real API calls (slow, costly, flaky).
        HOW: Returns a Mock that simulates LLM responses.
        """
        mock = Mock()
        mock.generate.return_value = "Mocked LLM response"
        return mock

    @pytest.fixture
    def mock_database(self) -> Mock:
        """
        Mock database connection.

        WHY: Tests should not depend on real database state.
        HOW: Returns a Mock that simulates database operations.
        """
        mock = Mock()
        mock.save.return_value = True
        mock.get.return_value = {"id": 1, "status": "active"}
        return mock

    @pytest.fixture
    def instance(self, mock_llm, mock_database):
        """
        Create instance with mocked dependencies.

        WHY: Provides fresh instance for each test (isolation).
        HOW: Injects mocked dependencies via constructor.
        """
        # Replace with your actual class initialization
        # return [CLASS](llm=mock_llm, database=mock_database)
        pass

    # Test naming: test_<method>_<scenario>_<expected_result>
    def test_method_name_with_valid_input_returns_expected_result(self, instance):
        """
        Test [method] with valid input returns expected result.

        GIVEN: Valid input parameters
        WHEN: Method is called
        THEN: Returns expected result
        """
        # GIVEN: Arrange - Set up test data and mocks
        input_data = "valid input"
        expected_output = "expected result"

        # Configure mock behavior
        instance.dependency.method.return_value = "dependency result"

        # WHEN: Act - Call the method being tested
        result = instance.method_name(input_data)

        # THEN: Assert - Verify the result
        assert result == expected_output

        # Verify mock interactions
        instance.dependency.method.assert_called_once_with(input_data)

    def test_method_name_with_invalid_input_raises_error(self, instance):
        """
        Test [method] with invalid input raises appropriate error.

        GIVEN: Invalid input parameters
        WHEN: Method is called
        THEN: Raises [ErrorType]
        """
        # GIVEN: Arrange
        invalid_input = None

        # WHEN + THEN: Act & Assert
        with pytest.raises(ValueError, match="Invalid input"):
            instance.method_name(invalid_input)

    def test_method_name_with_empty_input_returns_empty_result(self, instance):
        """
        Test [method] handles empty input gracefully.

        GIVEN: Empty input
        WHEN: Method is called
        THEN: Returns empty result (not error)
        """
        # GIVEN
        empty_input = []

        # WHEN
        result = instance.method_name(empty_input)

        # THEN
        assert result == []
        assert isinstance(result, list)

    def test_method_name_when_dependency_fails_handles_error(self, instance):
        """
        Test [method] handles dependency failures gracefully.

        GIVEN: Dependency raises exception
        WHEN: Method is called
        THEN: Handles error appropriately (retry, fallback, or propagate)
        """
        # GIVEN: Configure mock to raise exception
        instance.dependency.method.side_effect = ConnectionError("API unavailable")

        # WHEN + THEN: Verify error handling
        with pytest.raises(ConnectionError):
            instance.method_name("input")

        # OR: If method should handle error gracefully
        # result = instance.method_name("input")
        # assert result is None  # or fallback value

    @pytest.mark.parametrize("input_value,expected_output", [
        ("input1", "output1"),
        ("input2", "output2"),
        ("input3", "output3"),
    ])
    def test_method_name_with_various_inputs(self, instance, input_value, expected_output):
        """
        Test [method] with multiple input scenarios.

        WHY: Parametrized tests verify behavior across many cases efficiently.
        """
        # WHEN
        result = instance.method_name(input_value)

        # THEN
        assert result == expected_output

    def test_method_name_calls_dependencies_in_correct_order(self, instance):
        """
        Test [method] calls dependencies in the correct sequence.

        WHY: Verifies workflow orchestration logic.
        """
        # GIVEN
        input_data = "test"

        # WHEN
        instance.method_name(input_data)

        # THEN: Verify call order
        call_order = [
            call[0] for call in instance.dependency.method_calls
        ]
        expected_order = ['prepare', 'execute', 'finalize']
        assert call_order == expected_order

    @patch('module.external_function')
    def test_method_name_with_patched_function(self, mock_external, instance):
        """
        Test [method] with patched external function.

        WHY: Some dependencies are functions, not objects (use @patch decorator).
        """
        # GIVEN: Configure patched function
        mock_external.return_value = "patched result"

        # WHEN
        result = instance.method_name()

        # THEN
        assert result == "patched result"
        mock_external.assert_called_once()


# Additional test classes for edge cases, performance, etc.

class Test[CLASS]EdgeCases:
    """Edge case tests for [CLASS]."""

    def test_handles_unicode_characters(self, instance):
        """Test handling of unicode/special characters."""
        pass

    def test_handles_very_large_input(self, instance):
        """Test performance with large data sets."""
        pass

    def test_handles_concurrent_access(self, instance):
        """Test thread safety if applicable."""
        pass


class Test[CLASS]Integration:
    """
    Integration-style unit tests.

    WHY: Some unit tests verify multiple components working together
    (but still with mocked external dependencies).
    """

    def test_end_to_end_workflow_with_mocks(self, instance):
        """Test complete workflow from start to finish."""
        pass
