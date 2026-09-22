<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day1 — Redis key、record 與 queue

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-redis-persistence.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

job:<id> 的 JSON 是工作資料，job_queue 是 ID 清單。API 在同一 Redis pipeline transaction 發布兩者，避免 Redis 內只寫一半；但前面的 PostgreSQL commit 不在該交易中。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    with redis_client.pipeline() as pipe:
        pipe.set(f"job:{job_id}", json.dumps(job))
        pipe.rpush('job_queue', job_id)
        pipe.execute()
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
```

## 已有結果與解讀

### 自動工作驗收：已保存的真實結果

日期：2026-09-22T04:58:58.875811+00:00。環境：GKE hpc-gpu-sg，既有單 L4 叢集上的 **CPU MPI**，不是 GPU 訓練。

| 情境 | 保存的結果 | 怎麼解讀 |
|---|---|---|
| 正常工作 `f2d8df72-aef3-48bf-9d6b-6863523daa65` | `completed`；ranks `[0, 1, 2]` | 真實 MPI 程序啟動、完成並自動收回結果 |
| worker 重啟 `a697300a-b267-4554-bdd5-2c82bb9c9eda` | `completed`；同 job 的 JobSet 數 `1` | 停止期间 Kubernetes 已完成，worker 恢復後接續收集 |
| 模擬 dispatch 失敗 `0852fb7b-8efd-4600-b8ac-d4205554f6f3` | `failed`；retry_count `3` | 模擬提交分支耗盡重試，不是 MPI kernel crash |

正常工作的 launcher log 原文摘錄（只省略 SSH known-host warning）：

```text
RANK=0 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-0-0
RANK=1 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-1-0
RANK=2 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-2-0
```

驗收後的 queue 與手動端點結果，取自同份 JSON：

```json
{
  "database_status": {
    "a697300a-b267-4554-bdd5-2c82bb9c9eda": "completed",
    "f2d8df72-aef3-48bf-9d6b-6863523daa65": "completed",
    "0852fb7b-8efd-4600-b8ac-d4205554f6f3": "failed"
  },
  "queues": {
    "job_queue": [],
    "processing_queue": [],
    "dead_letter_queue": [
      "0852fb7b-8efd-4600-b8ac-d4205554f6f3"
    ]
  },
  "manual_endpoint_rejections": {
    "process-next": 409,
    "collect-mpi": 409,
    "recover-stuck": 409
  }
}
```

空 job_queue／processing_queue 表示本次驗收工作已清理；failed ID 留在 dead-letter。409 是自動模式刻意拒絕手動推進端點，並非 API 故障。這些結果不保證跨 DB 原子交易、Redis 全失恢復或 node failover。

來源：[完整原始驗收 JSON](<../evidence/automatic-worker-20260922.json>)。無須再提交一次工作。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week5/day1-redis-foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day1 - Redis Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [compose.yaml](../../compose.yaml)：本機服務組合
- [requirements.txt](../../requirements.txt)

---

## 今日平台增加什麼？

今天平台從 Memory State 演進成 Redis External State。

原本 Week4：

```text
FastAPI
  ├── jobs {}
  └── job_queue []
```

現在 Week5 Day1：

```text
FastAPI
  ├── Redis Key-Value: job:<job_id>
  └── Redis List: job_queue
```

API 不再依賴 Python Memory 保存 Job 與 Queue。

---

## 今日解決的 Platform Problem

Memory Queue 與 Memory Job Storage 只存在 Python Process 裡。

只要 API restart：

```text
jobs = {}
job_queue = []
```

資料就會消失。

因此平台需要把狀態搬到外部服務：

```text
Memory
  ↓
Redis
```

---

## 今日知識鏈

```text
Memory
  ↓
Persistence
  ↓
Key-Value Store
  ↓
Redis
  ↓
External State
  ↓
