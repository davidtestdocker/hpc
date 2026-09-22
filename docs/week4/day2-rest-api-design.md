<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day2 — REST 與端點契約

[上一課](<day1-platform-api-design.md>) · [本週目錄](README.md) · [下一課](<day3-job-identity.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 REST 回應摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

舊文沒有 body 的 POST 是舊版介面；現行 POST /benchmark 需要含 benchmark 字串的 JSON。BenchmarkRequest 沒有 enum／allowlist，列出四個名字也不表示程式會拒絕其他字串。

## 程式／設定與來源

本次核對：[api/main.py](<../../api/main.py>)、[api/worker.py](<../../api/worker.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day2-rest-api-design.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
{"benchmarks":["cpu","memory","disk_io"]}
```

這是舊 GET /benchmarks 清單；目前另有 mpi。名稱出現在清單不等於存在真實效能測試：worker 只有 mpi 提交真實 JobSet，其餘分支回 benchmark simulated。

**仍缺的證據／不能證明的事：** 此課沒有實際 CPU／memory／disk benchmark 數值；不得把 accepted 或清單當成工作執行完成。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 POST 提交／GET 查詢，MPI 由獨立 worker 執行；主 overlay 的手動 /worker/* 端點停用。
> **閱讀順序**：先學本文基礎，再讀[Week4 現行對照與檢核](../learning-guide.md#week4)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week4 Day2 - REST API Design

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理

---

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
