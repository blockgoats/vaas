---

# Preset API Local Clone

This project provides a local development environment for a Preset-like API using FastAPI and PostgreSQL.

---

## Features

- Teams, Users, Workspaces with full CRUD
- Users belong to Teams
- Workspaces belong to Teams
- Many-to-many Workspace Memberships (users can join multiple workspaces, with a role)
- Only team members can join a workspace
- Workspace membership roles (e.g., member, admin)
- All endpoints documented and browsable at `/docs`

---

## Data Model Overview

- **Team**: Has many users and workspaces
- **User**: Belongs to a team, can be a member of many workspaces
- **Workspace**: Belongs to a team, can have many users (via memberships)
- **WorkspaceMembership**: Links users and workspaces, with a `role` (e.g., member, admin)

---

## API Endpoints

### Teams
- `POST /teams/` — Create a team
- `GET /teams/` — List all teams
- `GET /teams/{team_id}` — Get a team (with users and workspaces)
- `PUT /teams/{team_id}` — Update a team
- `DELETE /teams/{team_id}` — Delete a team

### Users
- `POST /users/` — Create a user (must specify `team_id`)
- `GET /users/` — List all users
- `GET /users/{user_id}` — Get a user
- `PUT /users/{user_id}` — Update a user
- `DELETE /users/{user_id}` — Delete a user
- `GET /users/by_team/{team_id}` — List users in a team

### Workspaces
- `POST /workspaces/` — Create a workspace (must specify `team_id`)
- `GET /workspaces/` — List all workspaces
- `GET /workspaces/{workspace_id}` — Get a workspace
- `PUT /workspaces/{workspace_id}` — Update a workspace
- `DELETE /workspaces/{workspace_id}` — Delete a workspace
- `GET /workspaces/by_team/{team_id}` — List workspaces in a team

### Workspace Memberships
- `POST /workspaces/{workspace_id}/memberships` — Add a user to a workspace (must be a team member, specify `user_id` and `role`)
- `DELETE /workspaces/{workspace_id}/memberships/{user_id}` — Remove a user from a workspace
- `GET /workspaces/{workspace_id}/memberships` — List all memberships (users) in a workspace
- `GET /workspaces/memberships/by_user/{user_id}` — List all workspace memberships for a user

Database Connections
POST /databases/ — Create a new database connection (assign to a workspace)
GET /databases/ — List all database connections
GET /databases/{db_id} — Get a database connection
PUT /databases/{db_id} — Update a database connection
DELETE /databases/{db_id} — Delete a database connection
POST /databases/{db_id}/test — Test the connection (mocked)
Datasets
POST /datasets/ — Register a new dataset (assign to a workspace and database)
GET /datasets/ — List all datasets
GET /datasets/{dataset_id} — Get a dataset
PUT /datasets/{dataset_id} — Update a dataset
DELETE /datasets/{dataset_id} — Delete a dataset
Business Logic
Database connections and datasets are assigned to workspaces.
Datasets are linked to both a workspace and a database connection.
How to use:
Run docker-compose up --build
Use /databases and /datasets endpoints in http://localhost:8000/docs
You can now manage connections and datasets per workspace, just like in Superset!


Support for More Database Types
The /databases/ endpoints now validate the type field against a list of supported types: postgres, mysql, sqlite, oracle.
You can get the list of supported types via GET /databases/types.
2. Dataset Metadata (Columns & Metrics)
Models: DatasetColumn and DatasetMetric (each linked to a Dataset)
Endpoints for each dataset:
POST /datasets/{dataset_id}/columns — Add a column
GET /datasets/{dataset_id}/columns — List columns
PUT /datasets/columns/{column_id} — Update a column
DELETE /datasets/columns/{column_id} — Delete a column
POST /datasets/{dataset_id}/metrics — Add a metric
GET /datasets/{dataset_id}/metrics — List metrics
PUT /datasets/metrics/{metric_id} — Update a metric
DELETE /datasets/metrics/{metric_id} — Delete a metric
DatasetOut now includes columns and metrics.
How to use:
Run docker-compose up --build
Use /databases/types to see supported types
Use /datasets/{dataset_id}/columns and /datasets/{dataset_id}/metrics to manage dataset metadata

