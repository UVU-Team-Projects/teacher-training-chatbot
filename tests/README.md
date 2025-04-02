# Tests Directory Guide

This directory contains all test files for the Utah Elementary Teacher Training Assistant (UTAH-TTA). It follows a structured approach to testing, covering unit tests, integration tests, and end-to-end scenarios.

## 📋 Table of Contents
- [Directory Structure](#directory-structure)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Data](#test-data)
- [CI/CD Integration](#cicd-integration)

## Directory Structure

```
tests/
├── ai/                         # AI component tests
│   ├── test_embedding.py      # Embedding generation tests
│   ├── test_rag_pipeline.py   # RAG implementation tests
│   ├── test_evaluation.py     # Response evaluation tests
│   └── conftest.py           # AI test fixtures
│
├── database/                   # Database component tests
│   ├── test_models.py        # Model tests
│   ├── test_vector_ops.py    # Vector operation tests
│   └── test_connection.py    # Connection tests
│
├── frontend/                   # Frontend component tests
│   ├── test_routes.py        # Route tests
│   └── test_templates.py     # Template tests
│
├── integration/                # Integration tests
│   ├── test_ai_db.py         # AI-Database integration
│   ├── test_api_frontend.py  # API-Frontend integration
│   └── test_full_flow.py     # End-to-end tests
│
├── scenarios/                  # Scenario tests
│   ├── test_validation.py    # Scenario validation tests
│   └── test_processing.py    # Scenario processing tests
│
├── conftest.py                # Global test fixtures
└── pytest.ini                 # Pytest configuration
```

## Test Categories

### AI Tests (`ai/`)
- Test embedding generation accuracy
- Validate RAG pipeline functionality
- Verify response evaluation logic
- Test model integration

### Database Tests (`database/`)
- Test ORM model operations
- Verify vector similarity search
- Test connection management
- Validate data integrity

### Frontend Tests (`frontend/`)
- Test route functionality
- Validate template rendering
- Test form handling
- Verify error pages

### Integration Tests (`integration/`)
- Test component interactions
- Verify data flow
- Test error handling
- Performance testing

### Scenario Tests (`scenarios/`)
- Validate scenario format
- Test processing pipeline
- Verify evaluation criteria
- Test feedback generation

## Running Tests

### Basic Usage
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/ai/
pytest tests/database/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

### Test Configuration
```ini
# pytest.ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --cov=src --cov-report=html
testpaths = tests
```

## Writing Tests

### Test Structure
```python
# Example test file structure
import pytest
from src.ai import embedding

def test_embedding_generation():
    """Test embedding generation functionality."""
    # Arrange
    text = "Sample text"
    
    # Act
    embedding_vector = embedding.generate(text)
    
    # Assert
    assert len(embedding_vector) == 384
```

### Best Practices
1. **Naming Conventions**
   - Use descriptive test names
   - Follow `test_*` pattern
   - Group related tests in classes

2. **Test Organization**
   - Use Arrange-Act-Assert pattern
   - Keep tests focused and atomic
   - Use appropriate fixtures

3. **Mocking and Fixtures**
   - Mock external dependencies
   - Create reusable fixtures
   - Use appropriate scopes

4. **Error Testing**
   - Test edge cases
   - Verify error handling
   - Test boundary conditions

## Test Data

### Fixtures (`conftest.py`)
```python
@pytest.fixture
def sample_scenario():
    """Provide a sample scenario for testing."""
    return {
        "id": "TEST001",
        "content": "Test scenario content",
        "expected_response": "Expected response"
    }
```

### Mock Data
- Use realistic test data
- Maintain test data versioning
- Document data dependencies
- Clean up test data

## CI/CD Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/
```

### Quality Gates
- Minimum coverage requirements
- Performance thresholds
- Code quality checks
- Documentation validation

## Additional Resources

- [Testing Best Practices](../docs/technical/testing_guide.md)
- [CI/CD Pipeline](../docs/technical/ci_cd.md)
- [Coverage Reports](../docs/technical/coverage.md)
- [Test Data Management](../docs/technical/test_data.md)

## Support

For testing questions:
1. Review testing documentation
2. Check existing test cases
3. Contact QA lead
4. Create testing-related issues 