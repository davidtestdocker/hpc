<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day4 — Memory queue 的限制

[上一課](<day3-job-identity.md>) · [本週目錄](README.md) · [下一課](<day5-dockerize-api.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史模擬 worker 結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

jobs={} 和 job_queue=[] 是歷史程序內儲存，不是目前實作。現行 API 先 commit PostgreSQL，再以 Redis transaction 發布 record 和 queue；背景 worker 掃描 job records，因此不能套用舊 list FIFO 圖來保證目前工作的執行順序。AUTOMATIC_WORKER=true 時舊 process-next 入口回 409。

## 程式／設定與來源

本次核對：[api/main.py](<../../api/main.py>)、[api/worker.py](<../../api/worker.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day4-memory-queue.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
status = completed
result = benchmark simulated
```

這只證明舊教材記錄了模擬完成，不包含 CPU 耗時或吞吐。現在仍有非 MPI 模擬分支，不能把 completed 一律解讀成真實效能量測。

**仍缺的證據／不能證明的事：** 舊模擬沒有獨立 raw log；程序內 queue 也沒有跨程序共享或重啟持久性。DB 與 Redis 並非同一原子交易。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
