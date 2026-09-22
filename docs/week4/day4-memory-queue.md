<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day4 — Memory queue 的限制

[上一課](<day3-job-identity.md>) · [本週目錄](README.md) · [下一課](<day5-dockerize-api.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Python list 只在單一程序記憶體中，程序重啟或 API 多副本就無法共享一致的待處理列表。現行以 Redis record 保存工作，worker 掃描 record 接續，不只依賴 queue 中還有 ID。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
                    return

        def guard(lost=lost, lock=lock):
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week4/day4-memory-queue.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 POST 提交／GET 查詢，MPI 由獨立 worker 執行；主 overlay 的手動 /worker/* 端點停用。
> **閱讀順序**：先學本文基礎，再讀[Week4 現行對照與檢核](../learning-guide.md#week4)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week4 Day4 - Memory Queue

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理

---

## 今日平台增加什麼？

今天平台加入 **Memory Queue** 與 **Consumer**。

平台流程由：

```text
POST /benchmark
    ↓
建立 Job
```

進化成：

```text
POST /benchmark
    ↓
Producer
    ↓
Job Storage
    ↓
Memory Queue
    ↓
Consumer
    ↓
Benchmark Result
```

平台開始具備最基本的非同步任務處理流程。

---

## 今日解決的 Platform Problem

如果平台收到大量 Benchmark Request：

```text
Job A
Job B
Job C
```

API 不應等待所有 Benchmark 執行完成才回應 Client。

正確流程應為：

```text
Producer
    ↓
Queue
    ↓
Consumer
```

API 只負責建立 Job，真正執行工作交由 Worker 處理。

---

## 今日知識鏈

```text
Synchronous
      ↓
Asynchronous
      ↓
Producer
      ↓
Consumer
      ↓
Queue
      ↓
Memory Queue
```

---

## 今日實作

### 1. 建立 Job Storage

```python
jobs = {}
```

用途：

* 保存所有 Job
* 使用 `job_id` 快速查詢

---

### 2. 建立 Memory Queue

```python
job_queue = []
```

用途：

* 保存等待執行的 Job ID
* 模擬 Queue（FIFO）

---

### 3. Producer

`POST /benchmark`

建立：

* UUID
* Job
* Job Storage
* Queue

```python
jobs[job_id] = {...}
job_queue.append(job_id)
```

---

### 4. 查詢 API

新增：

```text
GET /jobs
GET /jobs/{job_id}
```

用途：

* 查詢所有 Job
* 查詢單一 Job

不存在的 Job：

```text
404 Not Found
```

而不是：

```text
500 Internal Server Error
```

---

### 5. Consumer

新增：

```text
POST /worker/process-next
```

流程：

```text
Queue
    ↓
取出第一個 Job
    ↓
status = completed
    ↓
寫入 result
```

模擬 Worker 處理 Benchmark。

---

## 今日驗證

建立 Job：

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu"}'
```

處理下一個 Job：

```bash
curl -X POST http://localhost:8000/worker/process-next
```

查詢 Job：

```bash
curl http://localhost:8000/jobs
```

結果：

```text
status = completed
result = benchmark simulated
```

---

## 今日平台架構

```text
Client
      │
POST /benchmark
      │
      ▼
Producer
      │
      ▼
Job Storage (jobs)
      │
      ▼
Memory Queue (job_queue)
      │
      ▼
Worker
      │
      ▼
Benchmark Result
      │
      ▼
GET /jobs
```

---

## 今日學到的重點

* Producer 負責建立 Job。
* Consumer 負責處理 Queue 中的 Job。
* Job Storage 與 Queue 是不同資料結構。
* Queue 採 FIFO（First In, First Out）。
* API 應回傳正確 HTTP 狀態碼，例如不存在的 Job 回傳 404。

---

## 它最後會變成平台哪一部分？

今天完成的是 **平台任務流程（Job Flow）**。

後續會演進成：

```text
Producer
      ↓
Redis Queue
      ↓
Worker
      ↓
Benchmark Engine
      ↓
Database
      ↓
Result API
```

Week5 會把 Memory Queue 換成 Redis Queue，而 API Contract 幾乎不用修改。

---

## Interview

### Q1：為什麼 Job Storage 和 Queue 要分開？

Job Storage 用來保存完整 Job 資訊並提供查詢；Queue 用來管理等待處理的順序。兩者職責不同，因此通常會使用不同的資料結構。

---

### Q2：為什麼不存在的 Job 要回傳 404，而不是 500？

404 表示請求的資源不存在，屬於正常的業務情境；500 則代表伺服器內部發生未預期錯誤。平台應將 `KeyError` 轉換為 `404 Not Found`，提供正確的 HTTP API 語意。
