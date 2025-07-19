from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.routers.db import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="team", cascade="all, delete-orphan")
    workspaces = relationship("Workspace", back_populates="team", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="users")
    workspace_memberships = relationship("WorkspaceMembership", back_populates="user", cascade="all, delete-orphan")

class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="workspaces")
    memberships = relationship("WorkspaceMembership", back_populates="workspace", cascade="all, delete-orphan")
    database_connections = relationship("DatabaseConnection", back_populates="workspace", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="workspace", cascade="all, delete-orphan")
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    region = relationship("Region", back_populates="workspaces")
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    cluster = relationship("Cluster", back_populates="workspaces")

class WorkspaceMembership(Base):
    __tablename__ = "workspace_memberships"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    role = Column(String, nullable=False, default="member")
    user = relationship("User", back_populates="workspace_memberships")
    workspace = relationship("Workspace", back_populates="memberships")

class DatabaseConnection(Base):
    __tablename__ = "database_connections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'postgres', 'mysql'
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)  # For demo only; encrypt in production
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    workspace = relationship("Workspace", back_populates="database_connections")
    datasets = relationship("Dataset", back_populates="database", cascade="all, delete-orphan")

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    schema = Column(String, nullable=True)
    table = Column(String, nullable=False)
    database_id = Column(Integer, ForeignKey("database_connections.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    database = relationship("DatabaseConnection", back_populates="datasets")
    workspace = relationship("Workspace", back_populates="datasets")

class DatasetColumn(Base):
    __tablename__ = "dataset_columns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    dataset = relationship("Dataset", back_populates="columns")

class DatasetMetric(Base):
    __tablename__ = "dataset_metrics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    expression = Column(String, nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    dataset = relationship("Dataset", back_populates="metrics")

class DatasetPermission(Base):
    __tablename__ = "dataset_permissions"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(String, nullable=False)  # e.g., 'read', 'write', 'admin'
    dataset = relationship("Dataset", back_populates="permissions")
    user = relationship("User", back_populates="dataset_permissions")

Dataset.columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
Dataset.metrics = relationship("DatasetMetric", back_populates="dataset", cascade="all, delete-orphan")
Dataset.permissions = relationship("DatasetPermission", back_populates="dataset", cascade="all, delete-orphan")
User.dataset_permissions = relationship("DatasetPermission", back_populates="user", cascade="all, delete-orphan") 

class Chart(Base):
    __tablename__ = "charts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    params = Column(String, nullable=True)  # JSON as string for simplicity
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    dataset = relationship("Dataset", back_populates="charts")
    workspace = relationship("Workspace", back_populates="charts")
    dashboards = relationship("DashboardChart", back_populates="chart", cascade="all, delete-orphan")

Dataset.charts = relationship("Chart", back_populates="dataset", cascade="all, delete-orphan")
Workspace.charts = relationship("Chart", back_populates="workspace", cascade="all, delete-orphan")

class Dashboard(Base):
    __tablename__ = "dashboards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    workspace = relationship("Workspace", back_populates="dashboards")
    charts = relationship("DashboardChart", back_populates="dashboard", cascade="all, delete-orphan")
    permissions = relationship("DashboardPermission", back_populates="dashboard", cascade="all, delete-orphan")

Workspace.dashboards = relationship("Dashboard", back_populates="workspace", cascade="all, delete-orphan")

class DashboardChart(Base):
    __tablename__ = "dashboard_charts"
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    chart_id = Column(Integer, ForeignKey("charts.id"), nullable=False)
    dashboard = relationship("Dashboard", back_populates="charts")
    chart = relationship("Chart", back_populates="dashboards")

class DashboardPermission(Base):
    __tablename__ = "dashboard_permissions"
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(String, nullable=False)  # e.g., 'view', 'edit', 'admin'
    dashboard = relationship("Dashboard", back_populates="permissions")
    user = relationship("User") 

class EmbeddedConfig(Base):
    __tablename__ = "embedded_configs"
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False, unique=True)
    enabled = Column(Integer, nullable=False, default=0)  # 0 = False, 1 = True
    allowed_domains = Column(String, nullable=True)  # Comma-separated or JSON string
    dashboard = relationship("Dashboard")

class EmbeddedToken(Base):
    __tablename__ = "embedded_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    user_info = Column(String, nullable=True)  # JSON string
    expiry = Column(String, nullable=True)  # ISO datetime as string
    dashboard = relationship("Dashboard") 

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    clusters = relationship("Cluster", back_populates="region", cascade="all, delete-orphan")
    workspaces = relationship("Workspace", back_populates="region")

class Cluster(Base):
    __tablename__ = "clusters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    region = relationship("Region", back_populates="clusters")
    workspaces = relationship("Workspace", back_populates="cluster")

# Airflow Models
class AirflowConnection(Base):
    __tablename__ = "airflow_connections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    connection_type = Column(String, nullable=False)  # e.g., 'postgres', 'mysql', 'http', 's3'
    host = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    database = Column(String, nullable=True)
    extra = Column(Text, nullable=True)  # JSON string for additional connection parameters
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    workspace = relationship("Workspace", back_populates="airflow_connections")

class DAG(Base):
    __tablename__ = "dags"
    id = Column(Integer, primary_key=True, index=True)
    dag_id = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    schedule_interval = Column(String, nullable=True)  # e.g., '@daily', '@hourly', '0 0 * * *'
    is_active = Column(Boolean, default=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    workspace = relationship("Workspace", back_populates="dags")
    tasks = relationship("Task", back_populates="dag", cascade="all, delete-orphan")
    runs = relationship("DAGRun", back_populates="dag", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, nullable=False)
    task_type = Column(String, nullable=False)  # e.g., 'python', 'bash', 'sql', 'http'
    operator = Column(String, nullable=False)  # e.g., 'PythonOperator', 'BashOperator', 'SqlOperator'
    code = Column(Text, nullable=True)  # Python code or SQL query
    parameters = Column(Text, nullable=True)  # JSON string for task parameters
    dag_id = Column(Integer, ForeignKey("dags.id"), nullable=False)
    dag = relationship("DAG", back_populates="tasks")
    instances = relationship("TaskInstance", back_populates="task", cascade="all, delete-orphan")

class DAGRun(Base):
    __tablename__ = "dag_runs"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, nullable=False)
    state = Column(String, nullable=False)  # e.g., 'running', 'success', 'failed', 'skipped'
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    execution_date = Column(DateTime, nullable=False)
    dag_id = Column(Integer, ForeignKey("dags.id"), nullable=False)
    dag = relationship("DAG", back_populates="runs")
    task_instances = relationship("TaskInstance", back_populates="dag_run", cascade="all, delete-orphan")

class TaskInstance(Base):
    __tablename__ = "task_instances"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, nullable=False)
    state = Column(String, nullable=False)  # e.g., 'running', 'success', 'failed', 'skipped'
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    log = Column(Text, nullable=True)  # Task execution log
    dag_run_id = Column(Integer, ForeignKey("dag_runs.id"), nullable=False)
    task_id_ref = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    dag_run = relationship("DAGRun", back_populates="task_instances")
    task = relationship("Task", back_populates="instances")

# Add relationships to existing models
Workspace.airflow_connections = relationship("AirflowConnection", back_populates="workspace", cascade="all, delete-orphan")
Workspace.dags = relationship("DAG", back_populates="workspace", cascade="all, delete-orphan") 