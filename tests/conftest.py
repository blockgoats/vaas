import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import time

# Import your app and database components
from app.main import app
from db import Base, engine, SessionLocal
import models  # Import all models

# Test database URL
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vaasuser:vaaspass@localhost:5432/vaasdb")

# sqlalchemy.url = postgresql+psycopg2://vaasuser:vaaspass@localhost:5432/vaasdb


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    # Wait for database to be ready
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            test_engine = create_engine(TEST_DATABASE_URL)
            # Test the connection
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            break
        except Exception as e:
            print(f"Database connection failed (attempt {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            time.sleep(2)
    else:
        raise Exception("Could not connect to test database after maximum retries")
    
    return test_engine

@pytest.fixture(scope="session")
def test_db(test_engine):
    """Create test database tables."""
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Clean up - drop all tables
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_db):
    """Create a new database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    """Create a test client with database session dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override the database dependency
    app.dependency_overrides = {}
    from routers import teams, workspaces, users, databases, datasets, charts, dashboards, regions, clusters
    
    # Override database dependencies for all routers
    for router in [teams, workspaces, users, databases, datasets, charts, dashboards, regions, clusters]:
        if hasattr(router, 'get_db'):
            app.dependency_overrides[router.get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides = {}

@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return {
        "name": "Test Team",
        "description": "A test team for API testing",
        "region_id": 1
    }

@pytest.fixture
def sample_workspace_data():
    """Sample workspace data for testing."""
    return {
        "name": "Test Workspace",
        "description": "A test workspace for API testing",
        "team_id": 1
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "team_id": 1
    }

@pytest.fixture
def sample_database_data():
    """Sample database data for testing."""
    return {
        "name": "Test Database",
        "connection_string": "postgresql://test:test@localhost:5432/test",
        "workspace_id": 1
    } 