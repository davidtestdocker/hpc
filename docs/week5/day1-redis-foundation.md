# Week5 Day1 - Redis Foundation

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

