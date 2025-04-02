"""
Configuration Initialization Module for Teacher Training Chatbot

This module handles the loading of appropriate configuration based on the
environment setting. It exports the configuration object used throughout
the application.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Determine environment
ENV = os.getenv("APP_ENV", "development").lower()

# Import appropriate config
if ENV == "production":
    from .production import *
elif ENV == "testing":
    from .testing import *
else:
    from .development import *

def get_config() -> Dict[str, Any]:
    """
    Get the current configuration dictionary.
    
    Returns:
        Dict[str, Any]: Complete configuration dictionary for current environment
    """
    return {
        "database": DATABASE_CONFIG,
        "api": API_CONFIG,
        "model": MODEL_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "scenario": SCENARIO_CONFIG,
        "logging": LOGGING_CONFIG,
        "environment": ENV,
        "paths": {
            "root": ROOT_DIR,
            "data": DATA_DIR,
            "logs": LOGS_DIR,
            "scenarios": SCENARIOS_DIR
        }
    }

# Create config instance
config = get_config()

__all__ = ['config', 'get_config', 'ENV'] 