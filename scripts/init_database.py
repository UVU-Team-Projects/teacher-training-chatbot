#!/usr/bin/env python3

import asyncio
import asyncpg
from config.settings import DATABASE_URL

async def init_database():
    """Initialize the database with required extensions and tables"""
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create extensions
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        
        # Create tables
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS scenarios (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                expected_response TEXT NOT NULL,
                scenario_embedding vector(384) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id SERIAL PRIMARY KEY,
                scenario_id INTEGER REFERENCES scenarios(id),
                query TEXT NOT NULL,
                query_embedding vector(384) NOT NULL,
                response TEXT NOT NULL,
                similarity_score FLOAT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback_templates (
                id SERIAL PRIMARY KEY,
                category VARCHAR(100) NOT NULL,
                template_text TEXT NOT NULL,
                template_embedding vector(384) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Create indexes
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_scenarios_embedding 
            ON scenarios USING hnsw (scenario_embedding vector_cosine_ops)
            WITH (lists = 100);
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_interactions_query
            ON interactions USING hnsw (query_embedding vector_cosine_ops)
            WITH (lists = 100);
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_template
            ON feedback_templates USING hnsw (template_embedding vector_cosine_ops)
            WITH (lists = 100);
        ''')
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_database()) 