from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routers.db import SessionLocal
from app.routers.models import User, Team
from app.routers.schemas import UserCreate, UserUpdate, UserOut
from typing import List
from app.routers.superset_client import create_superset_user

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Ensure team exists
    team = db.query(Team).filter(Team.id == user.team_id).first()
    if not team:
        raise HTTPException(status_code=400, detail="Team does not exist")
    db_user = User(email=user.email, name=user.name, team_id=user.team_id)
    db.add(db_user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    db.refresh(db_user)
    # Create user in Superset (best effort)
    try:
        create_superset_user(
            username=user.email,
            email=user.email,
            first_name=user.name,
            last_name="",
            role="Gamma"
        )
    except Exception as e:
        print(f"[WARN] Could not create user in Superset: {e}")
    return db_user

@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.team_id is not None:
        team = db.query(Team).filter(Team.id == user_update.team_id).first()
        if not team:
            raise HTTPException(status_code=400, detail="Team does not exist")
        user.team_id = user_update.team_id
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None

@router.get("/by_team/{team_id}", response_model=List[UserOut])
def get_users_by_team(team_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.team_id == team_id).all() 