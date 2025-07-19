from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://bi_user:bi_password@localhost:5432/bi_platform')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")
    settings = Column(JSON)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String)  # admin, editor, viewer
    workspace_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # postgresql, mysql, snowflake, bigquery
    host = Column(String)
    port = Column(Integer)
    database = Column(String)
    username = Column(String)
    encrypted_password = Column(String)
    workspace_id = Column(String)
    status = Column(String, default="active")
    last_test = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)  # Schema information, table list, etc.

class Chart(Base):
    __tablename__ = "charts"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # bar, line, pie, etc.
    config = Column(JSON)  # Chart configuration
    sql_query = Column(Text)
    data_source_id = Column(String)
    workspace_id = Column(String)
    created_by = Column(String)
    is_ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)  # Original prompt if AI generated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    views = Column(Integer, default=0)

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    layout = Column(JSON)  # Dashboard layout configuration
    chart_ids = Column(JSON)  # List of chart IDs
    workspace_id = Column(String)
    created_by = Column(String)
    is_public = Column(Boolean, default=False)
    embed_token = Column(String)  # For embedded dashboards
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    action = Column(String)  # login, create_chart, view_dashboard, etc.
    resource_type = Column(String)  # chart, dashboard, data_source
    resource_id = Column(String)
    workspace_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    metadata = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()