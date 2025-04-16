# Database Documentation

## Overview

The Teacher Training Chatbot uses PostgreSQL with pgvector extension for both relational data storage and vector similarity search capabilities.

## Database Schema

### Tables

1. **scenarios**
   ```sql
   CREATE TABLE scenarios (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       description TEXT,
       expected_response TEXT NOT NULL,
       expected_response_embedding vector(384),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **interactions**
   ```sql
   CREATE TABLE interactions (
       id SERIAL PRIMARY KEY,
       scenario_id INTEGER REFERENCES scenarios(id),
       personality VARCHAR(255),
       tone VARCHAR(255),
       query TEXT NOT NULL,
       query_embedding vector(384),
       teacher_response TEXT,
       teacher_response_embedding vector(384),
       similarity_score FLOAT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

3. **teacher_profiles**
   ```sql
   CREATE TABLE teacher_profiles (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       subject_area VARCHAR(255),
       experience_level VARCHAR(50),
       style_embedding vector(384),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

4. **feedback_templates**
   ```sql
   CREATE TABLE feedback_templates (
       id SERIAL PRIMARY KEY,
       category VARCHAR(255) NOT NULL,
       template_text TEXT NOT NULL,
       min_similarity FLOAT,
       max_similarity FLOAT,
       template_embedding vector(384),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

## Vector Similarity Search

### Setting Up pgvector

1. Install the extension:
   ```sql
   CREATE EXTENSION vector;
   ```

2. Create vector columns:
   ```sql
   ALTER TABLE scenarios 
   ADD COLUMN expected_response_embedding vector(384);
   ```

3. Create vector indexes:
   ```sql
   CREATE INDEX ON scenarios 
   USING ivfflat (expected_response_embedding vector_cosine_ops)
   WITH (lists = 100);
   ```

### Example Queries

1. Find similar responses:
   ```sql
   SELECT id, name, expected_response,
          1 - (expected_response_embedding <=> query_vector) as similarity
   FROM scenarios
   ORDER BY expected_response_embedding <=> query_vector
   LIMIT 5;
   ```

2. Filter by similarity threshold:
   ```sql
   SELECT *
   FROM interactions
   WHERE similarity_score > 0.8
   ORDER BY created_at DESC;
   ```

## Database Operations

### Backup and Restore

1. Create backup:
   ```bash
   pg_dump -Fc chatbot > backup.dump
   ```

2. Restore from backup:
   ```bash
   pg_restore -d chatbot backup.dump
   ```

### Maintenance

1. Vacuum analyze:
   ```sql
   VACUUM ANALYZE scenarios;
   VACUUM ANALYZE interactions;
   ```

2. Reindex:
   ```sql
   REINDEX TABLE scenarios;
   REINDEX TABLE interactions;
   ```

## Performance Optimization

### Indexing Strategy

1. B-tree indexes:
   ```sql
   CREATE INDEX idx_scenarios_name ON scenarios(name);
   CREATE INDEX idx_interactions_created ON interactions(created_at);
   ```

2. Vector indexes:
   ```sql
   CREATE INDEX idx_scenarios_embedding ON scenarios 
   USING ivfflat (expected_response_embedding vector_cosine_ops);
   ```

### Query Optimization

1. Use prepared statements
2. Implement connection pooling
3. Regular VACUUM ANALYZE
4. Monitor and update statistics

## Security

### Access Control

1. Create roles:
   ```sql
   CREATE ROLE teacher_bot_app WITH LOGIN PASSWORD 'secure_password';
   ```

2. Grant permissions:
   ```sql
   GRANT SELECT, INSERT, UPDATE ON scenarios TO teacher_bot_app;
   GRANT SELECT, INSERT ON interactions TO teacher_bot_app;
   ```

### Data Protection

1. Column-level encryption
2. Regular security audits
3. Backup encryption
4. SSL connections

## Monitoring

### Key Metrics

1. Query performance
2. Index usage
3. Cache hit ratio
4. Connection count

### Logging

1. Slow queries
2. Error logs
3. Connection logs
4. Security events

## Development Guidelines

### Best Practices

1. Use migrations for schema changes
2. Follow naming conventions
3. Document all changes
4. Test queries in staging

### Common Patterns

1. Implementing soft deletes
2. Handling versioning
3. Managing transactions
4. Error handling 