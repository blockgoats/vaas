from app.routers.db import Base, engine
import app.routers.models  # ensure models (including Region, Cluster) are imported

def init_db():
    # Base.metadata.create_all(bind=engine)
    print("Initializing the database...")