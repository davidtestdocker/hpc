# Week5 Day3 - Reliable Worker State Machine

## 今日平台增加什麼

今天的平台從：

```text
Producer
    ↓
job_queue
    ↓
Worker
    ↓
Completed
```

演進成：

```text
Producer
    ↓
Pending Queue
    ↓
Processing Queue
    ↓
Completed
```

新增能力：

* Reliable Queue 基礎
* Processing Queue
* Worker State Machine
* `accepted → processing → completed`
* `processing_started_at`
* 避免 Job 被 Worker 取出後直接消失

---

# Platform Problem

原本 Worker 使用：

```python
redis_client.lpop("job_queue")
```

問題是：

```text
LPOP 成功
    ↓
Job 從 Queue 消失
    ↓
Worker Crash
    ↓
Job Lost
```

Job 會停留在：

```text
status = accepted
```

但已經不在：

```text
job_queue
```

也不在 Worker 手上。

企業平台不能接受這種 Lost Job。

---

# 今日知識鏈

```text
Queue
  ↓
Consumer
  ↓
Worker Failure
  ↓
Lost Job
  ↓
Processing Queue
  ↓
State Machine
  ↓
Reliable Worker
```

---

# Hands-on

## 1. 從 LPOP 改成 LMOVE

原本：

```python
job_id = redis_client.lpop("job_queue")
```

改成：

```python
job_id = redis_client.lmove(
    "job_queue",
    "processing_queue",
    "LEFT",
    "RIGHT"
)
```

目的：

不是把 Job 從 Queue 拿出來後消失，而是：

```text
job_queue
    ↓
processing_queue
```

這是一個 atomic operation。

---

## 2. 建立 Processing State

Worker 取得 Job 後，先將狀態改成：

```python
job["status"] = "processing"

job["processing_started_at"] = datetime.now(
    timezone.utc
).isoformat()
```

目的：

讓 Job Storage 與 Queue 狀態一致。

```text
Job 在 processing_queue
        ↓
status 也應該是 processing
```

---

## 3. Job 完成後移出 Processing Queue

Job 完成後：

```python
job["status"] = "completed"
job["result"] = {
    "message": "benchmark simulated"
}
```

最後從 `processing_queue` 移除：

```python
redis_client.lrem(
    "processing_queue",
    1,
    job_id
)
```

為什麼不是 `LPOP`？

因為多個 Worker 時，完成的 Job 不一定是 processing queue 最左邊那一筆。

`LREM` 可以根據指定的 `job_id` 移除正確的 Job。

---

# 最終 Worker Flow

```text
job_queue
    ↓
LMOVE
    ↓
processing_queue
    ↓
status = processing
    ↓
processing_started_at
    ↓
status = completed
    ↓
LREM processing_queue
    ↓
completed
```

---

# 驗證

建立 Job：

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu"}'
```

處理 Job：

```bash
curl -X POST http://localhost:8000/worker/process-next
```

查詢 Jobs：

```bash
curl http://localhost:8000/jobs
```

驗證結果：

* Job 狀態從 `accepted` 進入 `processing`
* 完成後變成 `completed`
* Job 具有 `processing_started_at`
* `processing_queue` 最後為空

查詢 Processing Queue：

```bash
docker exec -it hpc-ai-benchmark-platform-redis-1 redis-cli LLEN processing_queue
```

預期：

```text
0
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
Redis job_queue
  ↓
LMOVE
  ↓
Redis processing_queue
  ↓
Worker
  ↓
Job Storage
  ↓
Completed
```

---

# 今日重點

* `LPOP` 會造成 Worker Crash 時 Job Lost。
* Reliable Queue 需要 Pending Queue 與 Processing Queue。
* `LMOVE` 可以 atomic 地把 Job 從一個 Queue 搬到另一個 Queue。
* `processing_queue` 是用來追蹤正在被 Worker 處理的 Job。
* Job 狀態要跟 Queue 狀態一致。
* `processing_started_at` 是未來做 Stuck Job Recovery 的基礎。
* Job 完成後必須從 `processing_queue` 移除。
* `LREM` 比 `LPOP` 更適合移除指定 Job。

---

# Interview Q&A

## Q1：為什麼 `LPOP` 不適合做可靠的 Worker Queue？

因為 `LPOP` 會直接把 Job 從 Queue 移除。

如果 Worker 在取出 Job 後 Crash，Job 不在 Queue，也沒有被完成，就會形成 Lost Job。

可靠設計應該先把 Job 搬到 `processing_queue`，避免 Job 消失。

---

## Q2：為什麼需要 `processing_queue`？

`processing_queue` 用來記錄已被 Worker 取走、但尚未完成的 Job。

它讓平台可以知道：

```text
哪些 Job 正在處理
哪些 Job 可能卡住
哪些 Job 未來需要 Recovery
```

這是後續實作 Stuck Job Recovery、Retry、Dead Letter Queue 的基礎。

---

# 今日成果

平台從：

```text
Simple Redis Queue
```

演進成：

```text
Reliable Worker State Machine
```

目前已具備：

```text
accepted
    ↓
processing
    ↓
completed
```

---

# 下一步

Week5 Day4：

實作 **Stuck Job Recovery**。

會處理：

```text
processing_queue
    ↓
timeout detection
    ↓
requeue
    ↓
retry
```

目標是讓 Worker Crash 後，卡在 `processing_queue` 的 Job 可以被重新放回 `job_queue`。

