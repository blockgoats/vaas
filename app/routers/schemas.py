from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# WorkspaceMembership models
class WorkspaceMembershipBase(BaseModel):
    user_id: int
    workspace_id: int
    role: str

class WorkspaceMembershipCreate(WorkspaceMembershipBase):
    pass

class WorkspaceMembershipOut(WorkspaceMembershipBase):
    id: int
    class Config:
        orm_mode = True

# DatabaseConnection models
class DatabaseConnectionBase(BaseModel):
    name: str
    type: str
    host: str
    port: int
    username: str
    password: str
    workspace_id: int

class DatabaseConnectionCreate(DatabaseConnectionBase):
    pass

class DatabaseConnectionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    workspace_id: Optional[int] = None

class DatabaseConnectionOut(DatabaseConnectionBase):
    id: int
    class Config:
        orm_mode = True

# Dataset models and dependencies
class DatasetColumnBase(BaseModel):
    name: str
    type: str
    dataset_id: int

class DatasetColumnCreate(DatasetColumnBase):
    pass

class DatasetColumnUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    dataset_id: Optional[int] = None

class DatasetColumnOut(DatasetColumnBase):
    id: int
    class Config:
        orm_mode = True

class DatasetMetricBase(BaseModel):
    name: str
    expression: str
    dataset_id: int

class DatasetMetricCreate(DatasetMetricBase):
    pass

class DatasetMetricUpdate(BaseModel):
    name: Optional[str] = None
    expression: Optional[str] = None
    dataset_id: Optional[int] = None

class DatasetMetricOut(DatasetMetricBase):
    id: int
    class Config:
        orm_mode = True

class DatasetPermissionBase(BaseModel):
    dataset_id: int
    user_id: int
    permission: str

class DatasetPermissionCreate(DatasetPermissionBase):
    pass

class DatasetPermissionOut(DatasetPermissionBase):
    id: int
    class Config:
        orm_mode = True

class DatasetBase(BaseModel):
    name: str
    schema: Optional[str] = None
    table: str
    database_id: int
    workspace_id: int

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    schema: Optional[str] = None
    table: Optional[str] = None
    database_id: Optional[int] = None
    workspace_id: Optional[int] = None

class DatasetOut(DatasetBase):
    id: int
    columns: Optional[List[DatasetColumnOut]] = None
    metrics: Optional[List[DatasetMetricOut]] = None
    permissions: Optional[List[DatasetPermissionOut]] = None
    class Config:
        orm_mode = True

# Dashboard and Chart models and dependencies
class DashboardChartOut(BaseModel):
    id: int
    dashboard_id: int
    chart_id: int
    class Config:
        orm_mode = True

class DashboardPermissionBase(BaseModel):
    dashboard_id: int
    user_id: int
    permission: str

class DashboardPermissionCreate(DashboardPermissionBase):
    pass

class DashboardPermissionOut(DashboardPermissionBase):
    id: int
    class Config:
        orm_mode = True

class DashboardBase(BaseModel):
    name: str
    workspace_id: int

class DashboardCreate(DashboardBase):
    pass

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    workspace_id: Optional[int] = None

class DashboardOut(DashboardBase):
    id: int
    charts: Optional[list[DashboardChartOut]] = None
    permissions: Optional[list[DashboardPermissionOut]] = None
    class Config:
        orm_mode = True

class ChartBase(BaseModel):
    name: str
    type: str
    params: Optional[str] = None
    dataset_id: int
    workspace_id: int

class ChartCreate(ChartBase):
    pass

class ChartUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    params: Optional[str] = None
    dataset_id: Optional[int] = None
    workspace_id: Optional[int] = None

class ChartOut(ChartBase):
    id: int
    dashboards: Optional[list[DashboardChartOut]] = None
    class Config:
        orm_mode = True

# Now Workspace and User models
class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class UserBase(BaseModel):
    email: str
    name: str
    team_id: int

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    team_id: Optional[int] = None

class UserOut(UserBase):
    id: int
    workspace_memberships: Optional[List[WorkspaceMembershipOut]] = None
    class Config:
        orm_mode = True

class RegionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class RegionCreate(RegionBase):
    pass

class RegionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class RegionOut(RegionBase):
    id: int
    class Config:
        orm_mode = True

