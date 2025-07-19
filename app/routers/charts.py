from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import Chart, Dataset, Workspace, DashboardChart
from app.routers.schemas import ChartCreate, ChartUpdate, ChartOut
from typing import List
from app.routers.superset_client import create_superset_chart, create_auto_charts_for_table

router = APIRouter(prefix="/charts", tags=["charts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ChartOut, status_code=status.HTTP_201_CREATED)
def create_chart(chart: ChartCreate, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == chart.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=400, detail="Dataset does not exist")
    workspace = db.query(Workspace).filter(Workspace.id == chart.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="Workspace does not exist")
    db_chart = Chart(**chart.dict())
    db.add(db_chart)
    db.commit()
    db.refresh(db_chart)
    
    # Create chart in Superset (best effort)
    try:
        create_superset_chart(chart_title=chart.title, database_id=chart.workspace_id, table_name=chart.title.lower())
    except Exception as e:
        print(f"[WARN] Could not create chart in Superset: {e}")
    
    return db_chart

@router.get("/", response_model=List[ChartOut])
def get_charts(db: Session = Depends(get_db)):
    return db.query(Chart).all()

@router.get("/{chart_id}", response_model=ChartOut)
def get_chart(chart_id: int, db: Session = Depends(get_db)):
    chart = db.query(Chart).filter(Chart.id == chart_id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    return chart

@router.put("/{chart_id}", response_model=ChartOut)
def update_chart(chart_id: int, chart_update: ChartUpdate, db: Session = Depends(get_db)):
    chart = db.query(Chart).filter(Chart.id == chart_id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    for field, value in chart_update.dict(exclude_unset=True).items():
        setattr(chart, field, value)
    db.commit()
    db.refresh(chart)
    return chart

@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chart(chart_id: int, db: Session = Depends(get_db)):
    chart = db.query(Chart).filter(Chart.id == chart_id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    db.delete(chart)
    db.commit()
    return None

@router.post("/auto/{database_id}/{table_name}")
def create_auto_charts_for_table_endpoint(database_id: int, table_name: str, columns: List[str], db: Session = Depends(get_db)):
    """Create automatic charts for a table based on its columns."""
    try:
        charts = create_auto_charts_for_table(database_id, table_name, columns)
        return {"table_name": table_name, "charts": charts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create auto charts: {str(e)}") 