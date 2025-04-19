# BFRPG MUD Testing Guide

This directory contains tests for the BFRPG MUD application. The tests are organized to support the project's testing strategy.

## Test Organization

Tests are organized into three main categories:

- **Unit Tests** (`tests/unit/`): Tests for individual components in isolation
- **Integration Tests** (`tests/integration/`): Tests for how components work together
- **Regression Tests** (`tests/regression/`): Tests for previously fixed bugs

## Running Tests

### Run all tests

```bash
pytest
```

### Run specific test categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Regression tests only
pytest tests/regression/
```

### Run with coverage report

```bash
# Run tests with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

## Test Configuration

Test configuration is managed through:

- **conftest.py**: Contains fixtures and test setup/teardown
- **.env.test**: Environment variables for testing
- **factories.py**: Factory functions for creating test data

## Test Naming Conventions

Tests follow these naming conventions:

- Test files: `test_<module>_<feature>.py`
- Test functions: `test_<behavior>_<condition>()`
- Test classes: `Test<Component>`

## Writing New Tests

When adding new tests:

1. Determine the appropriate category (unit, integration, regression)
2. Place the test file in the correct directory
3. Follow the naming conventions
4. Use existing fixtures from conftest.py where appropriate
5. Create factory functions in factories.py for test data
6. Add proper docstrings to explain what is being tested
7. For regression tests, reference the issue/bug number

### Example Test Structure

```python
"""
Unit tests for example functionality.
"""
import pytest
from app.example import example_function

def test_example_behavior_success():
    """Test that example_function works correctly with valid input."""
    result = example_function(valid_input)
    assert result == expected_output

def test_example_behavior_failure():
    """Test that example_function handles invalid input appropriately."""
    with pytest.raises(ValueError):
        example_function(invalid_input)
```

## Test Markers

Special test markers:

- `@pytest.mark.xfail`: Mark tests expected to fail (with reason)
- `@pytest.mark.regression`: Mark regression tests
- `@pytest.mark.asyncio`: Mark async tests
- `@pytest.mark.parametrize`: Used for parameterized tests

## CI Integration

Tests are run automatically on GitHub Actions:

- All tests must pass before merging
- PRs must include tests for new functionality
- Test coverage is reported and maintained above 80%
