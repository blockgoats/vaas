from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import Cluster, Region
from app.routers.schemas import ClusterCreate, ClusterUpdate, ClusterOut
from typing import List

router = APIRouter(prefix="/clusters", tags=["clusters"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ClusterOut, status_code=status.HTTP_201_CREATED)
def create_cluster(cluster: ClusterCreate, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == cluster.region_id).first()
    if not region:
        raise HTTPException(status_code=400, detail="Region does not exist")
    db_cluster = Cluster(**cluster.dict())
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster

@router.get("/", response_model=List[ClusterOut])
def get_clusters(db: Session = Depends(get_db)):
    return db.query(Cluster).all()

@router.get("/{cluster_id}", response_model=ClusterOut)
def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@router.put("/{cluster_id}", response_model=ClusterOut)
def update_cluster(cluster_id: int, cluster_update: ClusterUpdate, db: Session = Depends(get_db)):
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    for field, value in cluster_update.dict(exclude_unset=True).items():
        setattr(cluster, field, value)
    db.commit()
    db.refresh(cluster)
    return cluster

@router.delete("/{cluster_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cluster(cluster_id: int, db: Session = Depends(get_db)):
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    db.delete(cluster)
    db.commit()
    return None 