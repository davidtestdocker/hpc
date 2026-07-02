# Week4 Day3 - Job Identity

## 今日平台增加什麼？

今天平台新增 **Job Identity**。

平台流程由：

```text
Client
  ↓
POST /benchmark
  ↓
Accepted
```

變成：

```text
Client
  ↓
POST /benchmark
  ↓
Request Body
  ↓
Pydantic Validation
  ↓
建立 Job
  ↓
產生 UUID
  ↓
回傳 Job ID
```

平台開始能識別每一個 Benchmark Request。

---

## 今日解決的 Platform Problem

如果平台同時收到多個 Benchmark Request：

```text
Client A
POST /benchmark

Client B
POST /benchmark

Client C
POST /benchmark
```

平台必須知道：

* 哪個 Job 正在執行
* 哪個 Job 已完成
* 哪個 Worker 正在處理
* Client 查詢的是哪一個 Benchmark

因此，每個 Request 都需要唯一的 **Job Identity**。

---

## 今日知識鏈

```text
HTTP Request
      ↓
Benchmark Request
      ↓
Request Body
      ↓
Schema
      ↓
Pydantic
      ↓
Job
      ↓
Identity
      ↓
UUID
```

---

## 今日實作

### 1. 建立 Request Schema

新增：

```python
from pydantic import BaseModel


class BenchmarkRequest(BaseModel):
    benchmark: str
```

目的：

* 定義 Request Body 格式
* 驗證 Client 傳入資料
* 自動產生 OpenAPI Schema

---

### 2. 修改 POST API

修改：

```python
def create_benchmark(request: BenchmarkRequest):
```

FastAPI 會自動：

* 解析 JSON
* 建立 `BenchmarkRequest`
* 驗證資料格式
* 傳入 Handler

---

### 3. 建立 Job Identity

新增：

```python
from uuid import uuid4

job_id = str(uuid4())
```

目的：

* 每個 Benchmark Request 都擁有唯一 ID
* 提供後續 Job 查詢依據
* 避免分散式環境 ID 衝突

---

### 4. 回傳 Job 資訊

回傳：

```json
{
  "message": "benchmark request received",
  "job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "benchmark": "cpu",
  "status": "accepted"
}
```

代表平台已成功建立一個新的 Benchmark Job。

---

## 今日驗證

### 驗證 Request Body 必填

未提供 Body：

```bash
curl -X POST http://localhost:8000/benchmark
```

結果：

```text
422 Unprocessable Entity
```

代表 FastAPI 已完成 Request Validation。

---

### 驗證正常 Request

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu"}'
```

結果：

```json
{
  "message":"benchmark request received",
  "job_id":"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "benchmark":"cpu",
  "status":"accepted"
}
```

成功建立 Benchmark Job。

---

## 今日平台架構

```text
Client
      │
POST /benchmark
      │
      ▼
JSON Request Body
      │
      ▼
Pydantic Schema Validation
      │
      ▼
FastAPI
      │
      ▼
建立 Job
      │
      ▼
UUID
      │
      ▼
JSON Response
```

---

## 今日學到的重點

* Request Body 用來接收 Client 提交的資料。
* Pydantic 負責定義 Schema 與驗證資料。
* FastAPI 會自動將 JSON 轉成 Python Object。
* UUID 提供每個 Benchmark Job 唯一身份。
* `job_id` 是未來查詢 Job 狀態、Queue、Worker、Database 的基礎。

---

## 它最後會變成平台哪一部分？

今天建立的是 **Job Identity**。

後續會一路延伸：

```text
POST /benchmark
      ↓
Job ID
      ↓
Memory Queue
      ↓
Redis Queue
      ↓
Worker
      ↓
Database
      ↓
GET /jobs/{job_id}
      ↓
Benchmark Result
```

Day3 建立的是整個 HPC AI Performance Engineering Platform 的任務識別基礎。

---

## Interview

### Q1：為什麼 Benchmark Request 需要 Job ID？

因為平台可能同時處理大量 Benchmark Request，每個 Request 都必須有唯一身份，才能查詢狀態、追蹤執行流程、對應 Worker 與最終結果。

---

### Q2：Pydantic 在 FastAPI 中負責什麼？

Pydantic 用來定義 API Schema、驗證 Request Body，並將 JSON 自動轉換成 Python 物件，同時提供 OpenAPI Schema 給 Swagger 使用。

