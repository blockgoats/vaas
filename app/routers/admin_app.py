import uvicorn
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Model
from fastapi_admin.factory import app as admin_factory

from app.routers.db import engine
from models import User, Team, Workspace, Dataset, Chart, Dashboard
from resources import UserResource, WorkspaceResource

app = FastAPI()

@app.on_event("startup")
async def startup():
    await admin_factory(
        app=admin_app,
        admin_secret="your_admin_secret",
        providers=[
            UsernamePasswordProvider(
                admin_model=User,
                login_logo_url="https://fastapi-admin.github.io/img/logo.png"
            )
        ],
        resources=[
            UserResource,
            WorkspaceResource,
            Model(Team),
            Model(Dataset),
            Model(Chart),
            Model(Dashboard),
        ],
        engine=engine,
    )

app.mount("/admin", admin_app)

if __name__ == "__main__":
    uvicorn.run("admin_app:app", host="0.0.0.0", port=8001, reload=True) 