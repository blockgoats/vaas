from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import Dataset, DatabaseConnection, Workspace, DatasetColumn, DatasetMetric, DatasetPermission, User
from app.routers.schemas import DatasetCreate, DatasetUpdate, DatasetOut, DatasetColumnCreate, DatasetColumnUpdate, DatasetColumnOut, DatasetMetricCreate, DatasetMetricUpdate, DatasetMetricOut, DatasetPermissionCreate, DatasetPermissionOut
from typing import List

router = APIRouter(prefix="/datasets", tags=["datasets"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
def create_dataset(dataset: DatasetCreate, db: Session = Depends(get_db)):
    db_conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == dataset.database_id).first()
    if not db_conn:
        raise HTTPException(status_code=400, detail="Database connection does not exist")
    workspace = db.query(Workspace).filter(Workspace.id == dataset.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="Workspace does not exist")
    db_dataset = Dataset(**dataset.dict())
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

@router.get("/", response_model=List[DatasetOut])
def get_datasets(db: Session = Depends(get_db)):
    return db.query(Dataset).all()

@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.put("/{dataset_id}", response_model=DatasetOut)
def update_dataset(dataset_id: int, dataset_update: DatasetUpdate, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    for field, value in dataset_update.dict(exclude_unset=True).items():
        setattr(dataset, field, value)
    db.commit()
    db.refresh(dataset)
    return dataset

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(dataset)
    db.commit()
    return None

# Dataset Columns
@router.post("/{dataset_id}/columns", response_model=DatasetColumnOut, status_code=status.HTTP_201_CREATED)
def create_column(dataset_id: int, column: DatasetColumnCreate, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db_column = DatasetColumn(**column.dict(), dataset_id=dataset_id)
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column

@router.get("/{dataset_id}/columns", response_model=List[DatasetColumnOut])
def list_columns(dataset_id: int, db: Session = Depends(get_db)):
    return db.query(DatasetColumn).filter(DatasetColumn.dataset_id == dataset_id).all()

@router.put("/columns/{column_id}", response_model=DatasetColumnOut)
def update_column(column_id: int, column_update: DatasetColumnUpdate, db: Session = Depends(get_db)):
    column = db.query(DatasetColumn).filter(DatasetColumn.id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    for field, value in column_update.dict(exclude_unset=True).items():
        setattr(column, field, value)
    db.commit()
    db.refresh(column)
    return column

@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_column(column_id: int, db: Session = Depends(get_db)):
    column = db.query(DatasetColumn).filter(DatasetColumn.id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    db.delete(column)
    db.commit()
    return None

# Dataset Metrics
@router.post("/{dataset_id}/metrics", response_model=DatasetMetricOut, status_code=status.HTTP_201_CREATED)
def create_metric(dataset_id: int, metric: DatasetMetricCreate, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db_metric = DatasetMetric(**metric.dict(), dataset_id=dataset_id)
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

@router.get("/{dataset_id}/metrics", response_model=List[DatasetMetricOut])
def list_metrics(dataset_id: int, db: Session = Depends(get_db)):
    return db.query(DatasetMetric).filter(DatasetMetric.dataset_id == dataset_id).all()

@router.put("/metrics/{metric_id}", response_model=DatasetMetricOut)
def update_metric(metric_id: int, metric_update: DatasetMetricUpdate, db: Session = Depends(get_db)):
    metric = db.query(DatasetMetric).filter(DatasetMetric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    for field, value in metric_update.dict(exclude_unset=True).items():
        setattr(metric, field, value)
    db.commit()
    db.refresh(metric)
    return metric

@router.delete("/metrics/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric(metric_id: int, db: Session = Depends(get_db)):
    metric = db.query(DatasetMetric).filter(DatasetMetric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    db.delete(metric)
    db.commit()
    return None

# Dataset Permissions
@router.post("/{dataset_id}/permissions", response_model=DatasetPermissionOut, status_code=status.HTTP_201_CREATED)
def create_permission(dataset_id: int, perm: DatasetPermissionCreate, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    user = db.query(User).filter(User.id == perm.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_perm = DatasetPermission(dataset_id=dataset_id, user_id=perm.user_id, permission=perm.permission)
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm

@router.get("/{dataset_id}/permissions", response_model=List[DatasetPermissionOut])
def list_permissions(dataset_id: int, db: Session = Depends(get_db)):
    return db.query(DatasetPermission).filter(DatasetPermission.dataset_id == dataset_id).all()

@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    perm = db.query(DatasetPermission).filter(DatasetPermission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(perm)
    db.commit()
    return None 