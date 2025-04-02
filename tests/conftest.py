"""Test configuration and fixtures."""
import pytest
from src.web.app2 import app as flask_app
from src.database import Base, engine, Session

@pytest.fixture
def app():
    """Create application for the tests."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    
    # Create tables
    Base.metadata.create_all(engine)
    
    yield flask_app
    
    # Clean up
    Base.metadata.drop_all(engine)

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def db_session():
    """Create database session for tests."""
    session = Session()
    yield session
    session.close() 