ou’ll need to add:
Chart: Represents a visualization, belongs to a dataset and a workspace.
Dashboard: Represents a dashboard, belongs to a workspace.
DashboardChart: Association table for many-to-many between dashboards and charts.
DashboardPermission: (optional) For dashboard-level sharing/permissions.
2. Pydantic Schemas
Add schemas for Chart, Dashboard, DashboardChart, and DashboardPermission.
3. Routers/Endpoints
CRUD for charts:
POST /charts/, GET /charts/, GET /charts/{id}, PUT /charts/{id}, DELETE /charts/{id}
CRUD for dashboards:
POST /dashboards/, GET /dashboards/, GET /dashboards/{id}, PUT /dashboards/{id}, DELETE /dashboards/{id}
Assign charts to dashboards:
POST /dashboards/{dashboard_id}/charts (add chart to dashboard)
DELETE /dashboards/{dashboard_id}/charts/{chart_id} (remove chart from dashboard)
List charts in a dashboard:
GET /dashboards/{dashboard_id}/charts
List dashboards in a workspace:
GET /dashboards/by_workspace/{workspace_id}
Dashboard sharing/permissions:
POST /dashboards/{dashboard_id}/permissions
GET /dashboards/{dashboard_id}/permissions
DELETE /dashboards/permissions/{permission_id}
4. Implementation Plan
A. Models
Chart: id, name, type, params (JSON), dataset_id (FK), workspace_id (FK)
Dashboard: id, name, workspace_id (FK)
DashboardChart: id, dashboard_id (FK), chart_id (FK)
DashboardPermission: id, dashboard_id (FK), user_id (FK), permission (str)
B. Schemas
ChartBase, ChartCreate, ChartUpdate, ChartOut
DashboardBase, DashboardCreate, DashboardUpdate, DashboardOut
DashboardChartBase, DashboardChartCreate, DashboardChartOut
DashboardPermissionBase, DashboardPermissionCreate, DashboardPermissionOut
C. Routers
/charts
/dashboards
/dashboards/{dashboard_id}/charts
/dashboards/{dashboard_id}/permissions



Charts
POST /charts/ — Create a chart (visualization)
GET /charts/ — List all charts
GET /charts/{chart_id} — Get a chart
PUT /charts/{chart_id} — Update a chart
DELETE /charts/{chart_id} — Delete a chart
2. Dashboards
POST /dashboards/ — Create a dashboard
GET /dashboards/ — List all dashboards
GET /dashboards/{dashboard_id} — Get a dashboard
PUT /dashboards/{dashboard_id} — Update a dashboard
DELETE /dashboards/{dashboard_id} — Delete a dashboard
3. Assign Charts to Dashboards
POST /dashboards/{dashboard_id}/charts?chart_id=... — Add a chart to a dashboard
DELETE /dashboards/{dashboard_id}/charts/{chart_id} — Remove a chart from a dashboard
GET /dashboards/{dashboard_id}/charts — List charts in a dashboard
4. List Dashboards by Workspace
GET /dashboards/by_workspace/{workspace_id} — List dashboards in a workspace
5. Dashboard Sharing & Permissions
POST /dashboards/{dashboard_id}/permissions — Grant a permission (e.g., "view", "edit", "admin") to a user for a dashboard
GET /dashboards/{dashboard_id}/permissions — List all permissions for a dashboard
DELETE /dashboards/permissions/{permission_id} — Revoke a permission

Assign charts to dashboards, and dashboards to workspaces



