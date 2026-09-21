# 平台 API：接收工作、保存初始資料並操作 Redis 佇列；MPI 提交後為 submitted，其他分支仍是模擬結果。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import redis
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from redis.exceptions import ConnectionError

from api.database.models import Job
from api.database.session import SessionLocal
from api.workloads.dispatcher import submit_mpi_jobset

logging.basicConfig(level=logging.INFO)

# 讀取環境變數，未設定時使用第二個引數的預設值。
APP_NAME = os.getenv(
    "APP_NAME",
    "HPC AI Performance Engineering Platform"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
# 讀取環境變數，未設定時使用第二個引數的預設值。
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
#建立一個 Metrics 收集器.攔截 FastAPI 所有 HTTP Request.自動新增：GET /metrics
Instrumentator().instrument(app).expose(app)

# class 定義 BenchmarkRequest 類別；括號內是繼承的父類別。
# 繼承 Pydantic BaseModel，FastAPI 依欄位型別驗證 JSON；simulate_failure 預設為 False。
class BenchmarkRequest(BaseModel):
    benchmark: str
    simulate_failure: bool = False


# 回傳 API 首頁資訊。
# @ 是 decorator：將下方函式註冊為指定 HTTP 方法與路徑的處理函式。
@app.get("/")
def root():
    return {
        "message": "HPC API DEV",
        "status": "running"
    }

# 回傳程序健康狀態；這個端點未檢查所有外部相依服務。
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# 以 ping 檢查 Redis，連線失敗轉成 HTTP 503。
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


# 列出 API 支援的 benchmark 名稱。
@app.get("/benchmarks")
def list_benchmarks():
    return {
        "benchmarks": [
            "cpu",
            "memory",
            "disk_io",
            "mpi"
        ]
    }


# 建立 UUID，保存 Redis 狀態與 DB 初始紀錄，再將 ID 加入待處理佇列。
@app.post("/benchmark")
def create_benchmark(request: BenchmarkRequest):
    logger.info(
        "Received benchmark request: %s",
        request.benchmark
    )

    # uuid4 產生隨機識別碼；str 轉成字串，作為 Redis key 與回應中的 job_id。
    job_id = str(uuid4())

    job = {
    "job_id": job_id,
    "benchmark": request.benchmark,
    "simulate_failure": request.simulate_failure,
    "status": "accepted",
    "result": None,
    "retry_count": 0
    }

    # dumps 把 Python 資料轉成 JSON 字串，供 Redis 保存。
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

    # add 將 ORM 物件加入本次 Session，等待 flush／commit 寫入。
    session.add(db_job)
    # commit 提交資料庫交易，讓新增內容正式保存。
    session.commit()
    # close 釋放 Session 持有的連線資源。
    session.close()

    # RPUSH 從清單右側加入工作 ID；搭配從左側取出形成先進先出。
    redis_client.rpush(
        "job_queue",
        job_id
    )
    return {
        "message": "benchmark request received",
        "job_id": job_id,
        "benchmark": request.benchmark,
        "status": "accepted",
        "next_step": f"Check job status at GET /jobs/{job_id}"
    }

#第八週要改成scan而不是keys方式
# 讀取 job:* 對應的工作；KEYS 會掃描鍵空間，資料量大時有阻塞風險。
@app.get("/jobs")
def get_jobs():

    job_keys = redis_client.keys("job:*")

    jobs = []

    for key in job_keys:
        # loads 把 JSON 字串還原成 Python 字典或清單。
        job = json.loads(
            redis_client.get(key)
        )
        jobs.append(job)

    return {
        "jobs": jobs
    }


# 讀取超過重試門檻的工作 ID，再查詢每筆工作內容。
@app.get("/jobs/dead-letter")
def get_dead_letter_jobs():

    job_ids = redis_client.lrange(
        "dead_letter_queue",
        0,
        -1
    )

    jobs = []

    for job_id in job_ids:
        # loads 把 JSON 字串還原成 Python 字典或清單。
        job = json.loads(
            redis_client.get(f"job:{job_id}")
        )

        jobs.append(job)

    return {
        "jobs": jobs
    }


# 依 URL 傳入的 job_id 查詢；找不到時回傳 HTTP 404。
@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = redis_client.get(f"job:{job_id}")
    if job is None:
        raise HTTPException(
        status_code=404,
        detail="job not found"
    )

    return json.loads(job)



# 一次處理一筆佇列工作；需由 HTTP 手動觸發，尚非背景 worker daemon。
@app.post("/worker/process-next")
def process_next_job():
    # LMOVE 原子地把 ID 從待處理佇列移到處理中佇列，避免先取出再放入的空窗。
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
    # loads 把 JSON 字串還原成 Python 字典或清單。
    job = json.loads(
        redis_client.get(f"job:{job_id}")
    )

    job["status"] = "processing" 
    #isoformat 把datetime轉成字串(方便存到json/redis)
    job["processing_started_at"] = datetime.now(
    timezone.utc
    ).isoformat()

    # dumps 把 Python 資料轉成 JSON 字串，供 Redis 保存。
    redis_client.set( 
        f"job:{job_id}", 
        json.dumps(job) 
    )

    # 提早 return 模擬 worker 中斷，保留 processing_queue 項目供逾時恢復實驗。
    if job["simulate_failure"]:
        return {
            "message": "worker crashed",
            "job_id": job_id
        }

    if job["benchmark"] == "mpi":
        jobset_name = submit_mpi_jobset(job_id)

        # submitted 僅表示 JobSet 已建立；目前沒有 watcher 回寫 MPI 的最終成功／失敗狀態。
        job["status"] = "submitted"
        job["result"] = {
            "message": "MPI JobSet submitted",
            "jobset_name": jobset_name
        }
    else:
        job["status"] = "completed"
        job["result"] = {
            "message": "benchmark simulated"
        }

    # dumps 把 Python 資料轉成 JSON 字串，供 Redis 保存。
    redis_client.set(
        f"job:{job_id}",
        json.dumps(job)
    )

    # LREM 移除符合的 ID；count=1 表示從左側移除第一個符合項目。
    redis_client.lrem(
        "processing_queue",
        1,
        job_id
    )

    return job

# 統計 Redis 中的工作數量與已完成數。
@app.get("/job-metrics")
def job_metrics():
    job_keys = redis_client.keys("job:*")
    completed_jobs = 0

    for key in job_keys:
        # loads 把 JSON 字串還原成 Python 字典或清單。
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

# 依處理時間判斷逾時，移回待處理佇列或送入死信佇列。
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
        # loads 把 JSON 字串還原成 Python 字典或清單。
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
            # LREM 移除符合的 ID；count=1 表示從左側移除第一個符合項目。
            redis_client.lrem(
                "processing_queue",
                1,
                job_id
            )

            # 每次逾時恢復增加 retry_count；達到門檻送入 dead_letter_queue，不再重新排隊。
            MAX_RETRY = 3
            job["retry_count"] = job["retry_count"] + 1
            if job["retry_count"] >= MAX_RETRY:
                job["status"] = "failed"
                # RPUSH 從清單右側加入工作 ID；搭配從左側取出形成先進先出。
                redis_client.rpush(
                    "dead_letter_queue",
                    job_id
                )
            else:
                job["status"] = "retrying"
                # RPUSH 從清單右側加入工作 ID；搭配從左側取出形成先進先出。
                redis_client.rpush(
                    "job_queue",
                    job_id
                )

            # dumps 把 Python 資料轉成 JSON 字串，供 Redis 保存。
            redis_client.set(
                f"job:{job_id}",
                json.dumps(job)
            )

            recovered_jobs.append(job_id)

    return {
        "recovered_jobs": recovered_jobs,
        "count": len(recovered_jobs)
    }

# 新增測試資料以檢查 DB 寫入；此端點會真的寫入資料庫。
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

    # add 將 ORM 物件加入本次 Session，等待 flush／commit 寫入。
    session.add(job)
    # commit 提交資料庫交易，讓新增內容正式保存。
    session.commit()

    # close 釋放 Session 持有的連線資源。
    session.close()

    return {
        "message": "saved"
    }
