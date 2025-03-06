"""
Testing Configuration Module for Teacher Training Chatbot

This module contains test-specific configuration settings, inheriting from
the base configuration and overriding values for the testing environment.
Focuses on isolation and reproducibility of tests.
"""

from .base import *
import tempfile

# Use temporary directories for test data
TEMP_DIR = Path(tempfile.mkdtemp(prefix="teacher_bot_test_"))
DATA_DIR = TEMP_DIR / "data"
LOGS_DIR = TEMP_DIR / "logs"

# Ensure test directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Test Database Configuration
DATABASE_CONFIG.update({
    "database": "teacher_bot_test",
    "username": "test_user",
    "password": "test_password",
    "host": "localhost",
    "port": 5432,
    "min_connections": 1,
    "max_connections": 5
})

# Test API Configuration
API_CONFIG.update({
    "debug": True,
    "testing": True,
    "port": 8001
})

# Test Model Configuration
MODEL_CONFIG.update({
    "embedding_model": "all-MiniLM-L6-v2",  # Use smaller model for tests
    "max_context_length": 1024,
    "temperature": 0.0  # Deterministic outputs for testing
})

# Minimal Logging for Tests
LOGGING_CONFIG.update({
    "root": {
        "level": "WARNING",
        "handlers": ["console"]
    },
    "handlers": {
        "file": {
            "filename": LOGS_DIR / "test.log"
        }
    }
})

# Disable Monitoring in Tests
MONITORING_CONFIG.update({
    "enabled": False
})

# Test Scenario Configuration
SCENARIO_CONFIG.update({
    "similarity_threshold": 0.5,  # More lenient for testing
    "max_results": 3,
    "cache_ttl": 60,  # Short cache for tests
    "batch_size": 5
})

# Test-specific Configurations
TEST_CONFIG = {
    "mock_responses": True,
    "use_fixtures": True,
    "cleanup_after": True,
    "async_timeout": 5,
    "retry_attempts": 1
}

def cleanup():
    """Clean up temporary test directories"""
    import shutil
    shutil.rmtree(TEMP_DIR, ignore_errors=True) 