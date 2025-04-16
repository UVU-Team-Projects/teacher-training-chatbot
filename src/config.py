"""Configuration settings for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

def get_database_url(testing=False):
    """Get database URL based on environment."""
    if testing:
        return "postgresql://postgres:postgres@localhost:5432/chatbot_test"
    
    return os.getenv(
        'DATABASE_URL',
        "postgresql://postgres:postgres@localhost:5432/chatbot"
    )

class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_APP = 'src.web.app'
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PostgreSQL vector settings
    VECTOR_DIMENSION = 384  # Dimension for sentence-transformers embeddings
    
    # Llama model settings
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/llama-2-7b-chat.gguf')
    MODEL_N_CTX = int(os.getenv('MODEL_N_CTX', '2048'))
    MODEL_N_THREADS = int(os.getenv('MODEL_N_THREADS', '4'))
    MODEL_N_GPU_LAYERS = int(os.getenv('MODEL_N_GPU_LAYERS', '0'))
    
    # Application settings
    MAX_RESPONSE_TOKENS = 150
    SIMILARITY_THRESHOLD = 0.7
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = get_database_url(testing=True)

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Use production DB URL

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Active configuration
active_config = config[os.getenv('FLASK_ENV', 'default')] 