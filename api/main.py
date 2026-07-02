from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import os
import logging
logging.basicConfig(level=logging.INFO)

APP_NAME = os.getenv(
    "APP_NAME",
    "HPC AI Performance Engineering Platform"
)


logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    version="0.1.0"
)

class BenchmarkRequest(BaseModel):
    benchmark: str


jobs = {}
job_queue = []
@app.get("/")
def root():
    return {
        "message": "HPC API DEV",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.get("/benchmarks")
def list_benchmarks():
    return {
        "benchmarks": [
            "cpu",
            "memory",
            "disk_io"
        ]
    }


@app.post("/benchmark")
def create_benchmark(request: BenchmarkRequest):
    logger.info(
        "Received benchmark request: %s",
        request.benchmark
    )

    job_id = str(uuid4())
    jobs[job_id] = {
    "job_id": job_id,
    "benchmark": request.benchmark,
    "status": "accepted",
    "result": None
}
    job_queue.append(job_id)
    return {
        "message": "benchmark request received",
        "job_id": job_id,
        "benchmark": request.benchmark,
        "status": "accepted",
        "next_step": "job status API will be added next"
    }

@app.get("/jobs")
def get_jobs():
    return {
        "jobs": jobs
    }

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="job not found")

    return jobs[job_id]

@app.post("/worker/process-next")
def process_next_job():
    if not job_queue:
        return {
            "message": "no pending jobs"
        }

    job_id = job_queue.pop(0)
    job = jobs[job_id]

    job["status"] = "completed"
    job["result"] = {
        "message": "benchmark simulated"
    }

    return job

@app.get("/metrics")
def metrics():
    completed_jobs = 0

    for job in jobs.values():
        if job["status"] == "completed":
            completed_jobs = completed_jobs + 1

    return {
        "total_jobs": len(jobs),
        "queued_jobs": len(job_queue),
        "completed_jobs": completed_jobs
    }
