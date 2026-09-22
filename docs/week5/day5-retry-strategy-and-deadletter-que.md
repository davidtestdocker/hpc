<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day5 — Retry 與 dead-letter

[上一課](<day4-stuck-job-recovery.md>) · [本週目錄](README.md) · [下一課](<day6-postgresql-foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

simulate_failure 分支會累計三次後 failed 並進 dead-letter；真實依賴例外由 tick 記錄後下輪重試，不是每種錯誤都三次耗盡。重試需要能辨識同一工作，否則可能產生重複副作用。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
        if job.get('simulate_failure'):
            # 僅此模擬故障累計三次後 failed；真實依賴例外由 tick 記錄並於下輪重試。
            job['retry_count'] = job.get('retry_count', 0) + 1
            job['status'] = 'failed' if job['retry_count'] >= 3 else 'retrying'
            job['result'] = {'message': 'Simulated dispatch failure'}
        elif job['benchmark'] == 'mpi':
            name = main.submit_mpi_jobset(job_id)
            job['status'] = 'submitted'
            job['result'] = {'jobset_name': name, 'message': 'MPI JobSet submitted'}
        else:
            job['status'] = 'completed'
            job['result'] = {'message': 'benchmark simulated'}
        guard()
        main.persist_job_status(job_id, job['status'])
        guard()
        redis.set(key, json.dumps(job))
    elif state == 'submitted' and job['benchmark'] == 'mpi':
        # submitted 只代表已提交；collector 回傳 None 表示尚未取得終態。
        update = main.collect_mpi_jobset(job['result']['jobset_name'])
        if update is None:
            return
        guard()
        main.persist_job_status(job_id, update['status'])
        job.update(update)
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week5/day5-retry-strategy-and-deadletter-que.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
