<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day1 — 平台 API 設計

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-rest-api-design.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

API 負責接收和查詢，不該讓 HTTP 連線等待整個 MPI 工作結束。背景 worker 與 API 分開部署，讓工作生命週期不依附某一次請求；但資料發佈失敗仍須處理。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
        status=job["status"],
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week4/day1-platform-api-design.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 POST 提交／GET 查詢，MPI 由獨立 worker 執行；主 overlay 的手動 /worker/* 端點停用。
> **閱讀順序**：先學本文基礎，再讀[Week4 現行對照與檢核](../learning-guide.md#week4)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week4 Day1 - Platform API Design

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集
- [requirements.txt](../../requirements.txt)

---

## 今日目標

建立 **HPC AI Performance Engineering Platform** 的第一個 API 入口。

平台從只能執行本機 Python Script：

```text
User
  ↓
python monitoring/process_monitor.py
```

進化成：

```text
Client / Browser
        ↓
      HTTP
        ↓
    FastAPI API
        ↓
HPC AI Performance Engineering Platform
```

---

# 今日完成內容

## 1. 建立 Python 套件管理

建立 `requirements.txt`

```text
fastapi
uvicorn[standard]
```

目的：

* 統一管理 Python 相依套件
* Docker Image 可重複建置
* 不依賴 VM 本機環境

---

## 2. 修改 Dockerfile

改為使用：

```dockerfile
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt
```

目的：

* Image 建構時安裝套件
* 不在 Host 安裝 Python 套件
* 建立可重現的 Runtime

---

## 3. 修改 Docker Compose

建立 API Service

```yaml
services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
```

目的：

* 建立 API Container
* 對外開放 8000 Port

---

## 4. 建立第一個 FastAPI

建立：

```text
api/main.py
```

提供第一個 API：

```text
GET /
```

回傳：

```json
{
  "message": "HPC AI Performance Engineering Platform API",
  "status": "running"
}
```

---

## 5. 建立 API Runtime

完成：

```bash
docker compose build
docker compose up -d
```

成功建立：

```text
hpc-ai-benchmark-platform-api
```

---

## 6. 驗證 API

成功驗證：

```bash
curl http://localhost:8000/
```

成功回傳 JSON。

---

## 7. 驗證 Swagger

成功：

```text
http://localhost:8000/docs
```

FastAPI 自動產生 Swagger UI。

---

## 8. 驗證 OpenAPI

成功：

```text
http://localhost:8000/openapi.json
```

確認 API Contract 已建立。

---

# 今日平台架構

```text
Client
    │
 HTTP Request
    │
    ▼
Docker Container
    │
    ▼
Uvicorn
    │
    ▼
FastAPI
    │
    ▼
GET /
    │
    ▼
JSON Response
```

---

# 今日知識重點

```text
Platform
    ↓
API
    ↓
HTTP
    ↓
FastAPI
    ↓
OpenAPI
    ↓
Swagger
```

今天建立的是整個平台的 **API Control Plane**，未來會一路串接：

```text
API
 ↓
Redis Queue
 ↓
Worker
 ↓
Benchmark
 ↓
Monitoring
 ↓
Analysis
```

---

# Interview

### Q1：為什麼平台需要 API，而不是直接執行 Python Script？

因為平台需要讓 Browser、CI/CD、Worker、Dashboard 等外部系統透過 HTTP 呼叫功能，而不是登入主機執行 Python 程式，因此需要 API 作為平台的對外入口。

---

### Q2：`docker compose build` 與 `docker compose up` 有什麼不同？

`docker compose build` 依照 Dockerfile 建立 Image；`docker compose up` 則使用 Image 啟動 Container。Build 是建構執行環境，Up 是執行服務。
