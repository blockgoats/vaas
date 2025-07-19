from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid
import time

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# In-memory job status store (use Redis or DB in production)
onboarding_jobs = {}

@router.post("/start", response_model=dict)
def start_onboarding(background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    onboarding_jobs[job_id] = {"status": "starting"}
    background_tasks.add_task(run_onboarding_job, job_id)
    return {"job_id": job_id}

def run_onboarding_job(job_id):
    onboarding_jobs[job_id]["status"] = "connecting"
    time.sleep(1)
    onboarding_jobs[job_id]["status"] = "discovering"
    time.sleep(1)
    onboarding_jobs[job_id]["status"] = "generating"
    time.sleep(1)
    onboarding_jobs[job_id]["status"] = "complete"

@router.get("/status/{job_id}", response_model=dict)
def onboarding_status(job_id: str):
    if job_id not in onboarding_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": onboarding_jobs[job_id]["status"]} 