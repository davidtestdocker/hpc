# Week4 Day4 - Memory Queue

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

