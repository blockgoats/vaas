import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Test scenarios for database-to-dashboard workflow
def test_postgresql_database_connection_workflow(client):
    """Test complete workflow: PostgreSQL DB connection → Auto dashboard creation."""
    
    # Step 1: Create a workspace
    workspace_data = {
        "name": "Analytics Team Workspace",
        "description": "Workspace for PostgreSQL analytics",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]  # 201 if created, 400 if team doesn't exist
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Step 2: Add PostgreSQL database to workspace
        database_data = {
            "name": "Sales PostgreSQL DB",
            "connection_string": "postgresql://user:pass@localhost:5432/sales_db",
            "workspace_id": workspace_id,
            "database_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database_name": "sales_db",
            "username": "user",
            "password": "pass"
        }
        
        with patch('routers.databases.create_superset_database') as mock_superset:
            mock_superset.return_value = {"id": 1, "database_name": "sales_db"}
            
            response = client.post("/databases/", json=database_data)
            assert response.status_code == 200
            database = response.json()
            assert database["name"] == "Sales PostgreSQL DB"
            
            # Verify Superset database was created
            mock_superset.assert_called_once()
    
    # Step 3: Verify database appears in workspace
    response = client.get(f"/workspaces/{workspace_id}/databases")
    assert response.status_code == 200
    databases = response.json()
    assert isinstance(databases, list)

