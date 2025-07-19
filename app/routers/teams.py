from fastapi import APIRouter, status

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("")
def get_teams():
    return [{"id": 1, "name": "Team Alpha"}, {"id": 2, "name": "Team Beta"}]

@router.get("/{team_slug}/memberships")
def get_team_members(team_slug: str):
    return {"members": []}

@router.get("/{team_slug}/invites")
def get_pending_invites(team_slug: str):
    return {"invites": []}

@router.get("/{team_slug}/regions")
def get_team_regions(team_slug: str):
    return {"regions": []}

@router.post("/{team_slug}/invites", status_code=status.HTTP_201_CREATED)
def create_team_invite(team_slug: str):
    return {"message": "Invite created"}

@router.post("/{team_slug}/invites/many", status_code=status.HTTP_201_CREATED)
def create_multiple_team_invites(team_slug: str):
    return {"message": "Multiple invites created"}

@router.post("/{team_slug}/invites/resend/{invite_id}")
def resend_invite(team_slug: str, invite_id: int):
    return {"message": "Invite resent"}

@router.put("/{team_slug}")
def update_team_title(team_slug: str):
    return {"message": "Team title updated"}

@router.patch("/{team_slug}/memberships/{user_id}")
def change_user_role(team_slug: str, user_id: int):
    return {"message": "User role changed"}

@router.delete("/{team_slug}/memberships/{user_id}")
def delete_team_member(team_slug: str, user_id: int):
    return {"message": "Team member deleted"}

@router.delete("/{team_slug}/invites/{invite_id}")
def delete_pending_invite(team_slug: str, invite_id: int):
    return {"message": "Pending invite deleted"} 