Generating and managing embedded tokens for dashboards/charts
Enabling/disabling embedded mode for dashboards
Setting allowed domains for embedding
Here’s a step-by-step plan:
1. Data Model
EmbeddedConfig: Stores embedded settings for a dashboard (dashboard_id, enabled, allowed_domains).
(Optional) EmbeddedToken: Stores issued tokens for dashboards/charts (token, dashboard_id/chart_id, user info, expiry).
2. Schemas
EmbeddedConfigBase, EmbeddedConfigCreate, EmbeddedConfigUpdate, EmbeddedConfigOut
EmbeddedTokenCreate, EmbeddedTokenOut
3. Routers/Endpoints
POST /embedded/dashboard/{dashboard_id}/enable — Enable embedded mode and set allowed domains
POST /embedded/dashboard/{dashboard_id}/disable — Disable embedded mode
GET /embedded/dashboard/{dashboard_id}/config — Get embedded config for a dashboard
POST /embedded/dashboard/{dashboard_id}/token — Generate an embedded token for a dashboard
(Optional) POST /embedded/chart/{chart_id}/token — Generate an embedded token for a chart
4. Implementation Plan
A. Models
EmbeddedConfig: id, dashboard_id (FK), enabled (bool), allowed_domains (comma-separated string or JSON)
EmbeddedToken: id, token, dashboard_id/chart_id, user info, expiry
B. Schemas
EmbeddedConfigBase, EmbeddedConfigCreate, EmbeddedConfigUpdate, EmbeddedConfigOut
EmbeddedTokenCreate, EmbeddedTokenOut
C. Routers
/embedded/dashboard/{dashboard_id}/enable
/embedded/dashboard/{dashboard_id}/disable
/embedded/dashboard/{dashboard_id}/config
/embedded/dashboard/{dashboard_id}/token
(Optional) /embedded/chart/{chart_id}/token
Enable/Disable Embedded Mode & Set Allowed Domains
POST /embedded/dashboard/{dashboard_id}/enable — Enable embedded mode and set allowed domains (as JSON string or comma-separated)
POST /embedded/dashboard/{dashboard_id}/disable — Disable embedded mode
GET /embedded/dashboard/{dashboard_id}/config — Get embedded config for a dashboard
2. Generate and Manage Embedded Tokens
POST /embedded/dashboard/{dashboard_id}/token — Generate an embedded token for a dashboard (returns a UUID token, stores user info and expiry)
How to use:

1. Regions
POST /regions/ — Create a region (e.g., us-east-1)
GET /regions/ — List all regions
GET /regions/{region_id} — Get a region
PUT /regions/{region_id} — Update a region
DELETE /regions/{region_id} — Delete a region
2. Clusters (Private Cloud)
POST /clusters/ — Create a cluster (assign to a region)
GET /clusters/ — List all clusters
GET /clusters/{cluster_id} — Get a cluster
PUT /clusters/{cluster_id} — Update a cluster
DELETE /clusters/{cluster_id} — Delete a cluster
3. Workspaces
Workspaces can be assigned to a region and/or a cluster via region_id and cluster_id
GET /workspaces/by_region/{region_id} — List workspaces in a region
GET /workspaces/by_cluster/{cluster_id} — List workspaces in a cluster
How to use:
Run docker-compose up --build
Use /regions, /clusters, and /workspaces endpoints in http://localhost:8000/docs
When creating or updating a workspace, specify region_id and/or cluster_id
Next steps (optional):
Enforce region/cluster-based access control
Add region/cluster metadata to other resources (e.g., databases)
Add region/cluster filtering to more endpoints

yes

Superset and Redis have now been added to your docker-compose.yml:
Superset runs on port 8088 and uses the same Postgres database as your FastAPI app.
Redis is included as required by Superset.
Default Superset admin user:
username: admin
password: admin
How to Use
Run everything:
Apply to docker-compo...
Run
Access Superset at http://localhost:8088
Log in with admin / admin
Your FastAPI app and Superset now share the same database and can be integrated further via the Superset REST API.
Next Steps (Optional)
Call Superset’s API from FastAPI (for automation, dashboard/chart sync, etc.)
Automate user/workspace sync between your app and Superset
Add Superset API client code to your FastAPI app
Let me know if you want to see an example of calling the Superset API from FastAPI, or if you want to automate any specific workflow!
yes