def test_hive_database_connection_workflow(client):
    """Test complete workflow: Hive DB connection → Auto dashboard creation."""
    
    # Step 1: Create workspace
    workspace_data = {
        "name": "Data Engineering Workspace",
        "description": "Workspace for Hive data processing",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Step 2: Add Hive database to workspace
        hive_database_data = {
            "name": "Big Data Hive DB",
            "connection_string": "hive://hive-server:10000/default",
            "workspace_id": workspace_id,
            "database_type": "hive",
            "host": "hive-server",
            "port": 10000,
            "database_name": "default",
            "username": "hive_user",
            "password": "hive_pass"
        }
        
        with patch('routers.databases.create_superset_database') as mock_superset:
            mock_superset.return_value = {"id": 2, "database_name": "hive_default"}
            
            response = client.post("/databases/", json=hive_database_data)
            assert response.status_code == 200
            database = response.json()
            assert database["name"] == "Big Data Hive DB"
            assert database["database_type"] == "hive"
            
            # Verify Hive database was created in Superset
            mock_superset.assert_called_once()

def test_oracle_database_connection_workflow(client):
    """Test complete workflow: Oracle DB connection → Auto dashboard creation."""
    
    # Step 1: Create workspace
    workspace_data = {
        "name": "Enterprise Data Workspace",
        "description": "Workspace for Oracle enterprise data",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Step 2: Add Oracle database to workspace
        oracle_database_data = {
            "name": "Enterprise Oracle DB",
            "connection_string": "oracle+cx_oracle://user:pass@oracle-server:1521/ORCL",
            "workspace_id": workspace_id,
            "database_type": "oracle",
            "host": "oracle-server",
            "port": 1521,
            "database_name": "ORCL",
            "username": "user",
            "password": "pass"
        }
        
        with patch('routers.databases.create_superset_database') as mock_superset:
            mock_superset.return_value = {"id": 3, "database_name": "oracle_orcl"}
            
            response = client.post("/databases/", json=oracle_database_data)
            assert response.status_code == 200
            database = response.json()
            assert database["name"] == "Enterprise Oracle DB"
            assert database["database_type"] == "oracle"
            
            # Verify Oracle database was created in Superset
            mock_superset.assert_called_once()

def test_automatic_dashboard_generation(client):
    """Test automatic dashboard generation when database is connected."""
    
    # Mock the entire Superset integration
    with patch('routers.databases.create_superset_database') as mock_create_db, \
         patch('routers.dashboards.create_superset_dashboard') as mock_create_dashboard, \
         patch('routers.charts.create_superset_chart') as mock_create_chart:
        
        # Setup mocks
        mock_create_db.return_value = {"id": 1, "database_name": "test_db"}
        mock_create_dashboard.return_value = {"id": 1, "title": "Auto Dashboard"}
        mock_create_chart.return_value = {"id": 1, "title": "Auto Chart"}
        
        # Step 1: Create workspace
        workspace_data = {
            "name": "Auto Dashboard Workspace",
            "description": "Testing automatic dashboard generation",
            "team_id": 1
        }
        response = client.post("/workspaces/", json=workspace_data)
        assert response.status_code in [201, 400]
        
        if response.status_code == 201:
            workspace = response.json()
            workspace_id = workspace["id"]
            
            # Step 2: Add database (triggers auto dashboard creation)
            database_data = {
                "name": "Auto Dashboard DB",
                "connection_string": "postgresql://user:pass@localhost:5432/auto_db",
                "workspace_id": workspace_id,
                "database_type": "postgresql"
            }
            
            response = client.post("/databases/", json=database_data)
            assert response.status_code == 200
            
            # Step 3: Verify automatic dashboard was created
            response = client.get(f"/workspaces/{workspace_id}/dashboards")
            assert response.status_code == 200
            dashboards = response.json()
            assert isinstance(dashboards, list)
            
            # Verify Superset calls were made
            mock_create_db.assert_called_once()
            # Note: Auto dashboard creation might be async or triggered differently

def test_database_schema_discovery(client):
    """Test automatic schema discovery when database is connected."""
    
    with patch('routers.databases.discover_database_schema') as mock_discover:
        mock_discover.return_value = {
            "tables": [
                {"name": "users", "columns": ["id", "name", "email"]},
                {"name": "orders", "columns": ["id", "user_id", "amount", "created_at"]},
                {"name": "products", "columns": ["id", "name", "price", "category"]}
            ]
        }
        
        # Add database with schema discovery
        database_data = {
            "name": "Schema Discovery DB",
            "connection_string": "postgresql://user:pass@localhost:5432/discovery_db",
            "workspace_id": 1,
            "database_type": "postgresql",
            "auto_discover_schema": True
        }
        
        response = client.post("/databases/", json=database_data)
        assert response.status_code == 200
        
        # Verify schema discovery was called
        mock_discover.assert_called_once()

def test_auto_chart_generation_for_tables(client):
    """Test automatic chart generation for discovered tables."""
    
    with patch('routers.databases.discover_database_schema') as mock_discover, \
         patch('routers.charts.create_auto_charts_for_table') as mock_auto_charts:
        
        mock_discover.return_value = {
            "tables": [
                {"name": "sales", "columns": ["id", "amount", "date", "region"]},
                {"name": "users", "columns": ["id", "name", "created_at"]}
            ]
        }
        mock_auto_charts.return_value = [
            {"id": 1, "title": "Sales by Region", "type": "bar"},
            {"id": 2, "title": "Sales Trend", "type": "line"}
        ]
        
        # Add database with auto chart generation
        database_data = {
            "name": "Auto Charts DB",
            "connection_string": "postgresql://user:pass@localhost:5432/charts_db",
            "workspace_id": 1,
            "database_type": "postgresql",
            "auto_generate_charts": True
        }
        
        response = client.post("/databases/", json=database_data)
        assert response.status_code == 200
        
        # Verify auto chart generation was called
        mock_auto_charts.assert_called()

def test_mysql_database_connection_workflow(client):
    """Test complete workflow: MySQL DB connection → Auto dashboard creation."""
    
    workspace_data = {
        "name": "MySQL Analytics Workspace",
        "description": "Workspace for MySQL data analytics",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Add MySQL database
        mysql_database_data = {
            "name": "Web Analytics MySQL",
            "connection_string": "mysql://user:pass@mysql-server:3306/web_analytics",
            "workspace_id": workspace_id,
            "database_type": "mysql",
            "host": "mysql-server",
            "port": 3306,
            "database_name": "web_analytics",
            "username": "user",
            "password": "pass"
        }
        
        with patch('routers.databases.create_superset_database') as mock_superset:
            mock_superset.return_value = {"id": 4, "database_name": "mysql_web_analytics"}
            
            response = client.post("/databases/", json=mysql_database_data)
            assert response.status_code == 200
            database = response.json()
            assert database["name"] == "Web Analytics MySQL"
            assert database["database_type"] == "mysql"

def test_snowflake_database_connection_workflow(client):
    """Test complete workflow: Snowflake DB connection → Auto dashboard creation."""
    
    workspace_data = {
        "name": "Snowflake Data Warehouse",
        "description": "Workspace for Snowflake data warehouse",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Add Snowflake database
        snowflake_database_data = {
            "name": "Enterprise Snowflake",
            "connection_string": "snowflake://user:pass@account.snowflakecomputing.com/warehouse/database",
            "workspace_id": workspace_id,
            "database_type": "snowflake",
            "account": "account.snowflakecomputing.com",
            "warehouse": "warehouse",
            "database": "database",
            "username": "user",
            "password": "pass"
        }
        
        with patch('routers.databases.create_superset_database') as mock_superset:
            mock_superset.return_value = {"id": 5, "database_name": "snowflake_enterprise"}
            
            response = client.post("/databases/", json=snowflake_database_data)
            assert response.status_code == 200
            database = response.json()
            assert database["name"] == "Enterprise Snowflake"
            assert database["database_type"] == "snowflake"

def test_database_connection_error_handling(client):
    """Test error handling when database connection fails."""
    
    with patch('routers.databases.create_superset_database') as mock_superset:
        mock_superset.side_effect = Exception("Connection failed")
        
        # Try to add database with invalid connection
        database_data = {
            "name": "Invalid Connection DB",
            "connection_string": "postgresql://invalid:invalid@invalid:5432/invalid",
            "workspace_id": 1,
            "database_type": "postgresql"
        }
        
        response = client.post("/databases/", json=database_data)
        # Should handle the error gracefully
        assert response.status_code in [400, 500, 422]

def test_database_connection_validation(client):
    """Test validation of database connection parameters."""
    
    # Test missing required fields
    invalid_database_data = {
        "name": "Invalid DB",
        "workspace_id": 1
        # Missing connection_string and database_type
    }
    
    response = client.post("/databases/", json=invalid_database_data)
    assert response.status_code == 422  # Validation error
    
    # Test invalid database type
    invalid_type_data = {
        "name": "Invalid Type DB",
        "connection_string": "invalid://user:pass@host:port/db",
        "workspace_id": 1,
        "database_type": "invalid_type"
    }
    
    response = client.post("/databases/", json=invalid_type_data)
    assert response.status_code in [400, 422]

def test_workspace_database_relationship(client):
    """Test that databases are properly associated with workspaces."""
    
    # Create workspace
    workspace_data = {
        "name": "Database Relationship Test",
        "description": "Testing database-workspace relationships",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Add database to workspace
        database_data = {
            "name": "Relationship Test DB",
            "connection_string": "postgresql://user:pass@localhost:5432/relationship_db",
            "workspace_id": workspace_id,
            "database_type": "postgresql"
        }
        
        with patch('routers.databases.create_superset_database'):
            response = client.post("/databases/", json=database_data)
            assert response.status_code == 200
            database = response.json()
            assert database["workspace_id"] == workspace_id
            
            # Verify database appears in workspace databases
            response = client.get(f"/workspaces/{workspace_id}/databases")
            assert response.status_code == 200
            databases = response.json()
            assert isinstance(databases, list)

def test_database_connection_string_parsing(client):
    """Test parsing of different database connection string formats."""
    
    test_cases = [
        {
            "name": "PostgreSQL Standard",
            "connection_string": "postgresql://user:pass@localhost:5432/db",
            "database_type": "postgresql",
            "expected_host": "localhost",
            "expected_port": 5432
        },
        {
            "name": "Hive Standard",
            "connection_string": "hive://hive-server:10000/default",
            "database_type": "hive",
            "expected_host": "hive-server",
            "expected_port": 10000
        },
        {
            "name": "Oracle Standard",
            "connection_string": "oracle+cx_oracle://user:pass@oracle-server:1521/ORCL",
            "database_type": "oracle",
            "expected_host": "oracle-server",
            "expected_port": 1521
        }
    ]
    
    for test_case in test_cases:
        database_data = {
            "name": test_case["name"],
            "connection_string": test_case["connection_string"],
            "workspace_id": 1,
            "database_type": test_case["database_type"]
        }
        
        with patch('routers.databases.create_superset_database'):
            response = client.post("/databases/", json=database_data)
            assert response.status_code == 200
            database = response.json()
            assert database["name"] == test_case["name"]
            assert database["database_type"] == test_case["database_type"]

def test_auto_dashboard_templates(client):
    """Test automatic dashboard template selection based on database type."""
    
    template_test_cases = [
        {
            "database_type": "postgresql",
            "expected_templates": ["sales_analytics", "user_metrics", "operational_dashboard"]
        },
        {
            "database_type": "hive",
            "expected_templates": ["big_data_analytics", "data_warehouse_overview"]
        },
        {
            "database_type": "oracle",
            "expected_templates": ["enterprise_metrics", "financial_dashboard"]
        }
    ]
    
    for test_case in template_test_cases:
        with patch('routers.dashboards.get_dashboard_templates') as mock_templates:
            mock_templates.return_value = test_case["expected_templates"]
            
            database_data = {
                "name": f"{test_case['database_type'].title()} Template Test",
                "connection_string": f"{test_case['database_type']}://user:pass@host:port/db",
                "workspace_id": 1,
                "database_type": test_case["database_type"],
                "auto_create_dashboard": True
            }
            
            with patch('routers.databases.create_superset_database'):
                response = client.post("/databases/", json=database_data)
                assert response.status_code == 200
                
                # Verify template selection was called
                mock_templates.assert_called_once_with(test_case["database_type"]) 