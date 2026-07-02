# Week4 Day2 - REST API Design

## 今日平台增加什麼？

今天平台從單純的健康檢查 API：

```text
GET /
```

進化成具備 Benchmark API 語意的入口：

```text
GET /benchmarks
POST /benchmark
```

這代表平台開始有「查詢 Benchmark 能力」與「提交 Benchmark Request」的 API Contract。

---

## 今日解決的 Platform Problem

真正的 HPC AI Performance Engineering Platform 不能只靠人工執行 Python Script。

平台需要讓外部系統透過 HTTP 操作：

```text
Client
  ↓
API
  ↓
Benchmark Platform
```

因此今天建立 GET 與 POST 的基本語意：

```text
GET  = 查詢資源
POST = 建立請求 / 提交任務
```

---

## 今日知識鏈

```text
HTTP
  ↓
Method
  ↓
GET / POST
  ↓
Resource
  ↓
RESTful Design
  ↓
Request
  ↓
Response
  ↓
Benchmark API Contract
```

---

## 今日實作

### 1. 保留平台根入口

```text
GET /
```

用途：

```text
確認 API Server 正常運作
```

---

### 2. 新增 Benchmark 查詢 API

```text
GET /benchmarks
```

用途：

```text
查詢目前平台支援哪些 Benchmark 類型
```

回傳：

```json
{
  "benchmarks": [
    "cpu",
    "memory",
    "disk_io"
  ]
}
```

這是查詢資源，不是執行 Benchmark。

---

### 3. 新增 Benchmark Request API

```text
POST /benchmark
```

用途：

```text
提交一個 Benchmark Request
```

回傳：

```json
{
  "message": "benchmark request received",
  "status": "accepted",
  "next_step": "job identity will be added in Day3"
}
```

今天只建立 API Contract，不建立 UUID、Job Model、Queue、Redis 或 Worker。

---

## 今日 API 程式

```python
from fastapi import FastAPI

app = FastAPI(
    title="HPC AI Performance Engineering Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "HPC AI Performance Engineering Platform API",
        "status": "running"
    }


@app.get("/benchmarks")
def list_benchmarks():
    return {
        "benchmarks": [
            "cpu",
            "memory",
            "disk_io"
        ]
    }


@app.post("/benchmark")
def create_benchmark():
    return {
        "message": "benchmark request received",
        "status": "accepted",
        "next_step": "job identity will be added in Day3"
    }
```

---

## 今日驗證

重新 Build 並啟動：

```bash
docker compose up -d --build
```

測試查詢 Benchmark 類型：

```bash
curl http://localhost:8000/benchmarks
```

結果：

```json
{"benchmarks":["cpu","memory","disk_io"]}
```

測試提交 Benchmark Request：

```bash
curl -X POST http://localhost:8000/benchmark
```

結果：

```json
{"message":"benchmark request received","status":"accepted","next_step":"job identity will be added in Day3"}
```

---

## 今日平台架構

```text
Client
  ↓
HTTP Request
  ↓
FastAPI
  ↓
GET /benchmarks
  ↓
查詢 Benchmark 類型
```

```text
Client
  ↓
HTTP Request
  ↓
FastAPI
  ↓
POST /benchmark
  ↓
接收 Benchmark Request
```

---

## 今日學到的重點

* GET 用來查詢資源。
* POST 用來提交請求或建立資源。
* REST API 應該以 Resource 為核心，而不是以 Function 名稱為核心。
* `GET /benchmarks` 代表查詢 Benchmark 資源集合。
* `POST /benchmark` 代表提交新的 Benchmark Request。
* `status: accepted` 比 `completed` 更符合未來 Queue / Worker 架構。
* 今天只建立 API Contract，不提前實作 Day3 的 Job Identity 或 Day4 的 Queue。

---

## 它最後會變成平台哪一部分？

今天建立的是 Benchmark API Contract 的雛形。

未來會演進成：

```text
Client
  ↓
POST /benchmark
  ↓
API Server
  ↓
Job Identity
  ↓
Queue
  ↓
Worker
  ↓
Benchmark Engine
  ↓
Performance Analysis
```

今天的 `POST /benchmark` 之後會接上 UUID、Job Model、Memory Queue、Redis Queue、Worker、Database 與 Benchmark Engine。

---

## Interview

### Q1：GET 和 POST 在平台 API 設計中有什麼差別？

GET 用來查詢資源，不應該改變平台狀態；POST 用來提交請求或建立資源，通常會讓平台產生新的任務或狀態變化。

在本平台中，`GET /benchmarks` 是查詢支援的 Benchmark 類型，`POST /benchmark` 則是提交新的 Benchmark Request。

### Q2：為什麼 `POST /benchmark` 回傳 `accepted`，而不是 `completed`？

因為在真正的平台架構中，API 不應該直接執行 Benchmark。

API 只負責接收請求，後續會交給 Queue、Worker 與 Benchmark Engine 處理。因此 `accepted` 代表請求已被平台接收，但尚未完成執行，這符合非同步平台設計。

