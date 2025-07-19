from fastapi import APIRouter

router = APIRouter(prefix="/audit/teams/{team_slug}", tags=["audit"])

@router.get("/logs")
def query_audit_logs(team_slug: str):
    return {"logs": []}

@router.get("/logs/actions")
def get_available_actions(team_slug: str):
    return {"actions": []}

@router.post("/logs/downloads")
def download_audit_logs(team_slug: str):
    return {"message": "Audit logs download started"} 