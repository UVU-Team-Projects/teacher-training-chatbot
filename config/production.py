"""
Production Configuration Module for Teacher Training Chatbot

This module contains production-specific configuration settings, inheriting
from the base configuration and overriding values for production environment.
Emphasizes security, performance, and stability.
"""

from .base import *
import os

# Secure Database Configuration for Production
DATABASE_CONFIG.update({
    "database": os.getenv("DB_NAME", "teacher_bot_prod"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "ssl_mode": "require",
    "min_connections": 10,
    "max_connections": 50
})

# Production API Configuration
API_CONFIG.update({
    "debug": False,
    "cors_origins": os.getenv("ALLOWED_ORIGINS", "").split(","),
    "rate_limit": {
        "requests": 100,
        "period": 60
    },
    "timeout": 60
})

# Production Model Configuration
MODEL_CONFIG.update({
    "temperature": 0.6,  # More conservative responses
    "cache_responses": True,
    "retry_attempts": 3
})

# Production Logging
LOGGING_CONFIG.update({
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"]
    },
    "handlers": {
        "file": {
            "filename": LOGS_DIR / "production.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    }
})

# Production Monitoring
MONITORING_CONFIG.update({
    "enabled": True,
    "port": int(os.getenv("METRICS_PORT", "8001")),
    "host": "localhost",  # Only allow local prometheus scraping
    "authentication": {
        "enabled": True,
        "token": os.getenv("METRICS_TOKEN")
    }
})

# Production Scenario Configuration
SCENARIO_CONFIG.update({
    "similarity_threshold": 0.75,  # Stricter matching
    "cache_ttl": 7200,  # 2 hours cache
    "max_batch_size": 50
})

# Security Configuration
SECURITY_CONFIG = {
    "ssl_cert": os.getenv("SSL_CERT_PATH"),
    "ssl_key": os.getenv("SSL_KEY_PATH"),
    "allowed_ips": os.getenv("ALLOWED_IPS", "").split(","),
    "rate_limiting": True,
    "request_timeout": 30,
    "max_content_length": 1024 * 1024  # 1MB
} 