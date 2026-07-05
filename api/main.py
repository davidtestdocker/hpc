from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from uuid import UUID
import os
import logging
import redis
from api.database.models import Job
from api.database.session import SessionLocal
from redis.exceptions import ConnectionError
import json
from datetime import datetime, timezone, timedelta
logging.basicConfig(level=logging.INFO)

APP_NAME = os.getenv(
    "APP_NAME",
    "HPC AI Performance Engineering Platform"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

app = FastAPI(
    title=APP_NAME,
    version="0.1.0"
)

class BenchmarkRequest(BaseModel):
    benchmark: str
    simulate_failure: bool = False


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

@app.get("/health/redis")
def redis_health():
    try:
        redis_client.ping()

        return {
            "status": "healthy",
            "redis": "connected"
        }

    except ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Redis unavailable"
        )


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

    job = {
    "job_id": job_id,
    "benchmark": request.benchmark,
    "simulate_failure": request.simulate_failure,
    "status": "accepted",
    "result": None,
    "retry_count": 0
    }

    redis_client.set(
        f"job:{job_id}",
        json.dumps(job)
    )
    session = SessionLocal()

    db_job = Job(
        job_id=job_id,
        benchmark=job["benchmark"],
        status=job["status"],
        retry_count=job["retry_count"],
        created_at=datetime.now(timezone.utc)
    )

    session.add(db_job)
    session.commit()
    session.close()

    redis_client.rpush(
        "job_queue",
        job_id
    )
    return {
        "message": "benchmark request received",
        "job_id": job_id,
        "benchmark": request.benchmark,
        "status": "accepted",
        "next_step": "job status API will be added next"
    }

#第八週要改成scan而不是keys方式
@app.get("/jobs")
def get_jobs():

    job_keys = redis_client.keys("job:*")

    jobs = []

    for key in job_keys:
        job = json.loads(
            redis_client.get(key)
        )
        jobs.append(job)

    return {
        "jobs": jobs
    }


@app.get("/jobs/dead-letter")
def get_dead_letter_jobs():

    job_ids = redis_client.lrange(
        "dead_letter_queue",
        0,
        -1
    )

    jobs = []

    for job_id in job_ids:
        job = json.loads(
            redis_client.get(f"job:{job_id}")
        )

        jobs.append(job)

    return {
        "jobs": jobs
    }


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = redis_client.get(f"job:{job_id}")
    if job is None:
        raise HTTPException(
        status_code=404,
        detail="job not found"
    )

    return json.loads(job)



@app.post("/worker/process-next")
def process_next_job():
    job_id = redis_client.lmove(
        "job_queue",
        "processing_queue",
        "LEFT",
        "RIGHT"
    )
    if job_id is None:
        return {
            "message": "no pending jobs"
        }
    job = json.loads(
        redis_client.get(f"job:{job_id}")
    )

    job["status"] = "processing" 
    #isoformat 把datetime轉成字串(方便存到json/redis)
    job["processing_started_at"] = datetime.now(
    timezone.utc
    ).isoformat()

    redis_client.set( 
        f"job:{job_id}", 
        json.dumps(job) 
    )

    if job["simulate_failure"]:
        return {
            "message": "worker crashed",
            "job_id": job_id
        }

    job["status"] = "completed"
    job["result"] = {
        "message": "benchmark simulated"
    }

    redis_client.set(
        f"job:{job_id}",
        json.dumps(job)
    )

    redis_client.lrem(
        "processing_queue",
        1,
        job_id
    )

    return job

@app.get("/metrics")
def metrics():
    job_keys = redis_client.keys("job:*")
    completed_jobs = 0

    for key in job_keys:
        job = json.loads(
            redis_client.get(key)
        )

        if job["status"] == "completed":
            completed_jobs = completed_jobs + 1

    return {
        "total_jobs": len(job_keys),
        "queued_jobs": redis_client.llen("job_queue"),
        "completed_jobs": completed_jobs
    }

@app.post("/worker/recover-stuck")
def recover_stuck_jobs():
    recovered_jobs = []
    #lrange 就是 read list
    job_ids = redis_client.lrange(
        "processing_queue",
        0,
        -1
    )

    for job_id in job_ids:
        job = json.loads(
            redis_client.get(f"job:{job_id}")
        )
        #fromisoformat 把字串轉回datetime 方便做時間運算 
        started_at = datetime.fromisoformat(
            job["processing_started_at"]
        )
        
        now = datetime.now(timezone.utc)
        processing_time = now - started_at
        #建立一個代表30秒的時間差
        timeout = timedelta(seconds=30)

        if job["status"] != "completed" and processing_time > timeout:
            #從左邊數過來第一個符合的刪掉
            redis_client.lrem(
                "processing_queue",
                1,
                job_id
            )

            MAX_RETRY = 3
            job["retry_count"] = job["retry_count"] + 1
            if job["retry_count"] >= MAX_RETRY:
                job["status"] = "failed"
                redis_client.rpush(
                    "dead_letter_queue",
                    job_id
                )
            else:
                job["status"] = "retrying"
                redis_client.rpush(
                    "job_queue",
                    job_id
                )

            redis_client.set(
                f"job:{job_id}",
                json.dumps(job)
            )

            recovered_jobs.append(job_id)

    return {
        "recovered_jobs": recovered_jobs,
        "count": len(recovered_jobs)
    }

@app.post("/test/db")
def test_db():

    session = SessionLocal()

    job = Job(
        job_id=uuid4(),
        benchmark="cpu",
        status="accepted",
        retry_count=0,
        created_at=datetime.now(timezone.utc)
    )

    session.add(job)
    session.commit()

    session.close()

    return {
        "message": "saved"
    }
