<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day5 — Retry 與 dead-letter

[上一課](<day4-stuck-job-recovery.md>) · [本週目錄](README.md) · [下一課](<day6-postgresql-foundation.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：有日期的模擬失敗與 DLQ 結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

新版只有 simulate_failure 分支累計到三次後 failed；真實依賴例外由 tick 記錄並下輪重試，沒有同樣三次上限／退避，不能宣稱已完整避免無限重試。MPI 回報 failed 是另一種終態來源。模擬 dispatch 失敗不是真的殺死 worker 或 MPI process。DLQ 表示目前策略停止處理，不證明錯誤永遠不可修復；也沒有自動告警／重送功能。

## 程式／設定與來源

本次核對：[api/main.py](<../../api/main.py>)、[api/worker.py](<../../api/worker.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<../evidence/automatic-worker-20260922.json>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
"message": "Simulated dispatch failure"
      },
      "retry_count": 3
```

這是 2026-09-22 GKE hpc-gpu-sg／hpc-platform-dev 的已保存自動 worker 驗收，不是 Week5 舊 Compose 的當日重跑。0852fb7b-8efd-4600-b8ac-d4205554f6f3 最終 failed，Redis retry_count=3，dead_letter_queue 保存同一 ID，job_queue 與 processing_queue 均為空。

**仍缺的證據／不能證明的事：** 本份不是 MPI process 故障注入或實際 Kubernetes API 連續失敗測試。retry_count=3 是此模擬的三次失敗計數，不應改述成初次失敗後再重試三次；DB 目前只同步 status，不能拿 Redis 計數當作 PostgreSQL 已核對。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day5 - Retry Strategy and Dead Letter Queue

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [compose.yaml](../../compose.yaml)：本機服務組合

---

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
