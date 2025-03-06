# Source Code Directory Guide

This directory contains the core implementation of the Utah Elementary Teacher Training Assistant (UTAH-TTA). Each subdirectory is organized by functionality, with clear separation of concerns.

## 📋 Table of Contents
- [Directory Structure](#directory-structure)
- [AI Components](#ai-components)
- [Database Components](#database-components)
- [Frontend Components](#frontend-components)
- [API Components](#api-components)
- [Development Guidelines](#development-guidelines)
- [Testing Requirements](#testing-requirements)

## Directory Structure

```
src/
├── ai/                         # AI/ML components
│   ├── embedding.py           # Embedding generation
│   ├── rag_pipeline.py        # RAG implementation
│   ├── llm_config.py         # LLM configuration
│   └── evaluation.py         # Response evaluation
│
├── database/                   # Database components
│   ├── models.py             # Database models
│   ├── vector_ops.py         # Vector operations
│   └── connection.py         # Database connection
│
├── frontend/                   # Frontend components
│   ├── static/               # Static assets
│   ├── templates/            # HTML templates
│   └── routes.py             # Frontend routes
│
└── api/                       # API endpoints
    ├── routes.py             # API routes
    └── middleware.py         # API middleware
```

## AI Components

### Embedding Generation (`embedding.py`)
- Generates vector embeddings for scenarios and responses
- Uses SentenceTransformers for encoding
- Handles batch processing and caching
- Implements dimension reduction and normalization

### RAG Pipeline (`rag_pipeline.py`)
- Implements Retrieval-Augmented Generation
- Manages context retrieval and prompt construction
- Handles response generation and validation
- Implements caching and optimization strategies

### LLM Configuration (`llm_config.py`)
- Manages model parameters and configurations
- Handles model loading and optimization
- Implements temperature and sampling settings
- Manages context window and token limits

### Response Evaluation (`evaluation.py`)
- Evaluates teacher responses against criteria
- Generates feedback based on rubrics
- Implements scoring algorithms
- Handles performance metrics collection

## Database Components

### Database Models (`models.py`)
- SQLAlchemy ORM models
- Vector storage configurations
- Relationship definitions
- Model validation methods

### Vector Operations (`vector_ops.py`)
- pgvector operations implementation
- Similarity search functions
- Index management
- Performance optimization

### Database Connection (`connection.py`)
- Connection pool management
- Transaction handling
- Error recovery
- Health monitoring

## Frontend Components

### Static Assets (`static/`)
- CSS stylesheets
- JavaScript files
- Images and icons
- Font resources

### HTML Templates (`templates/`)
- Base templates
- Component templates
- Error pages
- Email templates

### Frontend Routes (`routes.py`)
- Page routing
- Form handling
- Authentication views
- Error handlers

## API Components

### API Routes (`routes.py`)
- RESTful endpoints
- Request validation
- Response formatting
- Error handling

### Middleware (`middleware.py`)
- Authentication
- Rate limiting
- Logging
- CORS handling

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Maintain consistent naming conventions

### Documentation Requirements
- Module-level documentation
- Function/class documentation
- Example usage
- Performance considerations

### Error Handling
- Use custom exception classes
- Implement proper error logging
- Provide informative error messages
- Handle edge cases

### Performance Considerations
- Implement caching where appropriate
- Optimize database queries
- Minimize API calls
- Profile critical paths

## Testing Requirements

### Unit Tests
- Test each component independently
- Achieve high coverage
- Mock external dependencies
- Test edge cases

### Integration Tests
- Test component interactions
- Verify data flow
- Test error scenarios
- Performance testing

### Documentation Tests
- Verify docstring examples
- Test API documentation
- Validate configuration examples
- Test error messages

## Getting Started

1. **Setting Up Development Environment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up pre-commit hooks
   pre-commit install
   ```

2. **Running Tests**
   ```bash
   # Run unit tests
   pytest tests/unit/
   
   # Run integration tests
   pytest tests/integration/
   ```

3. **Code Quality Checks**
   ```bash
   # Run linter
   flake8 src/
   
   # Run type checker
   mypy src/
   ```

## Additional Resources

- [Architecture Documentation](../docs/technical/architecture/)
- [API Documentation](../docs/technical/api/)
- [Development Guide](../docs/technical/development_guide.md)
- [Testing Guide](../docs/technical/testing_guide.md)

## Support

For development questions:
1. Check the technical documentation
2. Review existing issues
3. Contact the technical lead
4. Create a new issue with detailed information 