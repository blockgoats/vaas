import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Test Airflow DAG Management
def test_create_dag_workflow(client):
    """Test complete workflow: Create DAG → Add Tasks → Trigger Execution."""
    
    # Step 1: Create a workspace
    workspace_data = {
        "name": "Data Pipeline Workspace",
        "description": "Workspace for Airflow data pipelines",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Step 2: Create a DAG
        dag_data = {
            "dag_id": "test_data_pipeline",
            "description": "Test data pipeline for ETL workflow",
            "schedule_interval": "@daily",
            "is_active": True,
            "workspace_id": workspace_id
        }
        
        response = client.post("/airflow/dags", json=dag_data)
        assert response.status_code == 201
        dag = response.json()
        assert dag["dag_id"] == "test_data_pipeline"
        assert dag["workspace_id"] == workspace_id
        
        # Step 3: Add tasks to the DAG
        tasks_data = [
            {
                "task_id": "extract_data",
                "task_type": "python",
                "operator": "PythonOperator",
                "code": "print('Extracting data...')",
                "parameters": '{"param1": "value1"}',
                "dag_id": dag["id"]
            },
            {
                "task_id": "transform_data",
                "task_type": "python",
                "operator": "PythonOperator",
                "code": "print('Transforming data...')",
                "parameters": '{"param2": "value2"}',
                "dag_id": dag["id"]
            },
            {
                "task_id": "load_data",
                "task_type": "python",
                "operator": "PythonOperator",
                "code": "print('Loading data...')",
                "parameters": '{"param3": "value3"}',
                "dag_id": dag["id"]
            }
        ]
        
        for task_data in tasks_data:
            response = client.post("/airflow/tasks", json=task_data)
            assert response.status_code == 201
            task = response.json()
            assert task["task_id"] == task_data["task_id"]
            assert task["dag_id"] == dag["id"]
        
        # Step 4: Trigger the DAG
        response = client.post(f"/airflow/dags/{dag['id']}/trigger")
        assert response.status_code == 200
        trigger_result = response.json()
        assert "run_id" in trigger_result["message"]

def test_airflow_connection_management(client):
    """Test Airflow connection management workflow."""
    
    # Step 1: Create workspace
    workspace_data = {
        "name": "Airflow Connections Workspace",
        "description": "Workspace for managing Airflow connections",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Step 2: Create PostgreSQL connection
        postgres_connection = {
            "name": "postgres_production",
            "connection_type": "postgres",
            "host": "postgres-server",
            "port": 5432,
            "username": "postgres_user",
            "password": "postgres_pass",
            "database": "production_db",
            "extra": '{"sslmode": "require"}',
            "workspace_id": workspace_id
        }
        
        response = client.post("/airflow/connections", json=postgres_connection)
        assert response.status_code == 201
        connection = response.json()
        assert connection["name"] == "postgres_production"
        assert connection["connection_type"] == "postgres"
        
        # Step 3: Create MySQL connection
        mysql_connection = {
            "name": "mysql_analytics",
            "connection_type": "mysql",
            "host": "mysql-server",
            "port": 3306,
            "username": "mysql_user",
            "password": "mysql_pass",
            "database": "analytics_db",
            "extra": '{"charset": "utf8mb4"}',
            "workspace_id": workspace_id
        }
        
        response = client.post("/airflow/connections", json=mysql_connection)
        assert response.status_code == 201
        connection = response.json()
        assert connection["name"] == "mysql_analytics"
        assert connection["connection_type"] == "mysql"
        
        # Step 4: List workspace connections
        response = client.get(f"/airflow/workspaces/{workspace_id}/connections")
        assert response.status_code == 200
        connections = response.json()
        assert len(connections) == 2
        assert any(conn["name"] == "postgres_production" for conn in connections)
        assert any(conn["name"] == "mysql_analytics" for conn in connections)

def test_dag_monitoring_workflow(client):
    """Test DAG monitoring and execution tracking."""
    
    # Step 1: Create DAG with monitoring
    dag_data = {
        "dag_id": "monitoring_test_dag",
        "description": "DAG for testing monitoring capabilities",
        "schedule_interval": "@hourly",
        "is_active": True,
        "workspace_id": 1
    }
    
    response = client.post("/airflow/dags", json=dag_data)
    assert response.status_code == 201
    dag = response.json()
    
    # Step 2: Create DAG run
    dag_run_data = {
        "run_id": "manual_test_run",
        "state": "running",
        "execution_date": datetime.now().isoformat(),
        "dag_id": dag["id"]
    }
    
    response = client.post("/airflow/dag-runs", json=dag_run_data)
    assert response.status_code == 201
    dag_run = response.json()
    assert dag_run["run_id"] == "manual_test_run"
    assert dag_run["state"] == "running"
    
    # Step 3: Create task instances
    task_instances_data = [
        {
            "task_id": "extract_task",
            "state": "success",
            "start_date": datetime.now().isoformat(),
            "end_date": datetime.now().isoformat(),
            "duration": 30,
            "log": "Task completed successfully",
            "dag_run_id": dag_run["id"],
            "task_id_ref": 1
        },
        {
            "task_id": "transform_task",
            "state": "running",
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "duration": None,
            "log": "Task is currently running",
            "dag_run_id": dag_run["id"],
            "task_id_ref": 2
        }
    ]
    
    for task_instance_data in task_instances_data:
        response = client.post("/airflow/task-instances", json=task_instance_data)
        assert response.status_code == 201
        task_instance = response.json()
        assert task_instance["task_id"] == task_instance_data["task_id"]
        assert task_instance["state"] == task_instance_data["state"]
    
    # Step 4: Get DAG runs
    response = client.get(f"/airflow/dags/{dag['id']}/runs")
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) >= 1
    assert any(run["run_id"] == "manual_test_run" for run in runs)

def test_etl_pipeline_workflow(client):
    """Test complete ETL pipeline workflow with Airflow."""
    
    # Step 1: Create ETL workspace
    workspace_data = {
        "name": "ETL Pipeline Workspace",
        "description": "Workspace for ETL data pipelines",
        "team_id": 1
    }
    response = client.post("/workspaces/", json=workspace_data)
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace["id"]
        
        # Step 2: Create ETL DAG
        etl_dag_data = {
            "dag_id": "etl_sales_pipeline",
            "description": "ETL pipeline for sales data processing",
            "schedule_interval": "@daily",
            "is_active": True,
            "workspace_id": workspace_id
        }
        
        response = client.post("/airflow/dags", json=etl_dag_data)
        assert response.status_code == 201
        etl_dag = response.json()
        
        # Step 3: Add ETL tasks
        etl_tasks = [
            {
                "task_id": "extract_sales_data",
                "task_type": "python",
                "operator": "PythonOperator",
                "code": """
import pandas as pd
# Extract sales data from source
sales_data = pd.read_csv('/data/sales.csv')
print(f"Extracted {len(sales_data)} sales records")
""",
                "parameters": '{"source_path": "/data/sales.csv"}',
                "dag_id": etl_dag["id"]
            },
            {
                "task_id": "transform_sales_data",
                "task_type": "python",
                "operator": "PythonOperator",
                "code": """
import pandas as pd
# Transform sales data
sales_data['total_amount'] = sales_data['quantity'] * sales_data['unit_price']
sales_data['date'] = pd.to_datetime(sales_data['date'])
print("Sales data transformed successfully")
""",
                "parameters": '{"output_path": "/data/transformed_sales.csv"}',
                "dag_id": etl_dag["id"]
            },
            {
                "task_id": "load_sales_data",
                "task_type": "python",
                "operator": "PythonOperator",
                "code": """
import pandas as pd
# Load transformed data to warehouse
transformed_data = pd.read_csv('/data/transformed_sales.csv')
# Database connection and loading logic here
print("Sales data loaded to warehouse successfully")
""",
                "parameters": '{"warehouse_table": "sales_fact"}',
                "dag_id": etl_dag["id"]
            }
        ]
        
        for task_data in etl_tasks:
            response = client.post("/airflow/tasks", json=task_data)
            assert response.status_code == 201
        
        # Step 4: Trigger ETL pipeline
        response = client.post(f"/airflow/dags/{etl_dag['id']}/trigger")
        assert response.status_code == 200
        trigger_result = response.json()
        assert "ETL pipeline" in trigger_result["message"]

def test_data_quality_pipeline(client):
    """Test data quality monitoring pipeline."""
    
    # Step 1: Create data quality DAG
    dq_dag_data = {
        "dag_id": "data_quality_check",
        "description": "Data quality monitoring pipeline",
        "schedule_interval": "@hourly",
        "is_active": True,
        "workspace_id": 1
    }
    
    response = client.post("/airflow/dags", json=dq_dag_data)
    assert response.status_code == 201
    dq_dag = response.json()
    
    # Step 2: Add data quality tasks
    dq_tasks = [
        {
            "task_id": "check_data_completeness",
            "task_type": "python",
            "operator": "PythonOperator",
            "code": """
# Check for missing values
missing_count = df.isnull().sum().sum()
if missing_count > threshold:
    raise ValueError(f"Too many missing values: {missing_count}")
print("Data completeness check passed")
""",
            "parameters": '{"threshold": 100}',
            "dag_id": dq_dag["id"]
        },
        {
            "task_id": "check_data_consistency",
            "task_type": "python",
            "operator": "PythonOperator",
            "code": """
# Check data consistency rules
if not all(df['amount'] >= 0):
    raise ValueError("Negative amounts found")
print("Data consistency check passed")
""",
            "parameters": '{"rules": ["amount_positive"]}',
            "dag_id": dq_dag["id"]
        },
        {
            "task_id": "generate_quality_report",
            "task_type": "python",
            "operator": "PythonOperator",
            "code": """
# Generate data quality report
report = {
    "total_records": len(df),
    "missing_values": df.isnull().sum().to_dict(),
    "duplicates": df.duplicated().sum()
}
print("Quality report generated")
""",
            "parameters": '{"report_path": "/reports/quality_report.json"}',
            "dag_id": dq_dag["id"]
        }
    ]
    
    for task_data in dq_tasks:
        response = client.post("/airflow/tasks", json=task_data)
        assert response.status_code == 201

def test_scheduled_pipeline_management(client):
    """Test scheduled pipeline management and monitoring."""
    
    # Step 1: Create scheduled DAGs
    scheduled_dags = [
        {
            "dag_id": "hourly_data_sync",
            "description": "Hourly data synchronization",
            "schedule_interval": "@hourly",
            "is_active": True,
            "workspace_id": 1
        },
        {
            "dag_id": "daily_reporting",
            "description": "Daily reporting pipeline",
            "schedule_interval": "@daily",
            "is_active": True,
            "workspace_id": 1
        },
        {
            "dag_id": "weekly_aggregation",
            "description": "Weekly data aggregation",
            "schedule_interval": "@weekly",
            "is_active": True,
            "workspace_id": 1
        }
    ]
    
    created_dags = []
    for dag_data in scheduled_dags:
        response = client.post("/airflow/dags", json=dag_data)
        assert response.status_code == 201
        created_dags.append(response.json())
    
    # Step 2: Test DAG management operations
    for dag in created_dags:
        # Get DAG details
        response = client.get(f"/airflow/dags/{dag['id']}")
        assert response.status_code == 200
        dag_details = response.json()
        assert dag_details["dag_id"] == dag["dag_id"]
        
        # Update DAG (pause/unpause)
        update_data = {"is_active": False}
        response = client.put(f"/airflow/dags/{dag['id']}", json=update_data)
        assert response.status_code == 200
        updated_dag = response.json()
        assert updated_dag["is_active"] == False

def test_error_handling_and_recovery(client):
    """Test error handling and recovery mechanisms."""
    
    # Step 1: Create DAG with error-prone tasks
    error_dag_data = {
        "dag_id": "error_handling_test",
        "description": "DAG for testing error handling",
        "schedule_interval": "@daily",
        "is_active": True,
        "workspace_id": 1
    }
    
    response = client.post("/airflow/dags", json=error_dag_data)
    assert response.status_code == 201
    error_dag = response.json()
    
    # Step 2: Add tasks with different failure scenarios
    error_tasks = [
        {
            "task_id": "successful_task",
            "task_type": "python",
            "operator": "PythonOperator",
            "code": "print('Task completed successfully')",
            "parameters": '{}',
            "dag_id": error_dag["id"]
        },
        {
            "task_id": "retry_task",
            "task_type": "python",
            "operator": "PythonOperator",
            "code": """
import random
if random.random() < 0.5:
    raise Exception("Random failure for testing")
print("Task completed after retry")
""",
            "parameters": '{"retries": 3}',
            "dag_id": error_dag["id"]
        }
    ]
    
    for task_data in error_tasks:
        response = client.post("/airflow/tasks", json=task_data)
        assert response.status_code == 201
    
    # Step 3: Test error monitoring
    # Create failed task instance
    failed_task_instance = {
        "task_id": "failed_task",
        "state": "failed",
        "start_date": datetime.now().isoformat(),
        "end_date": datetime.now().isoformat(),
        "duration": 10,
        "log": "Task failed due to connection timeout",
        "dag_run_id": 1,
        "task_id_ref": 1
    }
    
    response = client.post("/airflow/task-instances", json=failed_task_instance)
    assert response.status_code == 201
    failed_instance = response.json()
    assert failed_instance["state"] == "failed"

def test_workspace_airflow_integration(client):
    """Test workspace-level Airflow integration."""
    
    # Step 1: Create multiple workspaces with different Airflow configurations
    workspaces = [
        {
            "name": "Production ETL",
            "description": "Production ETL pipelines",
            "team_id": 1
        },
        {
            "name": "Development Testing",
            "description": "Development and testing pipelines",
            "team_id": 1
        }
    ]
    
    created_workspaces = []
    for workspace_data in workspaces:
        response = client.post("/workspaces/", json=workspace_data)
        assert response.status_code in [201, 400]
        if response.status_code == 201:
            created_workspaces.append(response.json())
    
    # Step 2: Create DAGs for each workspace
    for workspace in created_workspaces:
        workspace_dag_data = {
            "dag_id": f"workspace_{workspace['id']}_pipeline",
            "description": f"Pipeline for workspace {workspace['name']}",
            "schedule_interval": "@daily",
            "is_active": True,
            "workspace_id": workspace["id"]
        }
        
        response = client.post("/airflow/dags", json=workspace_dag_data)
        assert response.status_code == 201
        
        # Verify DAG belongs to workspace
        dag = response.json()
        assert dag["workspace_id"] == workspace["id"]
        
        # Get workspace DAGs
        response = client.get(f"/airflow/workspaces/{workspace['id']}/dags")
        assert response.status_code == 200
        workspace_dags = response.json()
        assert len(workspace_dags) >= 1
        assert all(dag["workspace_id"] == workspace["id"] for dag in workspace_dags) 