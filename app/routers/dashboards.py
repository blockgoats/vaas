from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import Dashboard, DashboardChart, DashboardPermission, DatabaseConnection, Workspace
from app.routers.schemas import DashboardChartOut, DashboardCreate, DashboardOut, DashboardPermissionCreate, DashboardPermissionOut, DashboardUpdate, DatabaseConnectionCreate, DatabaseConnectionUpdate, DatabaseConnectionOut
from typing import List
from app.routers.superset_client import create_superset_database, discover_database_schema

router = APIRouter(prefix="/dashboards", tags=["dashboards"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DashboardOut, status_code=status.HTTP_201_CREATED)
def create_dashboard(dashboard: DashboardCreate, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(Workspace.id == dashboard.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="Workspace does not exist")
    db_dashboard = Dashboard(**dashboard.dict())
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    
    # Create dashboard in Superset (best effort)
    try:
        create_superset_dashboard(dashboard_title=dashboard.title, database_id=dashboard.workspace_id)
    except Exception as e:
        print(f"[WARN] Could not create dashboard in Superset: {e}")
    
    return db_dashboard

@router.get("/", response_model=List[DashboardOut])
def get_dashboards(db: Session = Depends(get_db)):
    return db.query(Dashboard).all()

@router.get("/{dashboard_id}", response_model=DashboardOut)
def get_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard

@router.put("/{dashboard_id}", response_model=DashboardOut)
def update_dashboard(dashboard_id: int, dashboard_update: DashboardUpdate, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    for field, value in dashboard_update.dict(exclude_unset=True).items():
        setattr(dashboard, field, value)
    db.commit()
    db.refresh(dashboard)
    return dashboard

@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.delete(dashboard)
    db.commit()
    return None

# Assign chart to dashboard
@router.post("/{dashboard_id}/charts", response_model=DashboardChartOut, status_code=status.HTTP_201_CREATED)
def add_chart_to_dashboard(dashboard_id: int, chart_id: int, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    chart = db.query(Chart).filter(Chart.id == chart_id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    existing = db.query(DashboardChart).filter_by(dashboard_id=dashboard_id, chart_id=chart_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Chart already assigned to dashboard")
    db_dc = DashboardChart(dashboard_id=dashboard_id, chart_id=chart_id)
    db.add(db_dc)
    db.commit()
    db.refresh(db_dc)
    return db_dc

# Remove chart from dashboard
@router.delete("/{dashboard_id}/charts/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_chart_from_dashboard(dashboard_id: int, chart_id: int, db: Session = Depends(get_db)):
    dc = db.query(DashboardChart).filter_by(dashboard_id=dashboard_id, chart_id=chart_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Chart not assigned to dashboard")
    db.delete(dc)
    db.commit()
    return None

# List charts in dashboard
@router.get("/{dashboard_id}/charts", response_model=List[DashboardChartOut])
def list_charts_in_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    return db.query(DashboardChart).filter(DashboardChart.dashboard_id == dashboard_id).all()

# List dashboards by workspace
@router.get("/by_workspace/{workspace_id}", response_model=List[DashboardOut])
def list_dashboards_by_workspace(workspace_id: int, db: Session = Depends(get_db)):
    return db.query(Dashboard).filter(Dashboard.workspace_id == workspace_id).all()

# Dashboard permissions
@router.post("/{dashboard_id}/permissions", response_model=DashboardPermissionOut, status_code=status.HTTP_201_CREATED)
def create_dashboard_permission(dashboard_id: int, perm: DashboardPermissionCreate, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    user = db.query(User).filter(User.id == perm.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_perm = DashboardPermission(dashboard_id=dashboard_id, user_id=perm.user_id, permission=perm.permission)
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm

@router.get("/{dashboard_id}/permissions", response_model=List[DashboardPermissionOut])
def list_dashboard_permissions(dashboard_id: int, db: Session = Depends(get_db)):
    return db.query(DashboardPermission).filter(DashboardPermission.dashboard_id == dashboard_id).all()

@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard_permission(permission_id: int, db: Session = Depends(get_db)):
    perm = db.query(DashboardPermission).filter(DashboardPermission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(perm)
    db.commit()
    return None

@router.get("/templates/{database_type}")
def get_dashboard_templates_for_database(database_type: str):
    """Get available dashboard templates for a specific database type."""
    try:
        templates = get_dashboard_templates(database_type)
        return {"database_type": database_type, "templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}") 

@router.get("/{dashboard_id}/embed_url", response_model=dict)
def get_dashboard_embed_url(dashboard_id: int):
    # In production, lookup the real Superset URL and handle auth/tokens
    url = f"http://superset:8088/superset/dashboard/{dashboard_id}/?standalone=1"
    return {"url": url} 