Your docker-compose.yml is now fully set up to run:
FastAPI app (on port 8000)
Postgres database (shared by both app and Superset)
Redis (required by Superset)
Superset (on port 8088, with default admin user: admin / admin)
How to proceed:
Start all services:
Apply to docker-compo...
Run
Access your services:
FastAPI: http://localhost:8000
Superset: http://localhost:8088 (login: admin / admin)
Superset and your app now share the same Postgres database.
You can use Superset’s UI or REST API to manage dashboards, charts, etc.
You can automate Superset via its REST API from your FastAPI app if desired.
Next Steps (Optional)
Automate Superset via API:
If you want your FastAPI app to create dashboards, charts, or users in Superset automatically, let me know and I’ll show you how to call the Superset REST API from FastAPI.
Sync users/workspaces:
If you want to keep users/workspaces in sync between your app and Superset, I can help you automate that as well.
You’re ready to go!
Let me know if you want to see Superset API automation, or if you have another integration or feature in mind.
Call Superset’s API from FastAPI (for automation, dashboard/chart sync, etc.)
Automate user/workspace sync between your app and Superset
Add Superset API client code to your FastAPI app

Here’s how you can automate Superset from your FastAPI app:
1. Call Superset’s API from FastAPI
You can use Python’s requests library (or httpx) to call Superset’s REST API from your FastAPI endpoints.
Superset’s API docs: https://superset.apache.org/docs/rest-api/
Basic steps:
Authenticate to Superset (get a JWT access token)
Use the token to call Superset endpoints (e.g., create dashboard, chart, user, etc.)
2. Automate User/Workspace Sync
When you create a user/workspace in your app, also create it in Superset via the API.
You can do this in your FastAPI endpoint logic.
3. Add Superset API Client Code to FastAPI
Here’s a minimal example of a Superset API client in FastAPI:
Apply to docker-compo...
4. How to Use in FastAPI
Place the above code in a superset_client.py file in your app.
Import and call these functions from your FastAPI endpoints (e.g., after user/workspace creation).
5. Automate Workspace Sync Example
Apply to docker-compo...
6. Docker Networking Note
If you call Superset from FastAPI inside Docker Compose, use http://superset:8088.
If you call from outside Docker, use http://localhost:8088.
7. Next Steps
Add more client functions for dashboards, charts, etc.
Call these functions from your FastAPI endpoints as needed.
Would you like me to:
Add a superset_client.py to your app with these functions?
Show a full example of user/workspace sync in a FastAPI endpoint?
Both?
Let me know and I’ll implement the next step!
both

You now have:
1. Superset API Client (superset_client.py)
Functions to:
Get a Superset access token
Create a user in Superset
Create a database (workspace) in Superset
2. Automated User/Workspace Sync
When you create a user in your FastAPI app, it also creates the user in Superset (best effort, logs warning if it fails).
When you create a workspace in your FastAPI app, it also creates a Superset database (best effort, logs warning if it fails).

Add More Superset API Automation (Dashboards, Charts, Roles)
Add functions to your superset_client.py for:
Creating dashboards
Creating charts
Assigning roles to users
Updating and deleting dashboards/charts
2. Handle Superset Errors Robustly
Use retries (e.g., with tenacity or a custom retry loop) for transient errors.
Return or log status reporting (success/failure, error details).
Optionally, raise FastAPI HTTP errors if Superset sync is critical.
3. Sync Deletions/Updates as Well as Creations
When you update or delete a user/workspace in your app, also update/delete in Superset.
Add update/delete functions to your Superset client and call them from your FastAPI endpoints.
Step-by-Step Implementation
A. Extend superset_client.py
I’ll add:
create_superset_dashboard
update_superset_dashboard
delete_superset_dashboard
create_superset_chart
update_superset_chart
delete_superset_chart
assign_superset_role
Robust error handling with retries
B. Update FastAPI Endpoints
Call the appropriate Superset client functions on update/delete as well as create.
Log or return status of Superset sync.
Let’s star
---