class ClusterBase(BaseModel):
    name: str
    description: Optional[str] = None
    region_id: int

class ClusterCreate(ClusterBase):
    pass

class ClusterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    region_id: Optional[int] = None

class ClusterOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    region_id: int

    class Config:
        from_attributes = True

# Airflow Schemas
class AirflowConnectionBase(BaseModel):
    name: str
    connection_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    extra: Optional[str] = None
    workspace_id: int

class AirflowConnectionCreate(AirflowConnectionBase):
    pass

class AirflowConnectionUpdate(BaseModel):
    name: Optional[str] = None
    connection_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    extra: Optional[str] = None

class AirflowConnectionOut(AirflowConnectionBase):
    id: int

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    task_id: str
    task_type: str
    operator: str
    code: Optional[str] = None
    parameters: Optional[str] = None
    dag_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    task_id: Optional[str] = None
    task_type: Optional[str] = None
    operator: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[str] = None

class TaskOut(TaskBase):
    id: int

    class Config:
        from_attributes = True

class DAGBase(BaseModel):
    dag_id: str
    description: Optional[str] = None
    schedule_interval: Optional[str] = None
    is_active: bool = True
    workspace_id: int

class DAGCreate(DAGBase):
    pass

class DAGUpdate(BaseModel):
    dag_id: Optional[str] = None
    description: Optional[str] = None
    schedule_interval: Optional[str] = None
    is_active: Optional[bool] = None

class DAGOut(DAGBase):
    id: int

    class Config:
        from_attributes = True

class DAGRunBase(BaseModel):
    run_id: str
    state: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    execution_date: datetime
    dag_id: int

class DAGRunCreate(DAGRunBase):
    pass

class DAGRunUpdate(BaseModel):
    run_id: Optional[str] = None
    state: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    execution_date: Optional[datetime] = None

class DAGRunOut(DAGRunBase):
    id: int

    class Config:
        from_attributes = True

class TaskInstanceBase(BaseModel):
    task_id: str
    state: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration: Optional[int] = None
    log: Optional[str] = None
    dag_run_id: int
    task_id_ref: int

class TaskInstanceCreate(TaskInstanceBase):
    pass

class TaskInstanceUpdate(BaseModel):
    task_id: Optional[str] = None
    state: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration: Optional[int] = None
    log: Optional[str] = None

class TaskInstanceOut(TaskInstanceBase):
    id: int

    class Config:
        from_attributes = True

class WorkspaceBase(BaseModel):
    name: str
    team_id: int
    region_id: Optional[int] = None
    cluster_id: Optional[int] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    team_id: Optional[int] = None
    region_id: Optional[int] = None
    cluster_id: Optional[int] = None

class WorkspaceOut(WorkspaceBase):
    id: int
    memberships: Optional[List[WorkspaceMembershipOut]] = None
    database_connections: Optional[List[DatabaseConnectionOut]] = None
    datasets: Optional[List[DatasetOut]] = None
    dashboards: Optional[List[DashboardOut]] = None
    charts: Optional[List[ChartOut]] = None
    region: Optional[RegionOut] = None
    cluster: Optional[ClusterOut] = None
    class Config:
        orm_mode = True

class TeamOut(TeamBase):
    id: int
    users: Optional[List[UserOut]] = None
    workspaces: Optional[List[WorkspaceOut]] = None
    class Config:
        orm_mode = True

class EmbeddedConfigBase(BaseModel):
    dashboard_id: int
    enabled: bool
    allowed_domains: Optional[str] = None  # JSON string or comma-separated

class EmbeddedConfigCreate(EmbeddedConfigBase):
    pass

class EmbeddedConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    allowed_domains: Optional[str] = None

class EmbeddedConfigOut(EmbeddedConfigBase):
    id: int
    class Config:
        orm_mode = True

class EmbeddedTokenCreate(BaseModel):
    dashboard_id: int
    user_info: Optional[str] = None
    expiry: Optional[str] = None

class EmbeddedTokenOut(BaseModel):
    id: int
    token: str
    dashboard_id: int
    user_info: Optional[str] = None
    expiry: Optional[str] = None
    class Config:
        orm_mode = True 