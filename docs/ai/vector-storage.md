# Vector Storage Standardization Guide

## Overview

This document outlines the standardized approach for vector storage across the Teacher Training Chatbot project. We use PostgreSQL with pgvector extension as our unified vector storage solution.

## Configuration

### Database Setup
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Standard vector dimension for all embeddings
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    expected_response TEXT NOT NULL,
    expected_response_embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES scenarios(id),
    query TEXT NOT NULL,
    query_embedding vector(384),
    teacher_response TEXT,
    teacher_response_embedding vector(384),
    similarity_score FLOAT
);

CREATE TABLE feedback_templates (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    template_text TEXT NOT NULL,
    template_embedding vector(384),
    min_similarity FLOAT,
    max_similarity FLOAT
);
```

### Index Configuration
```sql
-- Create consistent indexes for vector similarity search
CREATE INDEX idx_scenarios_embedding 
ON scenarios USING ivfflat (expected_response_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_interactions_query
ON interactions USING ivfflat (query_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_feedback_template
ON feedback_templates USING ivfflat (template_embedding vector_cosine_ops)
WITH (lists = 100);
```

## Implementation

### Constants and Configuration
```python
# config/vector_config.py
VECTOR_DIMENSION = 384
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.8
BATCH_SIZE = 32
```

### Embedding Generation
```python
# utils/embedding.py
from sentence_transformers import SentenceTransformer
from config.vector_config import EMBEDDING_MODEL

class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
    
    def get_embedding(self, text):
        return self.model.encode(text)
    
    def batch_get_embeddings(self, texts):
        return self.model.encode(texts)
```

### Database Operations
```python
# database/vector_ops.py
from utils.embedding import EmbeddingGenerator
from config.vector_config import SIMILARITY_THRESHOLD

class VectorOperations:
    def __init__(self):
        self.embedder = EmbeddingGenerator()
    
    def store_scenario(self, name, description, expected_response):
        embedding = self.embedder.get_embedding(expected_response)
        # SQL to store scenario with embedding
        
    def find_similar_scenarios(self, query, threshold=SIMILARITY_THRESHOLD):
        query_embedding = self.embedder.get_embedding(query)
        # SQL to find similar scenarios
```

## Usage Examples

### Storing New Content
```python
# Example: Storing a new teaching scenario
vector_ops = VectorOperations()
vector_ops.store_scenario(
    name="Classroom Disruption",
    description="Student interrupting lesson",
    expected_response="Address behavior calmly and professionally"
)
```

### Searching Similar Content
```python
# Example: Finding similar scenarios
similar_scenarios = vector_ops.find_similar_scenarios(
    query="How to handle student interruptions?",
    threshold=0.8
)
```

## Best Practices

### 1. Embedding Generation
- Use batch processing for multiple items
- Cache frequently used embeddings
- Handle text preprocessing consistently
- Implement error handling for embedding generation

### 2. Database Operations
- Use connection pooling
- Implement query timeouts
- Monitor index performance
- Regular maintenance (VACUUM ANALYZE)

### 3. Performance Optimization
```python
# Example: Batch processing
def batch_process_scenarios(scenarios, batch_size=BATCH_SIZE):
    for i in range(0, len(scenarios), batch_size):
        batch = scenarios[i:i + batch_size]
        embeddings = embedder.batch_get_embeddings([s.text for s in batch])
        # Bulk insert with embeddings
```

## Monitoring and Maintenance

### 1. Performance Metrics
- Track query response times
- Monitor embedding generation time
- Check index usage statistics
- Measure similarity search accuracy

### 2. Regular Maintenance
```sql
-- Regular maintenance tasks
VACUUM ANALYZE scenarios;
VACUUM ANALYZE interactions;
VACUUM ANALYZE feedback_templates;

-- Update statistics
ANALYZE scenarios;
ANALYZE interactions;
ANALYZE feedback_templates;
```

### 3. Error Handling
```python
class VectorStorageError(Exception):
    """Base class for vector storage errors"""
    pass

class EmbeddingError(VectorStorageError):
    """Raised when embedding generation fails"""
    pass

class SearchError(VectorStorageError):
    """Raised when vector search fails"""
    pass
```

## Integration Guidelines

### 1. For AI/ML Developers
- Use the standard EmbeddingGenerator class
- Follow batch processing guidelines
- Implement proper error handling
- Monitor embedding quality

### 2. For Content Specialists
- Use provided interfaces for content storage
- Follow text preprocessing guidelines
- Validate embedding results
- Report unusual similarity scores

### 3. For QA Specialists
- Test vector operations thoroughly
- Validate similarity search results
- Monitor performance metrics
- Document edge cases 