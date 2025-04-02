"""
Base Configuration Module for Teacher Training Chatbot

This module contains base configuration settings that are common across all
environments (development, production, testing). Environment-specific configs
will inherit from this base.
"""

from pathlib import Path

# Project paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
SCENARIOS_DIR = DATA_DIR / "scenarios"
LOGS_DIR = ROOT_DIR / "logs"

# Ensure required directories exist
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Model Configuration
MODEL_CONFIG = {
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "llm_model": "llama2",
    "max_context_length": 2048,
    "temperature": 0.7
}

# Database Configuration Base
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "teacher_bot",
    "min_connections": 5,
    "max_connections": 20
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "timeout": 30,
    "cors_origins": ["*"]
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "enabled": True,
    "port": 8001,
    "log_level": "INFO",
    "metrics_path": "/metrics"
}

# Scenario Configuration
SCENARIO_CONFIG = {
    "similarity_threshold": 0.7,
    "max_results": 5,
    "cache_ttl": 3600,
    "batch_size": 32
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",
            "formatter": "standard"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    }
} 