from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthRequest(BaseModel):
    name: str
    secret: str

@router.post("/", status_code=status.HTTP_200_OK)
def get_jwt_token(auth: AuthRequest):
    # Mock JWT token
    return {"access_token": "mocked.jwt.token", "token_type": "bearer"} 