from fastapi import FastAPI
from app.routers import auth, teams, workspaces, permissions, audit, embedded, users, databases, datasets, charts, dashboards, regions, clusters, airflow, onboarding
from app.routers.startup import init_db
from app.main2 import app as legacy_app

app = FastAPI()

init_db()

app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(users.router)
app.include_router(workspaces.router)
app.include_router(databases.router)
app.include_router(datasets.router)
app.include_router(charts.router)
app.include_router(dashboards.router)
app.include_router(regions.router)
app.include_router(clusters.router)
app.include_router(permissions.router)
app.include_router(audit.router)
app.include_router(embedded.router)
app.include_router(airflow.router)
app.include_router(onboarding.router)

# Mount the legacy/AI app under /ai
app.mount("/ai", legacy_app)

@app.get("/")
def read_root():
    return {"message": "Preset API local clone running!"} 

