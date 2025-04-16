# Vector Storage Operations Guide

## Database Setup

### 1. Enable pgvector Extension
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create vector similarity functions
CREATE OR REPLACE FUNCTION cosine_similarity(a vector, b vector) 
RETURNS float
AS $$
SELECT 1 - (a <=> b);
$$ LANGUAGE SQL IMMUTABLE STRICT PARALLEL SAFE;
```

### 2. Table Schemas
```sql
-- Scenarios table with vector embeddings
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    expected_response TEXT NOT NULL,
    scenario_embedding vector(384) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Interactions table with vector embeddings
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES scenarios(id),
    query TEXT NOT NULL,
    query_embedding vector(384) NOT NULL,
    response TEXT NOT NULL,
    similarity_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Feedback templates with vector embeddings
CREATE TABLE feedback_templates (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    template_text TEXT NOT NULL,
    template_embedding vector(384) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Indexes
```sql
-- Create HNSW indexes for fast similarity search
CREATE INDEX ON scenarios USING hnsw (scenario_embedding vector_cosine_ops);
CREATE INDEX ON interactions USING hnsw (query_embedding vector_cosine_ops);
CREATE INDEX ON feedback_templates USING hnsw (template_embedding vector_cosine_ops);
```

## Database Operations

### 1. Basic Operations
```python
# database/vector_ops.py
from typing import List, Dict
import numpy as np
from database.connection import get_db_connection

class VectorOperations:
    def __init__(self):
        self.conn = get_db_connection()
    
    async def store_scenario(self, name: str, description: str, 
                           expected_response: str, embedding: List[float]):
        query = """
        INSERT INTO scenarios (name, description, expected_response, scenario_embedding)
        VALUES ($1, $2, $3, $4)
        RETURNING id;
        """
        async with self.conn.cursor() as cur:
            scenario_id = await cur.fetchval(query, name, description, 
                                          expected_response, embedding)
            return scenario_id
    
    async def find_similar_scenarios(self, query_embedding: List[float], 
                                   threshold: float = 0.8, limit: int = 5):
        query = """
        SELECT id, name, description, expected_response,
               cosine_similarity(scenario_embedding, $1) as similarity
        FROM scenarios
        WHERE cosine_similarity(scenario_embedding, $1) > $2
        ORDER BY similarity DESC
        LIMIT $3;
        """
        async with self.conn.cursor() as cur:
            results = await cur.fetch(query, query_embedding, threshold, limit)
            return [dict(r) for r in results]
```

### 2. Batch Operations
```python
# database/batch_ops.py
async def batch_store_scenarios(scenarios: List[Dict]):
    query = """
    INSERT INTO scenarios (name, description, expected_response, scenario_embedding)
    SELECT * FROM unnest($1::text[], $2::text[], $3::text[], $4::vector[])
    RETURNING id;
    """
    names = [s['name'] for s in scenarios]
    descriptions = [s['description'] for s in scenarios]
    responses = [s['expected_response'] for s in scenarios]
    embeddings = [s['embedding'] for s in scenarios]
    
    async with conn.transaction():
        scenario_ids = await conn.fetch(query, names, descriptions, 
                                      responses, embeddings)
        return [r['id'] for r in scenario_ids]
```

### 3. Maintenance Operations
```python
# database/maintenance.py
async def reindex_vectors():
    queries = [
        "REINDEX INDEX scenarios_scenario_embedding_idx;",
        "REINDEX INDEX interactions_query_embedding_idx;",
        "REINDEX INDEX feedback_templates_template_embedding_idx;"
    ]
    async with conn.transaction():
        for query in queries:
            await conn.execute(query)

async def vacuum_analyze():
    queries = [
        "VACUUM ANALYZE scenarios;",
        "VACUUM ANALYZE interactions;",
        "VACUUM ANALYZE feedback_templates;"
    ]
    for query in queries:
        await conn.execute(query)
```

## Performance Optimization

### 1. Connection Pooling
```python
# database/connection.py
from asyncpg import create_pool
from config import DATABASE_URL, MIN_CONNECTIONS, MAX_CONNECTIONS

async def init_db_pool():
    return await create_pool(
        DATABASE_URL,
        min_size=MIN_CONNECTIONS,
        max_size=MAX_CONNECTIONS,
        command_timeout=60
    )

# Usage
pool = await init_db_pool()
async with pool.acquire() as conn:
    await conn.fetch("SELECT * FROM scenarios LIMIT 1")
```

### 2. Query Optimization
```python
# database/optimized_queries.py
# Use materialized view for frequently accessed scenarios
CREATE MATERIALIZED VIEW frequent_scenarios AS
SELECT s.*, 
       COUNT(i.id) as interaction_count,
       AVG(i.similarity_score) as avg_similarity
FROM scenarios s
LEFT JOIN interactions i ON s.id = i.scenario_id
GROUP BY s.id
HAVING COUNT(i.id) > 100;

# Refresh materialized view
REFRESH MATERIALIZED VIEW frequent_scenarios;
```

## Monitoring

### 1. Performance Metrics
```python
# monitoring/db_metrics.py
from prometheus_client import Histogram, Counter

DB_OPERATION_TIME = Histogram(
    'db_operation_seconds',
    'Time spent on database operations',
    ['operation_type']
)

VECTOR_SEARCH_TIME = Histogram(
    'vector_search_seconds',
    'Time spent on vector similarity search',
    ['index_type']
)

DB_ERRORS = Counter(
    'db_errors_total',
    'Number of database errors',
    ['error_type']
)
```

### 2. Health Checks
```python
# monitoring/health_checks.py
async def check_vector_indexes():
    query = """
    SELECT schemaname, tablename, indexname, indexdef
    FROM pg_indexes
    WHERE indexdef LIKE '%vector_cosine_ops%';
    """
    async with pool.acquire() as conn:
        indexes = await conn.fetch(query)
        return {
            'status': 'healthy' if len(indexes) == 3 else 'degraded',
            'indexes': [dict(idx) for idx in indexes]
        }
```

## Error Handling

### 1. Common Errors
```python
# database/error_handling.py
class VectorDBError(Exception):
    """Base class for vector database errors"""
    pass

class EmbeddingDimensionError(VectorDBError):
    """Raised when embedding dimension doesn't match schema"""
    pass

class SimilaritySearchError(VectorDBError):
    """Raised when similarity search fails"""
    pass

async def safe_vector_operation(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncpg.exceptions.DataError as e:
            if "vector dimension" in str(e):
                raise EmbeddingDimensionError(str(e))
            raise VectorDBError(str(e))
        except Exception as e:
            raise VectorDBError(f"Unexpected error: {str(e)}")
    return wrapper
```

### 2. Recovery Procedures
```python
# database/recovery.py
async def recover_vector_indexes():
    """Recover from corrupted vector indexes"""
    try:
        await reindex_vectors()
        await vacuum_analyze()
        return {'status': 'success', 'message': 'Indexes recovered successfully'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
``` 