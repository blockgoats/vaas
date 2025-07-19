from db import SessionLocal
from models import Team, User, Workspace, WorkspaceMembership, DatabaseConnection, Dataset, Chart, Dashboard, Region, Cluster

db = SessionLocal()

# 1. Insert Teams
team = Team(name="Test Team")
db.add(team)
db.commit()
db.refresh(team)

# 2. Insert Users
user = User(email="testuser@example.com", name="Test User", team_id=team.id)
db.add(user)
db.commit()
db.refresh(user)

# 3. Insert Workspace
workspace = Workspace(name="Test Workspace", team_id=team.id)
db.add(workspace)
db.commit()
db.refresh(workspace)

# 4. Insert Workspace Membership
membership = WorkspaceMembership(user_id=user.id, workspace_id=workspace.id, role="admin")
db.add(membership)
db.commit()

# 5. Insert Database Connection
db_conn = DatabaseConnection(
    name="TestDB",
    type="postgres",
    host="localhost",
    port=5432,
    username="vaasuser",
    password="vaaspass",
    workspace_id=workspace.id
)
db.add(db_conn)
db.commit()
db.refresh(db_conn)

# 6. Insert Dataset
dataset = Dataset(
    name="Test Dataset",
    schema="public",
    table="test_table",
    database_id=db_conn.id,
    workspace_id=workspace.id
)
db.add(dataset)
db.commit()
db.refresh(dataset)

# 7. Insert Chart
chart = Chart(
    name="Test Chart",
    type="bar",
    params="{}",
    dataset_id=dataset.id,
    workspace_id=workspace.id
)
db.add(chart)
db.commit()
db.refresh(chart)

# 8. Insert Dashboard
dashboard = Dashboard(
    name="Test Dashboard",
    workspace_id=workspace.id
)
db.add(dashboard)
db.commit()
db.refresh(dashboard)

# 9. Insert Region
region = Region(name="Test Region", code="test-region", description="A test region")
db.add(region)
db.commit()
db.refresh(region)

# 10. Insert Cluster
cluster = Cluster(name="Test Cluster", description="A test cluster", region_id=region.id)
db.add(cluster)
db.commit()
db.refresh(cluster)

db.close()
print("Test data inserted successfully.") 