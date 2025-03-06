"""
Development Configuration Module for Teacher Training Chatbot

This module contains development-specific configuration settings, inheriting
from the base configuration and overriding values for development environment.
"""

from .base import *

# Override Database Configuration for Development
DATABASE_CONFIG.update({
    "database": "teacher_bot_dev",
    "username": "dev_user",
    "password": "dev_password",  # Note: Use environment variables in practice
})

# Enable Debug Mode
API_CONFIG.update({
    "debug": True,
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
})

# Development-specific Model Configuration
MODEL_CONFIG.update({
    "temperature": 0.8,  # More creative responses in development
    "max_context_length": 4096  # Larger context for debugging
})

# Enhanced Logging for Development
LOGGING_CONFIG["root"]["level"] = "DEBUG"
LOGGING_CONFIG["handlers"]["file"]["filename"] = LOGS_DIR / "dev.log"

# Development Monitoring Configuration
MONITORING_CONFIG.update({
    "debug": True,
    "log_level": "DEBUG"
})

# Development Scenario Configuration
SCENARIO_CONFIG.update({
    "similarity_threshold": 0.6,  # More lenient matching for testing
    "cache_ttl": 300  # Shorter cache time for development
}) 