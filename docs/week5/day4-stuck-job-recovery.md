<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day4 — 卡住與重啟接續

[上一課](<day3-reliable-worker-state-machine.md>) · [本週目錄](README.md) · [下一課](<day5-retry-strategy-and-deadletter-que.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

程序停止時，Kubernetes 工作可能繼續執行。恢復後 worker 重新掃 record，依固定 JobSet 名稱取得狀態；鎖過期和失去鎖時也要防止不受控寫入。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def tick():
    """逐筆掃描並取得 lease；單筆例外不阻止本輪繼續處理其他工作。"""
    redis = main.redis_client
    for key in redis.scan_iter(match='job:*', count=100):
        job_id = key.removeprefix('job:')
        if redis.get(f'worker:done:{job_id}'):
            continue
        # 不等待其他持有者；thread_local=False 讓續期執行緒可使用相同 lock token。
        lock = redis.lock(f'worker:lock:{job_id}', timeout=120, blocking=False,
                          thread_local=False)
        if not lock.acquire(blocking=False):
            continue
        finished = threading.Event()
        lost = threading.Event()

        def renew(finished=finished, lock=lock, lost=lost):
            """每 30 秒把 lease 有效期重設為 120 秒；失敗後通知主流程停止發布。"""
            # 預設參數固定本次迴圈的物件，避免執行緒引用到下一筆工作的變數。
            while not finished.wait(30):
                try:
                    lock.extend(120, replace_ttl=True)
                except Exception:
                    logger.exception('Worker lease renewal failed')
                    lost.set()
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week5/day4-stuck-job-recovery.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day4 - Stuck Job Recovery

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [compose.yaml](../../compose.yaml)：本機服務組合

---

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
