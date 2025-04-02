#!/bin/bash

# Check if PostgreSQL is installed
if ! [ -x "$(command -v psql)" ]; then
  echo "Error: PostgreSQL is not installed" >&2
  echo "Installing PostgreSQL..."
  apt-get update
  apt-get install -y postgresql postgresql-contrib
  
  # Start PostgreSQL service
  # In Docker, you may need to use service command instead
  service postgresql start
fi

# Check PostgreSQL status
pg_isready || { echo "PostgreSQL is not running"; exit 1; }

# Try as current user first (for Docker environments)
createuser -s postgres 2>/dev/null || echo "Postgres user already exists or could not be created"

# Use postgres user for the following commands
su - postgres -c "psql -c \"SELECT pg_terminate_backend(pg_stat_activity.pid) 
    FROM pg_stat_activity 
    WHERE pg_stat_activity.datname = 'teacher_chatbot_database' 
    AND pid <> pg_backend_pid();\""

su - postgres -c "psql -c \"DROP DATABASE IF EXISTS teacher_chatbot_database;\""

# Drop user if exists and recreate
su - postgres -c "psql -c \"DROP USER IF EXISTS teacher_chatbot_user;\""
su - postgres -c "psql -c \"CREATE USER teacher_chatbot_user WITH PASSWORD 'team4ai';\""

# Create database
su - postgres -c "createdb teacher_chatbot_database"

# Grant privileges
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE teacher_chatbot_database TO teacher_chatbot_user;\""

# Check if the dump file exists
if [ -f "/workspace/scripts/setup/database_dump.sql" ]; then
    # Load the database dump
    su - postgres -c "psql -d teacher_chatbot_database -f /workspace/scripts/setup/database_dump.sql"
    echo "Database dump loaded successfully"
else
    echo "Warning: database_dump.sql not found. Creating empty database."
    # Create empty tables if needed
fi

echo "Database setup completed successfully"
