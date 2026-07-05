# Week5 Day4 - Stuck Job Recovery

## 今日平台增加什麼

今天的平台新增：

* Recovery Worker
* Recovery Policy
* Timeout Detection
* `retrying` State

平台能力從：

```text
Pending Queue
    ↓
Processing Queue
    ↓
Completed
```

演進成：

```text
Pending Queue
    ↓
Processing Queue
    ↓
Worker Crash
    ↓
Recovery Worker
    ↓
Retrying
    ↓
Pending Queue
```

---

# Platform Problem

Day3 已經解決：

```text
Worker Crash
    ↓
Job 不會 Lost
```

但是：

```text
Job 卡在 processing_queue
```

仍然沒有任何 Worker 會再處理它。

如果沒有 Recovery 機制：

```text
Processing Queue
    ↓
永遠卡住
```

平台就無法自我修復（Self Recovery）。

---

# 今日知識鏈

```text
Processing Queue
    ↓
processing_started_at
    ↓
Timeout Detection
    ↓
Recovery Policy
    ↓
Retrying
```

---

# Hands-on

## 1. 建立 Recovery API

新增：

```text
POST /worker/recover-stuck
```

功能：

* 掃描 `processing_queue`
* 取得 Processing 中的 Job

---

## 2. 加入 Timeout Detection

利用：

```python
processing_started_at
```

計算：

```text
現在時間
    ↓
開始時間
    ↓
Processing Duration
```

設定：

```text
Timeout = 30 秒
```

只有超過 Timeout 才允許 Recovery。

---

## 3. Recovery Policy

符合條件：

```text
status != completed

AND

processing_time > timeout
```

Recovery Worker：

* 從 `processing_queue` 移除
* 放回 `job_queue`
* 更新狀態為 `retrying`

---

# 驗證

建立 Job：

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu"}'
```

模擬 Worker Crash：

```redis
LMOVE job_queue processing_queue LEFT RIGHT
```

確認：

```redis
LRANGE processing_queue 0 -1
```

執行 Recovery：

```bash
curl -X POST http://localhost:8000/worker/recover-stuck
```

再次執行 Worker：

```bash
curl -X POST http://localhost:8000/worker/process-next
```

確認：

```bash
curl http://localhost:8000/jobs
```

驗證：

* Job 被成功 Recovery
* Job 回到 `job_queue`
* Worker 可再次完成 Job
* 最終狀態為 `completed`

---

# 平台架構

```text
                 Client
                    │
                    ▼
                 FastAPI
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Redis job_queue    Redis processing_queue
          │                   │
          ▼                   │
        Worker                │
          │                   │
          ├────────Crash──────┘
          │
          ▼
    Recovery Worker
          │
          ▼
      retrying
          │
          ▼
      job_queue
```

---

# 今日重點

* Recovery Worker 負責找回卡住的 Job。
* `processing_started_at` 是 Timeout 判斷的依據。
* Recovery 必須有 Policy，而不是看到 Processing Job 就立即回收。
* `retrying` 比重新改回 `accepted` 更能反映 Job 的生命週期。
* Recovery 是 Reliable Queue 的核心能力之一。

---

# Interview Q&A

## Q1：為什麼 Recovery 不能直接回收所有 Processing Job？

因為 Worker 可能仍在正常執行。

如果沒有 Timeout，就可能造成兩個 Worker 同時處理同一個 Job（Duplicate Processing）。

---

## Q2：為什麼需要 `retrying` 狀態，而不是改回 `accepted`？

`accepted` 代表第一次進入系統。

Recovery 後的 Job 已經執行過一次，因此使用 `retrying` 能更準確表示 Job 的生命週期，也方便後續加入 Retry Count 與 Failed 狀態。

---

# 下一步

Week5 Day5：

實作 Retry Strategy。

新增：

* `retry_count`
* `max_retry`
* `failed`
* Dead Letter Queue（DLQ）

讓平台具備完整的 Job Failure Handling 能力。

