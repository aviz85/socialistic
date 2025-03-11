# Testing Guide for Socialistic

This directory contains tests for the Socialistic platform. The tests are organized by component and test type.

## Test Structure

- `tests/users/`: Tests for user-related functionality
- `tests/posts/`: Tests for post-related functionality
- `tests/projects/`: Tests for project-related functionality
- `tests/notifications/`: Tests for notification-related functionality
- `tests/integration/`: Integration tests that test multiple components together
- `tests/security/`: Security-focused tests
- `tests/performance/`: Performance tests

## Current Status

The tests are currently failing because they were written based on the expected API structure, but the actual implementation may differ. To make the tests pass, you'll need to either:

1. Update the tests to match the actual implementation, or
2. Update the implementation to match the expected API structure in the tests.

The second option is recommended, as the tests were designed to cover all the requirements and user stories.

## Common Issues

- URL name mismatches: Many tests are failing because they're trying to use URL names that don't exist in the current implementation.
- Field name differences: Some tests are failing because they're using field names that don't match the actual model fields.
- Missing methods: Some model methods referenced in the tests (like `mark_as_read()` for notifications) don't exist in the current implementation.

## Running Tests

### Running All Tests

To run all tests:

```bash
python manage.py test
```

Or using pytest:

```bash
pytest
```

### Running Specific Test Categories

To run tests with specific markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only model tests
pytest -m model

# Run only API tests
pytest -m api

# Run only security tests
pytest -m security

# Run only performance tests
pytest -m performance
```

### Running Tests for Specific Components

To run tests for specific components:

```bash
# Run all user tests
pytest tests/users/

# Run all post tests
pytest tests/posts/

# Run all project tests
pytest tests/projects/

# Run all notification tests
pytest tests/notifications/

# Run all integration tests
pytest tests/integration/
```

### Running a Specific Test File

To run a specific test file:

```bash
pytest tests/users/test_models.py
```

### Running a Specific Test Class or Method

To run a specific test class:

```bash
pytest tests/users/test_models.py::TestUserModel
```

To run a specific test method:

```bash
pytest tests/users/test_models.py::TestUserModel::test_user_creation
```

## Test Coverage

To run tests with coverage:

```bash
pytest --cov=.
```

To generate a coverage report:

```bash
pytest --cov=. --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Test Fixtures

Test fixtures are defined in `tests/conftest.py`. These fixtures provide common test data and objects that can be used across multiple tests.

## Adding New Tests

When adding new tests, follow these guidelines:

1. Place the test in the appropriate directory based on the component being tested.
2. Use the appropriate markers to categorize the test.
3. Follow the naming convention: `test_*.py` for test files, `Test*` for test classes, and `test_*` for test methods.
4. Use fixtures from `conftest.py` when possible to avoid duplicating test setup code.
5. Write clear docstrings for test classes and methods to explain what is being tested.

## Continuous Integration

Tests are automatically run in the CI pipeline when changes are pushed to the repository. The CI pipeline will fail if any tests fail or if the test coverage falls below the required threshold. 