## Business Logic

- **Only users whose `team_id` matches the workspace's `team_id` can be added as members.**
- **Workspace membership requires a `role` (e.g., `member`, `admin`).**

---

## Example Requests

### Create a Team
```json
POST /teams/
{
  "name": "Engineering"
}
```

### Create a User
```json
POST /users/
{
  "email": "alice@example.com",
  "name": "Alice",
  "team_id": 1
}
```

### Create a Workspace
```json
POST /workspaces/
{
  "name": "Data Science",
  "team_id": 1
}
```

### Add a User to a Workspace
```json
POST /workspaces/1/memberships
{
  "user_id": 1,
  "workspace_id": 1,
  "role": "admin"
}
```

---

## API Documentation

Interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Extending

- Add more fields to models as needed
- Add authentication, permissions, or invite logic
- See `app/` for all routers and models

---

Let me know if you want this in a different format, or if you want to add more usage examples or details!

---

## 1. **A Real Test Case for Dynamic Dashboard Creation**
- File: `tests/test_database_dashboard.py`
- Uses `pytest` and FastAPI’s `TestClient`
- Mocks Superset API client functions so the test is isolated and fast

---

## 2. **Test Scenario**
- When a user imports a database via the API, the system (mock) creates a Superset database and a dynamic dashboard.
- The test checks that the database is created in your app and that the dashboard creation logic is triggered (via the mock).

---

## 3. **How to Run the Test**
```bash
<code_block_to_apply_changes_from>
```

---

## 4. **How to Extend**
- You can add assertions for logs, or (with a real Superset instance) check the Superset API for the new dashboard.
- You can add similar tests for update/delete sync, or for other Superset resources.

---

**You now have a robust, automated test for this scenario!  
Let me know if you want to see more test examples, or need help with real Superset API integration tests.**
  
## Airflow Integration

The VaaS platform now includes comprehensive Apache Airflow integration for data pipeline orchestration and workflow management.

### Airflow Features

#### 1. **DAG Management**
- Create, update, and delete DAGs (Directed Acyclic Graphs)
- Schedule pipelines with various intervals (@daily, @hourly, @weekly, cron expressions)
- Pause/unpause DAGs for maintenance or debugging
- Monitor DAG execution status and history

#### 2. **Task Management**
- Define tasks with different operators (PythonOperator, BashOperator, etc.)
- Configure task parameters and dependencies
- Track task execution logs and performance metrics
- Handle task retries and error recovery

#### 3. **Connection Management**
- Manage database connections (PostgreSQL, MySQL, Oracle, etc.)
- Configure external service connections (APIs, cloud services)
- Store connection credentials securely
- Test connection validity

#### 4. **Pipeline Orchestration**
- ETL (Extract, Transform, Load) workflows
- Data quality monitoring pipelines
- Scheduled reporting and analytics
- Real-time data processing workflows

#### 5. **Monitoring and Alerting**
- Real-time DAG and task monitoring
- Execution history and performance metrics
- Error tracking and alerting
- Resource utilization monitoring

### Airflow API Endpoints

#### DAG Management
```bash
# Create a new DAG
POST /airflow/dags
{
  "dag_id": "sales_etl_pipeline",
  "description": "ETL pipeline for sales data",
  "schedule_interval": "@daily",
  "is_active": true,
  "workspace_id": 1
}

# Get all DAGs
GET /airflow/dags

# Get specific DAG
GET /airflow/dags/{dag_id}

# Update DAG
PUT /airflow/dags/{dag_id}

# Delete DAG
DELETE /airflow/dags/{dag_id}

# Trigger DAG execution
POST /airflow/dags/{dag_id}/trigger
```

#### Task Management
```bash
# Create a new task
POST /airflow/tasks
{
  "task_id": "extract_sales_data",
  "task_type": "python",
  "operator": "PythonOperator",
  "code": "print('Extracting sales data...')",
  "parameters": "{\"source\": \"sales_db\"}",
  "dag_id": 1
}

# Get all tasks
GET /airflow/tasks

# Get specific task
GET /airflow/tasks/{task_id}

# Update task
PUT /airflow/tasks/{task_id}

# Delete task
DELETE /airflow/tasks/{task_id}
```

