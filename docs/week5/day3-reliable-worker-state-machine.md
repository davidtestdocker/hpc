<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day3 — 現行 worker 狀態機

[上一課](<day2-redis-persistence.md>) · [本週目錄](README.md) · [下一課](<day4-stuck-job-recovery.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

reconcile_job 依狀態推進：processing 也可重入，submit 成功記 submitted，之後 collector 等終態。done marker 在狀態回寫與 queue 清理後設定；queue 並非唯一接續來源。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def reconcile_job(job, guard=lambda: None):
    """推進一筆工作；先記錄提交意圖，終態則先寫 PostgreSQL 再發布 Redis。

    guard 在關鍵寫入前檢查 lease；預設空操作供單元測試直接呼叫使用。
    這是可重試流程，並非兩個資料庫之間的原子交易或 exactly-once 保證。
    """
    redis = main.redis_client
    job_id = job['job_id']
    key = f'job:{job_id}'
    state = job['status']
    guard()
    if state in {'completed', 'failed'}:
        # 終態已發布但尚未標記 done 時，補寫 DB 並接續下方 queue 清理。
        main.persist_job_status(job_id, state)
    elif state in {'accepted', 'retrying', 'processing'}:
        # processing 也可以重入：上次可能已建立 JobSet，卻來不及保存 submitted。
        # dispatcher 會用固定名稱及 owner label 接回同一個 JobSet。
        job['status'] = 'processing'
        redis.set(key, json.dumps(job))
        if job.get('simulate_failure'):
            # 僅此模擬故障累計三次後 failed；真實依賴例外由 tick 記錄並於下輪重試。
            job['retry_count'] = job.get('retry_count', 0) + 1
            job['status'] = 'failed' if job['retry_count'] >= 3 else 'retrying'
            job['result'] = {'message': 'Simulated dispatch failure'}
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week5/day3-reliable-worker-state-machine.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day3 - Reliable Worker State Machine

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [compose.yaml](../../compose.yaml)：本機服務組合

---

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
