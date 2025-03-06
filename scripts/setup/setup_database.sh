#!/bin/bash

# Terminate existing connections and drop database if it exists
sudo -u postgres psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) 
    FROM pg_stat_activity 
    WHERE pg_stat_activity.datname = 'teacher_chatbot_database' 
    AND pid <> pg_backend_pid();"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS teacher_chatbot_database;"

# Drop user if exists and recreate
sudo -u postgres psql -c "DROP USER IF EXISTS teacher_chatbot_user;"
sudo -u postgres psql -c "CREATE USER teacher_chatbot_user WITH PASSWORD 'team4ai';"

# Create database
sudo -u postgres createdb teacher_chatbot_database

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE teacher_chatbot_database TO teacher_chatbot_user;"

# Load the database dump
sudo -u postgres psql -d teacher_chatbot_database -f scripts/setup/database_dump.sql