#### Connection Management
```bash
# Create a new connection
POST /airflow/connections
{
  "name": "postgres_production",
  "connection_type": "postgres",
  "host": "postgres-server",
  "port": 5432,
  "username": "user",
  "password": "pass",
  "database": "production_db",
  "extra": "{\"sslmode\": \"require\"}",
  "workspace_id": 1
}

# Get all connections
GET /airflow/connections

# Get specific connection
GET /airflow/connections/{connection_id}

# Update connection
PUT /airflow/connections/{connection_id}

# Delete connection
DELETE /airflow/connections/{connection_id}
```

#### DAG Run Management
```bash
# Create a new DAG run
POST /airflow/dag-runs
{
  "run_id": "manual_20240101_120000",
  "state": "running",
  "execution_date": "2024-01-01T12:00:00",
  "dag_id": 1
}

# Get all DAG runs
GET /airflow/dag-runs

# Get specific DAG run
GET /airflow/dag-runs/{dag_run_id}

# Update DAG run
PUT /airflow/dag-runs/{dag_run_id}
```

#### Task Instance Management
```bash
# Create a new task instance
POST /airflow/task-instances
{
  "task_id": "extract_data",
  "state": "success",
  "start_date": "2024-01-01T12:00:00",
  "end_date": "2024-01-01T12:01:00",
  "duration": 60,
  "log": "Task completed successfully",
  "dag_run_id": 1,
  "task_id_ref": 1
}

# Get all task instances
GET /airflow/task-instances

# Get specific task instance
GET /airflow/task-instances/{task_instance_id}

# Update task instance
PUT /airflow/task-instances/{task_instance_id}
```

#### Workspace Integration
```bash
# Get all DAGs for a workspace
GET /airflow/workspaces/{workspace_id}/dags

# Get all connections for a workspace
GET /airflow/workspaces/{workspace_id}/connections
```

### Sample DAG Workflows

#### 1. **ETL Pipeline**
```python
# Sample ETL DAG for sales data processing
dag_data = {
    "dag_id": "sales_etl_pipeline",
    "description": "ETL pipeline for sales data processing",
    "schedule_interval": "@daily",
    "is_active": True,
    "workspace_id": 1
}

# Tasks for the ETL pipeline
tasks = [
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
        "dag_id": dag_id
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
        "dag_id": dag_id
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
        "dag_id": dag_id
    }
]
```

#### 2. **Data Quality Pipeline**
```python
# Sample data quality monitoring DAG
dq_dag_data = {
    "dag_id": "data_quality_check",
    "description": "Data quality monitoring pipeline",
    "schedule_interval": "@hourly",
    "is_active": True,
    "workspace_id": 1
}

# Data quality tasks
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
        "dag_id": dq_dag_id
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
        "dag_id": dq_dag_id
    }
]
```

### Airflow Services

The platform includes the following Airflow services:

1. **Airflow Webserver** (Port 8080)
   - Web UI for DAG management and monitoring
   - REST API for programmatic access
   - User authentication and authorization

2. **Airflow Scheduler**
   - Monitors DAG files and triggers executions
   - Manages task dependencies and scheduling
   - Handles DAG parsing and validation

3. **Airflow Worker**
   - Executes tasks in parallel
   - Supports multiple task types and operators
   - Handles task retries and error recovery

4. **Redis** (Message Broker)
   - Queues tasks for worker execution
   - Stores task results and metadata
   - Enables distributed task execution

### Environment Variables

Configure Airflow with these environment variables:

