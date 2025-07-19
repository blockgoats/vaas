from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import EmbeddedConfig, EmbeddedToken, Dashboard
from app.routers.schemas import EmbeddedConfigCreate, EmbeddedConfigUpdate, EmbeddedConfigOut, EmbeddedTokenCreate, EmbeddedTokenOut
from typing import List
import uuid

router = APIRouter(prefix="/embedded", tags=["embedded"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/dashboard/{dashboard_id}/enable", response_model=EmbeddedConfigOut)
def enable_embedded(dashboard_id: int, config: EmbeddedConfigCreate, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db_config = db.query(EmbeddedConfig).filter(EmbeddedConfig.dashboard_id == dashboard_id).first()
    if db_config:
        db_config.enabled = True
        db_config.allowed_domains = config.allowed_domains
    else:
        db_config = EmbeddedConfig(dashboard_id=dashboard_id, enabled=True, allowed_domains=config.allowed_domains)
        db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.post("/dashboard/{dashboard_id}/disable", response_model=EmbeddedConfigOut)
def disable_embedded(dashboard_id: int, db: Session = Depends(get_db)):
    db_config = db.query(EmbeddedConfig).filter(EmbeddedConfig.dashboard_id == dashboard_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Embedded config not found")
    db_config.enabled = False
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/dashboard/{dashboard_id}/config", response_model=EmbeddedConfigOut)
def get_embedded_config(dashboard_id: int, db: Session = Depends(get_db)):
    db_config = db.query(EmbeddedConfig).filter(EmbeddedConfig.dashboard_id == dashboard_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Embedded config not found")
    return db_config

@router.post("/dashboard/{dashboard_id}/token", response_model=EmbeddedTokenOut)
def generate_embedded_token(dashboard_id: int, token_req: EmbeddedTokenCreate, db: Session = Depends(get_db)):
    db_config = db.query(EmbeddedConfig).filter(EmbeddedConfig.dashboard_id == dashboard_id).first()
    if not db_config or not db_config.enabled:
        raise HTTPException(status_code=400, detail="Embedded mode not enabled for this dashboard")
    token = str(uuid.uuid4())
    db_token = EmbeddedToken(token=token, dashboard_id=dashboard_id, user_info=token_req.user_info, expiry=token_req.expiry)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token 