from fastapi import APIRouter, status

router = APIRouter(prefix="/teams/{team_slug}/permissions", tags=["permissions"])

@router.get("/resources")
def get_resources(team_slug: str):
    return {"resources": []}

@router.get("")
def get_permissions(team_slug: str):
    return {"permissions": []}

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_permission(team_slug: str):
    return {"message": "Permission created"}

@router.post("/{permission_name}/grantees")
def add_grantees(team_slug: str, permission_name: str):
    return {"message": "Grantees added"}

@router.patch("/{permission_name}")
def update_permission(team_slug: str, permission_name: str):
    return {"message": "Permission updated"}

@router.delete("/{permission_name}")
def delete_permission(team_slug: str, permission_name: str):
    return {"message": "Permission deleted"}

@router.delete("/{permission_name}/grantees")
def delete_grantee(team_slug: str, permission_name: str):
    return {"message": "Grantee removed"} 