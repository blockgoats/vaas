from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import DAG, Task, DAGRun, TaskInstance, AirflowConnection, Workspace
from app.routers.schemas import (
    DAGCreate, DAGUpdate, DAGOut, 
    TaskCreate, TaskUpdate, TaskOut,
    DAGRunCreate, DAGRunUpdate, DAGRunOut,
    TaskInstanceCreate, TaskInstanceUpdate, TaskInstanceOut,
    AirflowConnectionCreate, AirflowConnectionUpdate, AirflowConnectionOut
)
from typing import List
import json
from datetime import datetime
import requests

router = APIRouter(prefix="/airflow", tags=["airflow"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Airflow Connection Management
@router.post("/connections", response_model=AirflowConnectionOut, status_code=status.HTTP_201_CREATED)
def create_airflow_connection(connection: AirflowConnectionCreate, db: Session = Depends(get_db)):
    """Create a new Airflow connection."""
    workspace = db.query(Workspace).filter(Workspace.id == connection.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="Workspace does not exist")
    
    db_connection = AirflowConnection(**connection.dict())
    db.add(db_connection)
    try:
        db.commit()
        db.refresh(db_connection)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Connection name must be unique")
    
    return db_connection

@router.get("/connections", response_model=List[AirflowConnectionOut])
def get_airflow_connections(db: Session = Depends(get_db)):
    """Get all Airflow connections."""
    return db.query(AirflowConnection).all()

@router.get("/connections/{connection_id}", response_model=AirflowConnectionOut)
def get_airflow_connection(connection_id: int, db: Session = Depends(get_db)):
    """Get a specific Airflow connection."""
    connection = db.query(AirflowConnection).filter(AirflowConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Airflow connection not found")
    return connection

@router.put("/connections/{connection_id}", response_model=AirflowConnectionOut)
def update_airflow_connection(connection_id: int, connection_update: AirflowConnectionUpdate, db: Session = Depends(get_db)):
    """Update an Airflow connection."""
    connection = db.query(AirflowConnection).filter(AirflowConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Airflow connection not found")
    
    for field, value in connection_update.dict(exclude_unset=True).items():
        setattr(connection, field, value)
    
    db.commit()
    db.refresh(connection)
    return connection

@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_airflow_connection(connection_id: int, db: Session = Depends(get_db)):
    """Delete an Airflow connection."""
    connection = db.query(AirflowConnection).filter(AirflowConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Airflow connection not found")
    
    db.delete(connection)
    db.commit()
    return None

# DAG Management
@router.post("/dags", response_model=DAGOut, status_code=status.HTTP_201_CREATED)
def create_dag(dag: DAGCreate, db: Session = Depends(get_db)):
    """Create a new DAG."""
    workspace = db.query(Workspace).filter(Workspace.id == dag.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="Workspace does not exist")
    
    db_dag = DAG(**dag.dict())
    db.add(db_dag)
    try:
        db.commit()
        db.refresh(db_dag)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="DAG ID must be unique")
    
    return db_dag

@router.get("/dags", response_model=List[DAGOut])
def get_dags(db: Session = Depends(get_db)):
    """Get all DAGs."""
    return db.query(DAG).all()

@router.get("/dags/{dag_id}", response_model=DAGOut)
def get_dag(dag_id: int, db: Session = Depends(get_db)):
    """Get a specific DAG."""
    dag = db.query(DAG).filter(DAG.id == dag_id).first()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")
    return dag

@router.put("/dags/{dag_id}", response_model=DAGOut)
def update_dag(dag_id: int, dag_update: DAGUpdate, db: Session = Depends(get_db)):
    """Update a DAG."""
    dag = db.query(DAG).filter(DAG.id == dag_id).first()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")
    
    for field, value in dag_update.dict(exclude_unset=True).items():
        setattr(dag, field, value)
    
    db.commit()
    db.refresh(dag)
    return dag

@router.delete("/dags/{dag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dag(dag_id: int, db: Session = Depends(get_db)):
    """Delete a DAG."""
    dag = db.query(DAG).filter(DAG.id == dag_id).first()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")
    
    db.delete(dag)
    db.commit()
    return None

# Task Management
@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    dag = db.query(DAG).filter(DAG.id == task.dag_id).first()
    if not dag:
        raise HTTPException(status_code=400, detail="DAG does not exist")
    
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks", response_model=List[TaskOut])
def get_tasks(db: Session = Depends(get_db)):
    """Get all tasks."""
    return db.query(Task).all()

@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return None

# DAG Run Management
@router.post("/dag-runs", response_model=DAGRunOut, status_code=status.HTTP_201_CREATED)
def create_dag_run(dag_run: DAGRunCreate, db: Session = Depends(get_db)):
    """Create a new DAG run."""
    dag = db.query(DAG).filter(DAG.id == dag_run.dag_id).first()
    if not dag:
        raise HTTPException(status_code=400, detail="DAG does not exist")
    
    db_dag_run = DAGRun(**dag_run.dict())
    db.add(db_dag_run)
    db.commit()
    db.refresh(db_dag_run)
    return db_dag_run

@router.get("/dag-runs", response_model=List[DAGRunOut])
def get_dag_runs(db: Session = Depends(get_db)):
    """Get all DAG runs."""
    return db.query(DAGRun).all()

@router.get("/dag-runs/{dag_run_id}", response_model=DAGRunOut)
def get_dag_run(dag_run_id: int, db: Session = Depends(get_db)):
    """Get a specific DAG run."""
    dag_run = db.query(DAGRun).filter(DAGRun.id == dag_run_id).first()
    if not dag_run:
        raise HTTPException(status_code=404, detail="DAG run not found")
    return dag_run

@router.put("/dag-runs/{dag_run_id}", response_model=DAGRunOut)
def update_dag_run(dag_run_id: int, dag_run_update: DAGRunUpdate, db: Session = Depends(get_db)):
    """Update a DAG run."""
    dag_run = db.query(DAGRun).filter(DAGRun.id == dag_run_id).first()
    if not dag_run:
        raise HTTPException(status_code=404, detail="DAG run not found")
    
    for field, value in dag_run_update.dict(exclude_unset=True).items():
        setattr(dag_run, field, value)
    
    db.commit()
    db.refresh(dag_run)
    return dag_run

# Task Instance Management
@router.post("/task-instances", response_model=TaskInstanceOut, status_code=status.HTTP_201_CREATED)
def create_task_instance(task_instance: TaskInstanceCreate, db: Session = Depends(get_db)):
    """Create a new task instance."""
    dag_run = db.query(DAGRun).filter(DAGRun.id == task_instance.dag_run_id).first()
    if not dag_run:
        raise HTTPException(status_code=400, detail="DAG run does not exist")
    
    task = db.query(Task).filter(Task.id == task_instance.task_id_ref).first()
    if not task:
        raise HTTPException(status_code=400, detail="Task does not exist")
    
    db_task_instance = TaskInstance(**task_instance.dict())
    db.add(db_task_instance)
    db.commit()
    db.refresh(db_task_instance)
    return db_task_instance

@router.get("/task-instances", response_model=List[TaskInstanceOut])
def get_task_instances(db: Session = Depends(get_db)):
    """Get all task instances."""
    return db.query(TaskInstance).all()

@router.get("/task-instances/{task_instance_id}", response_model=TaskInstanceOut)
def get_task_instance(task_instance_id: int, db: Session = Depends(get_db)):
    """Get a specific task instance."""
    task_instance = db.query(TaskInstance).filter(TaskInstance.id == task_instance_id).first()
    if not task_instance:
        raise HTTPException(status_code=404, detail="Task instance not found")
    return task_instance

@router.put("/task-instances/{task_instance_id}", response_model=TaskInstanceOut)
def update_task_instance(task_instance_id: int, task_instance_update: TaskInstanceUpdate, db: Session = Depends(get_db)):
    """Update a task instance."""
    task_instance = db.query(TaskInstance).filter(TaskInstance.id == task_instance_id).first()
    if not task_instance:
        raise HTTPException(status_code=404, detail="Task instance not found")
    
    for field, value in task_instance_update.dict(exclude_unset=True).items():
        setattr(task_instance, field, value)
    
    db.commit()
    db.refresh(task_instance)
    return task_instance

# Additional Airflow-specific endpoints
@router.post("/dags/{dag_id}/trigger")
def trigger_dag(dag_id: int, db: Session = Depends(get_db)):
    """Trigger a DAG run."""
    dag = db.query(DAG).filter(DAG.id == dag_id).first()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")
    
    # Create a new DAG run
    run_id = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dag_run = DAGRun(
        run_id=run_id,
        state="running",
        execution_date=datetime.now(),
        dag_id=dag_id
    )
    
    db.add(dag_run)
    db.commit()
    db.refresh(dag_run)
    
    return {"message": f"DAG {dag.dag_id} triggered successfully", "run_id": run_id}

@router.get("/dags/{dag_id}/tasks", response_model=List[TaskOut])
def get_dag_tasks(dag_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a specific DAG."""
    dag = db.query(DAG).filter(DAG.id == dag_id).first()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")
    
    return db.query(Task).filter(Task.dag_id == dag_id).all()

@router.get("/dags/{dag_id}/runs", response_model=List[DAGRunOut])
def get_dag_runs_by_dag(dag_id: int, db: Session = Depends(get_db)):
    """Get all runs for a specific DAG."""
    dag = db.query(DAG).filter(DAG.id == dag_id).first()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")
    
    return db.query(DAGRun).filter(DAGRun.dag_id == dag_id).all()

@router.get("/pipelines/{dag_id}/embed_url", response_model=dict)
def get_pipeline_embed_url(dag_id: str):
    # In production, lookup the real Airflow URL and handle auth/tokens
    url = f"http://airflow-webserver:8080/graph?dag_id={dag_id}"
    return {"url": url}

@router.get("/workspaces/{workspace_id}/dags", response_model=List[DAGOut])
def get_workspace_dags(workspace_id: int, db: Session = Depends(get_db)):
    """Get all DAGs for a specific workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return db.query(DAG).filter(DAG.workspace_id == workspace_id).all()

@router.get("/workspaces/{workspace_id}/connections", response_model=List[AirflowConnectionOut])
def get_workspace_connections(workspace_id: int, db: Session = Depends(get_db)):
    """Get all Airflow connections for a specific workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return db.query(AirflowConnection).filter(AirflowConnection.workspace_id == workspace_id).all() 