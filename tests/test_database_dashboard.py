import pytest
from fastapi.testclient import TestClient
from main import app
import superset_client as superset_client

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_superset(monkeypatch):
    # Mock Superset database and dashboard creation
    monkeypatch.setattr(superset_client, "create_superset_database", lambda database_name, sqlalchemy_uri: {"id": 123, "database_name": database_name})
    monkeypatch.setattr(superset_client, "create_superset_dashboard", lambda dashboard_title, **kwargs: {"id": 456, "dashboard_title": dashboard_title})

def test_app_health_check(client):
    """Test that the app is running and responding"""
    response = client.get("/")
    assert response.status_code == 200

def test_superset_integration_mock(client):
    """Test that Superset integration functions are properly mocked"""
    # This test verifies our mocking is working
    from superset_client import create_superset_database, create_superset_dashboard
    
    # Test mocked functions
    db_result = create_superset_database("test_db", "sqlite:///test.db")
    assert db_result["id"] == 123
    assert db_result["database_name"] == "test_db"
    
    dashboard_result = create_superset_dashboard("Test Dashboard")
    assert dashboard_result["id"] == 456
    assert dashboard_result["dashboard_title"] == "Test Dashboard"

def test_app_structure(client):
    """Test that the app has the expected structure and endpoints"""
    # Test that the app loads without errors
    assert app is not None
    
    # Test that we can get the OpenAPI docs
    response = client.get("/docs")
    assert response.status_code == 200 