```bash
# Airflow Configuration
AIRFLOW_URL=http://airflow-webserver:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow

# Database Configuration
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://vaasuser:vaaspass@localhost:5432/vaasdb

# Celery Configuration
AIRFLOW__CELERY__BROKER_URL=redis://:@redis:6379/0
AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://vaasuser:vaaspass@localhost:5432/vaasdb

# Security Configuration
AIRFLOW__CORE__FERNET_KEY=your_fernet_key_here
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### Testing Airflow Integration

Run the Airflow integration tests:

```bash
# Run all Airflow tests
pytest tests/test_airflow_integration.py -v

# Run specific test scenarios
pytest tests/test_airflow_integration.py::test_create_dag_workflow -v
pytest tests/test_airflow_integration.py::test_etl_pipeline_workflow -v
pytest tests/test_airflow_integration.py::test_data_quality_pipeline -v
```

### Monitoring and Observability

1. **DAG Monitoring**
   - Real-time DAG execution status
   - Task-level monitoring and logging
   - Performance metrics and resource usage

2. **Error Handling**
   - Automatic task retries with exponential backoff
   - Error logging and alerting
   - Failed task recovery mechanisms

3. **Resource Management**
   - Worker pool management
   - Resource allocation and scaling
   - Queue management and prioritization

4. **Security**
   - User authentication and authorization
   - Connection credential encryption
   - Audit logging and compliance

### Integration with Other Services

Airflow integrates seamlessly with other VaaS services:

1. **Database Integration**
   - Use workspace database connections in DAGs
   - Execute SQL tasks with database operators
   - Monitor database performance and health

2. **Superset Integration**
   - Trigger dashboard refreshes from Airflow
   - Update datasets and charts automatically
   - Monitor analytics pipeline execution

3. **Workspace Management**
   - Organize DAGs by workspace
   - Manage connections per workspace
   - Control access and permissions

### Best Practices

1. **DAG Design**
   - Keep DAGs focused and single-purpose
   - Use descriptive task and DAG names
   - Implement proper error handling and retries

2. **Resource Management**
   - Monitor worker pool utilization
   - Configure appropriate task timeouts
   - Use resource pools for different task types

3. **Security**
   - Encrypt sensitive connection credentials
   - Use least-privilege access controls
   - Regularly rotate passwords and keys

4. **Monitoring**
   - Set up comprehensive logging
   - Monitor DAG execution performance
   - Implement alerting for failures

5. **Testing**
   - Test DAGs in development environment
   - Validate task dependencies and schedules
   - Use mock data for testing

---
  # DAG Management
POST   /airflow/dags                    # Create DAG
GET    /airflow/dags                    # List all DAGs
GET    /airflow/dags/{dag_id}          # Get specific DAG
PUT    /airflow/dags/{dag_id}          # Update DAG
DELETE /airflow/dags/{dag_id}          # Delete DAG
POST   /airflow/dags/{dag_id}/trigger  # Trigger DAG execution

# Task Management
POST   /airflow/tasks                   # Create task
GET    /airflow/tasks                   # List all tasks
GET    /airflow/tasks/{task_id}        # Get specific task
PUT    /airflow/tasks/{task_id}        # Update task
DELETE /airflow/tasks/{task_id}        # Delete task

# Connection Management
POST   /airflow/connections             # Create connection
GET    /airflow/connections             # List all connections
GET    /airflow/connections/{conn_id}  # Get specific connection
PUT    /airflow/connections/{conn_id}  # Update connection
DELETE /airflow/connections/{conn_id}  # Delete connection

# Execution Monitoring
POST   /airflow/dag-runs               # Create DAG run
GET    /airflow/dag-runs               # List all DAG runs
GET    /airflow/dag-runs/{run_id}     # Get specific DAG run
PUT    /airflow/dag-runs/{run_id}     # Update DAG run

# Workspace Integration
GET    /airflow/workspaces/{ws_id}/dags        # Get workspace DAGs
GET    /airflow/workspaces/{ws_id}/connections # Get workspace connections

   psql -h localhost -U vaasuser -d vaasdb


   CREATE TABLE teams (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL UNIQUE
   ); 

   
   INSERT INTO teams (name) VALUES ('Test Team');# vaas
