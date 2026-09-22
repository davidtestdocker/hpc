<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day2 — REST 與端點契約

[上一課](<day1-platform-api-design.md>) · [本週目錄](README.md) · [下一課](<day3-job-identity.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

GET 查詢通常不應啟動運算；POST /benchmark 表示提交請求。HTTP 200 與 job.status=completed 是不同層的成功，不能把提交回應當成 benchmark 結果。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
@app.post("/benchmark")
def create_benchmark(request: BenchmarkRequest):
    logger.info(
        "Received benchmark request: %s",
        request.benchmark
    )

    # uuid4 產生隨機識別碼；str 轉成字串，作為 Redis key 與回應中的 job_id。
    job_id = str(uuid4())

    job = {
    "job_id": job_id,
    "benchmark": request.benchmark,
    "simulate_failure": request.simulate_failure,
    "status": "accepted",
    "result": None,
    "retry_count": 0
    }

    session = SessionLocal()

    db_job = Job(
        job_id=job_id,
        benchmark=job["benchmark"],
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week4/day2-rest-api-design.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
