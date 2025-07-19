from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import DatabaseConnection, Workspace
from app.routers.schemas import DatabaseConnectionCreate, DatabaseConnectionUpdate, DatabaseConnectionOut
from typing import List
from app.routers.superset_client import create_superset_database, discover_database_schema

SUPPORTED_DB_TYPES = ["postgres", "mysql", "sqlite", "oracle", "postgresql", "hive", "snowflake"]

router = APIRouter(prefix="/databases", tags=["databases"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/types", response_model=List[str])
def get_supported_db_types():
    return SUPPORTED_DB_TYPES

@router.post("/", response_model=DatabaseConnectionOut, status_code=status.HTTP_201_CREATED)
def create_database(db_conn: DatabaseConnectionCreate, db: Session = Depends(get_db)):
    if db_conn.type not in SUPPORTED_DB_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported database type. Supported types: {SUPPORTED_DB_TYPES}")
    workspace = db.query(Workspace).filter(Workspace.id == db_conn.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="Workspace does not exist")
    db_db = DatabaseConnection(**db_conn.dict())
    db.add(db_db)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database connection name must be unique")
    db.refresh(db_db)
    
    # Create database in Superset (best effort)
    try:
        sqlalchemy_uri = db_conn.connection_string
        create_superset_database(database_name=db_conn.name, sqlalchemy_uri=sqlalchemy_uri)
    except Exception as e:
        print(f"[WARN] Could not create database in Superset: {e}")
    
    return db_db

@router.get("/", response_model=List[DatabaseConnectionOut])
def get_databases(db: Session = Depends(get_db)):
    return db.query(DatabaseConnection).all()

@router.get("/{db_id}", response_model=DatabaseConnectionOut)
def get_database(db_id: int, db: Session = Depends(get_db)):
    db_db = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
    if not db_db:
        raise HTTPException(status_code=404, detail="Database connection not found")
    return db_db

@router.put("/{db_id}", response_model=DatabaseConnectionOut)
def update_database(db_id: int, db_update: DatabaseConnectionUpdate, db: Session = Depends(get_db)):
    if db_update.type is not None and db_update.type not in SUPPORTED_DB_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported database type. Supported types: {SUPPORTED_DB_TYPES}")
    db_db = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
    if not db_db:
        raise HTTPException(status_code=404, detail="Database connection not found")
    for field, value in db_update.dict(exclude_unset=True).items():
        setattr(db_db, field, value)
    db.commit()
    db.refresh(db_db)
    return db_db

@router.delete("/{db_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_database(db_id: int, db: Session = Depends(get_db)):
    db_db = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
    if not db_db:
        raise HTTPException(status_code=404, detail="Database connection not found")
    db.delete(db_db)
    db.commit()
    return None

@router.post("/{db_id}/test", status_code=status.HTTP_200_OK)
def test_database_connection(db_id: int, db: Session = Depends(get_db)):
    # This is a mock; in production, actually test the connection
    db_db = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
    if not db_db:
        raise HTTPException(status_code=404, detail="Database connection not found")
    return {"success": True, "message": "Connection successful (mocked)"}

@router.get("/{db_id}/schema")
def get_database_schema(db_id: int, db: Session = Depends(get_db)):
    """Get database schema information."""
    db_db = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
    if not db_db:
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    try:
        schema = discover_database_schema(db_id)
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to discover schema: {str(e)}") 