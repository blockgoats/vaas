from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import Workspace, Team, WorkspaceMembership, User
from app.routers.schemas import WorkspaceCreate, WorkspaceUpdate, WorkspaceOut, WorkspaceMembershipCreate, WorkspaceMembershipOut
from typing import List
from app.routers.superset_client import create_superset_database

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == workspace.team_id).first()
    if not team:
        raise HTTPException(status_code=400, detail="Team does not exist")
    db_workspace = Workspace(**workspace.dict())
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    # Create workspace in Superset (best effort)
    try:
        sqlalchemy_uri = f"postgresql+psycopg2://vaasuser:vaaspass@localhost:5432/vaasdb"
        create_superset_database(database_name=workspace.name, sqlalchemy_uri=sqlalchemy_uri)
    except Exception as e:
        print(f"[WARN] Could not create workspace in Superset: {e}")
    return db_workspace

@router.get("/", response_model=List[WorkspaceOut])
def get_workspaces(db: Session = Depends(get_db)):
    return db.query(Workspace).all()

@router.get("/{workspace_id}", response_model=WorkspaceOut)
def get_workspace(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.put("/{workspace_id}", response_model=WorkspaceOut)
def update_workspace(workspace_id: int, workspace_update: WorkspaceUpdate, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if workspace_update.name is not None:
        workspace.name = workspace_update.name
    if workspace_update.team_id is not None:
        team = db.query(Team).filter(Team.id == workspace_update.team_id).first()
        if not team:
            raise HTTPException(status_code=400, detail="Team does not exist")
        workspace.team_id = workspace_update.team_id
    db.commit()
    db.refresh(workspace)
    return workspace

@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.delete(workspace)
    db.commit()
    return None

@router.get("/by_team/{team_id}", response_model=List[WorkspaceOut])
def get_workspaces_by_team(team_id: int, db: Session = Depends(get_db)):
    return db.query(Workspace).filter(Workspace.team_id == team_id).all()

@router.get("/by_region/{region_id}", response_model=List[WorkspaceOut])
def get_workspaces_by_region(region_id: int, db: Session = Depends(get_db)):
    return db.query(Workspace).filter(Workspace.region_id == region_id).all()

@router.get("/by_cluster/{cluster_id}", response_model=List[WorkspaceOut])
def get_workspaces_by_cluster(cluster_id: int, db: Session = Depends(get_db)):
    return db.query(Workspace).filter(Workspace.cluster_id == cluster_id).all()

@router.get("/{workspace_id}/memberships")
def get_workspace_users(team_slug: str, workspace_id: int):
    return {"users": []}

@router.get("/{workspace_slug}/access-token-keys")
def get_embedded_auth_keys(team_slug: str, workspace_slug: str):
    return {"keys": []}

@router.post("/{workspace_slug}/access-token-keys")
def create_embedded_auth_key(team_slug: str, workspace_slug: str):
    return {"message": "Embedded auth key created"}

@router.delete("/{workspace_slug}/access-token-keys/{key_id}")
def delete_embedded_auth_key(team_slug: str, workspace_slug: str, key_id: int):
    return {"message": "Embedded auth key deleted"}

@router.post("/{workspace_id}/memberships", response_model=WorkspaceMembershipOut, status_code=status.HTTP_201_CREATED)
def add_user_to_workspace(workspace_id: int, membership: WorkspaceMembershipCreate, db: Session = Depends(get_db)):
    # Ensure workspace and user exist
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    user = db.query(User).filter(User.id == membership.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Only team members can join workspaces
    if user.team_id != workspace.team_id:
        raise HTTPException(status_code=400, detail="User is not a member of the workspace's team")
    # Prevent duplicate membership
    existing = db.query(WorkspaceMembership).filter_by(user_id=membership.user_id, workspace_id=workspace_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already a member of this workspace")
    db_membership = WorkspaceMembership(user_id=membership.user_id, workspace_id=workspace_id, role=membership.role)
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

@router.delete("/{workspace_id}/memberships/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_workspace(workspace_id: int, user_id: int, db: Session = Depends(get_db)):
    membership = db.query(WorkspaceMembership).filter_by(user_id=user_id, workspace_id=workspace_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    db.delete(membership)
    db.commit()
    return None

@router.get("/{workspace_id}/memberships", response_model=List[WorkspaceMembershipOut])
def list_workspace_members(workspace_id: int, db: Session = Depends(get_db)):
    return db.query(WorkspaceMembership).filter_by(workspace_id=workspace_id).all()

@router.get("/memberships/by_user/{user_id}", response_model=List[WorkspaceMembershipOut])
def list_user_workspaces(user_id: int, db: Session = Depends(get_db)):
    return db.query(WorkspaceMembership).filter_by(user_id=user_id).all() 