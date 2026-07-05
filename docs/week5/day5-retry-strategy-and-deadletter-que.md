# Week5 Day5 - Retry Strategy and Dead Letter Queue

## 今日平台增加什麼

今天的平台新增：

* Retry Strategy
* `retry_count`
* `MAX_RETRY`
* `failed` State
* Dead Letter Queue（DLQ）
* Failure Simulation
* DLQ Query API

平台從：

```text
Recovery Worker
    ↓
retrying
    ↓
job_queue
```

演進成：

```text
Recovery Worker
    ↓
retry_count + 1
    ↓
Retry Policy
    ↓
retrying / failed
    ↓
Dead Letter Queue
```

---

# Platform Problem

Day4 已經能把卡在 `processing_queue` 的 Job 找回並重新排隊。

但是如果 Worker 一直失敗：

```text
processing
    ↓
timeout
    ↓
retrying
    ↓
processing
    ↓
timeout
    ↓
retrying
    ↓
...
```

平台會進入 Infinite Retry。

企業平台不能無限重試，必須有：

```text
retry_count
MAX_RETRY
failed
Dead Letter Queue
```

---

# 今日知識鏈

```text
Failure Simulation
    ↓
Recovery
    ↓
Retry Count
    ↓
Max Retry
    ↓
Failed
    ↓
Dead Letter Queue
```

---

# Hands-on

## 1. 新增 retry_count

建立 Job 時加入：

```python
"retry_count": 0
```

讓每一筆 Job 從建立開始就具備 Retry Metadata。

---

## 2. 新增 Failure Simulation

在 Request Model 加入：

```python
simulate_failure: bool = False
```

建立 Job 時保存：

```python
"simulate_failure": request.simulate_failure
```

Worker 在進入 processing 並寫入 `processing_started_at` 後，如果：

```python
job["simulate_failure"]
```

為 True，則回傳：

```python
return {
    "message": "worker crashed",
    "job_id": job_id
}
```

用來模擬 Worker Crash，驗證 Recovery / Retry / DLQ 流程。

---

## 3. Recovery 時累加 retry_count

Recovery Worker 發現 Job 超過 timeout 後：

```python
job["retry_count"] = job["retry_count"] + 1
```

代表這筆 Job 已被重新排隊處理一次。

---

## 4. 加入 MAX_RETRY

設定：

```python
MAX_RETRY = 3
```

判斷：

```python
if job["retry_count"] >= MAX_RETRY:
    job["status"] = "failed"
else:
    job["status"] = "retrying"

    redis_client.rpush(
        "job_queue",
        job_id
    )
```

只有 `retrying` 的 Job 才會重新進入 `job_queue`。

`failed` 的 Job 不會再被 Worker 處理。

---

## 5. 加入 Dead Letter Queue

當 Job 超過最大重試次數：

```python
if job["retry_count"] >= MAX_RETRY:
    job["status"] = "failed"

    redis_client.rpush(
        "dead_letter_queue",
        job_id
    )
```

DLQ 用來保存永遠失敗、需要人工或後續系統處理的 Job。

---

## 6. 新增 DLQ Query API

新增：

```python
@app.get("/jobs/dead-letter")
def get_dead_letter_jobs():
```

從：

```text
dead_letter_queue
```

取得 failed job_id，並回傳完整 Job Metadata。

注意：

`/jobs/dead-letter` 必須放在：

```python
@app.get("/jobs/{job_id}")
```

之前。

否則 FastAPI 會把 `dead-letter` 當成 `job_id`。

---

# 驗證

建立會失敗的 Job：

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu","simulate_failure":true}'
```

執行 Worker：

```bash
curl -X POST http://localhost:8000/worker/process-next
```

結果：

```json
{
  "message": "worker crashed",
  "job_id": "..."
}
```

等待 timeout 後執行 Recovery：

```bash
curl -X POST http://localhost:8000/worker/recover-stuck
```

重複：

```text
process-next
recover-stuck
```

直到：

```json
{
  "status": "failed",
  "retry_count": 3
}
```

查詢 Worker：

```bash
curl -X POST http://localhost:8000/worker/process-next
```

結果：

```json
{
  "message": "no pending jobs"
}
```

代表 failed Job 沒有再回到 `job_queue`。

查詢 DLQ：

```bash
curl http://localhost:8000/jobs/dead-letter
```

結果可看到 failed Jobs：

```json
{
  "jobs": [
    {
      "benchmark": "cpu",
      "simulate_failure": true,
      "status": "failed",
      "retry_count": 3
    }
  ]
}
```

---

# 平台架構

```text
Client
  ↓
FastAPI
  ↓
Producer
  ↓
job_queue
  ↓
Worker
  ↓
processing_queue
  ↓
Recovery Worker
  ↓
retry_count + 1
  ↓
MAX_RETRY Check
  ├── retrying → job_queue
  └── failed → dead_letter_queue
```

---

# 今日重點

* Retry 不能無限執行。
* `retry_count` 是 Job Lifecycle Metadata。
* `MAX_RETRY` 是 Retry Policy。
* `failed` Job 不應再放回 `job_queue`。
* DLQ 是保存永久失敗 Job 的 Queue。
* Failure Simulation 是驗證 Recovery / Retry / DLQ 的重要手段。
* Static Route 要放在 Dynamic Route 前面，例如 `/jobs/dead-letter` 要放在 `/jobs/{job_id}` 前面。

---

# Interview Q&A

## Q1：為什麼需要 Dead Letter Queue？

因為有些 Job 即使重試多次仍然失敗。

DLQ 可以集中保存這些永久失敗的 Job，方便後續人工分析、告警、重新派送或產生報告，而不是讓它們無限回到主 Queue。

---

## Q2：為什麼 failed Job 不應該再放回 job_queue？

`job_queue` 代表等待 Worker 處理的任務。

如果 failed Job 又被放回 `job_queue`，`MAX_RETRY` 就失去意義，平台會繼續重試同一筆已判定失敗的 Job，造成無限循環與資源浪費。

---

# 今日成果

平台從：

```text
Recovery + retrying
```

演進成：

```text
Retry Strategy + Failed State + Dead Letter Queue
```

目前 Queue 已具備：

```text
accepted
  ↓
processing
  ↓
completed
```

以及失敗路徑：

```text
processing
  ↓
timeout
  ↓
retrying
  ↓
failed
  ↓
dead_letter_queue
```

---

# 下一步

Week5 Day6：

進入 PostgreSQL Foundation。

核心問題：

```text
為什麼 Job Metadata 不應該永久只存在 Redis？
```

開始建立：

* PostgreSQL Container
* PostgreSQL Volume
* Database
* Table
* Persistent Job Metadata

