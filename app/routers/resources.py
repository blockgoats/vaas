from fastapi_admin.resources import Model
from fastapi_admin.widgets import displays, inputs
from models import User, Team, Workspace

class UserResource(Model):
    label = "User"
    model = User
    icon = "fa fa-user"
    fields = [
        "id",
        displays.Input(display="Email", field="email"),
        displays.Input(display="Name", field="name"),
        displays.ForeignKey(display="Team", field="team_id", model=Team, search_field="name"),
    ]
    search_fields = ["email", "name"]
    filters = ["team_id"]
    can_create = True
    can_edit = True
    can_delete = True

class WorkspaceResource(Model):
    label = "Workspace"
    model = Workspace
    icon = "fa fa-building"
    fields = [
        "id",
        displays.Input(display="Name", field="name"),
        displays.ForeignKey(display="Team", field="team_id", model=Team, search_field="name"),
        displays.Input(display="Region", field="region_id"),
        displays.Input(display="Cluster", field="cluster_id"),
    ]
    search_fields = ["name"]
    filters = ["team_id", "region_id", "cluster_id"]
    can_create = True
    can_edit = True
    can_delete = True 