Stateless API
```

---

## 今日實作

### 1. 新增 Redis Service

`compose.yaml` 新增：

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

驗證：

```bash
docker compose exec redis redis-cli ping
```

結果：

```text
PONG
```

---

### 2. 安裝 Redis Python Client

`requirements.txt` 新增：

```text
redis
```

驗證：

```bash
docker compose exec api python -c "import redis; print('redis client ok')"
```

---

### 3. FastAPI 連 Redis

新增：

```python
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)
```

新增：

```text
GET /health/redis
```

驗證 API 可以透過 Docker Network 連到 Redis。

---

### 4. Redis Queue

Producer 原本使用：

```python
job_queue.append(job_id)
```

改成：

```python
redis_client.rpush("job_queue", job_id)
```

Consumer 原本使用：

```python
job_queue.pop(0)
```

改成：

```python
job_id = redis_client.lpop("job_queue")
```

這代表 Queue 已從 Python List 轉為 Redis List。

---

### 5. Redis Job Storage

原本使用：

```python
jobs[job_id] = job
```

改成：

```python
redis_client.set(
    f"job:{job_id}",
    json.dumps(job)
)
```

查詢時使用：

```python
job = redis_client.get(f"job:{job_id}")
json.loads(job)
```

Job Detail 已從 Memory Dictionary 轉為 Redis Key-Value。

---

### 6. Redis Job Query

`GET /jobs/{job_id}` 改為從 Redis 查詢：

```python
job = redis_client.get(f"job:{job_id}")

if job is None:
    raise HTTPException(
        status_code=404,
        detail="job not found"
    )

return json.loads(job)
```

---

### 7. Redis Job List

`GET /jobs` 改為：

```python
job_keys = redis_client.keys("job:*")

jobs = []

for key in job_keys:
    job = json.loads(redis_client.get(key))
    jobs.append(job)

return {
    "jobs": jobs
}
```

---

### 8. Redis Metrics

`GET /metrics` 改為從 Redis 計算：

```python
total_jobs = len(job_keys)
queued_jobs = redis_client.llen("job_queue")
completed_jobs = completed_jobs
```

---

## 今日驗證

建立 Job：

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu"}'
```

查看 Redis Queue：

```bash
docker compose exec redis redis-cli LRANGE job_queue 0 -1
```

處理 Job：

```bash
curl -X POST http://localhost:8000/worker/process-next
```

查詢所有 Jobs：

```bash
curl http://localhost:8000/jobs
```

查詢 Metrics：

```bash
curl http://localhost:8000/metrics
```

---

## 今日平台架構

```text
Client
  ↓
FastAPI
  ↓
Redis
  ├── job_queue
  │     └── Redis List
  │
  └── job:<job_id>
        └── Redis JSON String
```

完整流程：

```text
POST /benchmark
  ↓
Producer
  ↓
Redis SET job:<job_id>
  ↓
Redis RPUSH job_queue
  ↓
POST /worker/process-next
  ↓
Redis LPOP job_queue
  ↓
Redis GET job:<job_id>
  ↓
Update Job
  ↓
Redis SET job:<job_id>
```

---

## 今日 Debug 重點

### 問題：Redis Queue 有 job_id，但 Memory jobs 找不到

錯誤：

```text
KeyError: '<job_id>'
```

原因：

```text
Redis Queue 還保留 job_id
但 API restart 後 memory jobs{} 已清空
```

解法：

```text
Job Storage 也必須搬到 Redis
```

這證明只把 Queue 搬到 Redis 不夠，Job Detail 也必須外部化。

---

## 今日學到的重點

* Redis 可以作為 Queue，也可以作為 Job Storage。
* Queue 使用 Redis List：`RPUSH` / `LPOP`。
* Job Detail 使用 Redis Key-Value：`SET` / `GET`。
* API 不應依賴自己的 Memory 保存平台狀態。
* Stateless API + External State 是現代平台的重要設計。
* Docker Compose 內部服務應使用 service name，例如 `redis`，不是 `localhost`。

---

## 它最後會變成平台哪一部分？

今天完成的是 **Persistent Platform Foundation**。

後續會演進成：

```text
FastAPI
  ↓
Redis Queue
  ↓
Worker
  ↓
PostgreSQL
  ↓
Kubernetes
  ↓
Distributed Benchmark Platform
```

Redis 之後會負責 Queue 與暫存狀態，PostgreSQL 則會負責長期保存 Job、Result、Report。

---

## Interview

### Q1：為什麼 API 要設計成 Stateless？

因為 API Container 可能重啟、重建或水平擴展。如果狀態存在 API Memory，服務重啟後資料會消失。將狀態放到 Redis 等外部服務後，API 可以任意重建，資料仍然保留。

### Q2：Redis 在這個平台中扮演什麼角色？

Redis 目前扮演兩個角色：第一是 Queue，使用 Redis List 保存等待處理的 Job ID；第二是 Job Storage，使用 Key-Value 保存 Job Detail。這讓 Producer、Consumer 和 Query API 可以共享同一份外部狀態。
