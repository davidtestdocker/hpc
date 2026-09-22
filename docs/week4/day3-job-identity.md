<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day3 — Job identity

[上一課](<day2-rest-api-design.md>) · [本週目錄](README.md) · [下一課](<day4-memory-queue.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

UUID 是工作身分，固定 mpi-<job_id> 名稱讓重試可接回同一 JobSet。名稱衝突不自動表示是自己的工作，dispatcher 還核對 owner label。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[api/workloads/dispatcher.py](<../../api/workloads/dispatcher.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
        # create 成功後程序可能中斷。409 時查回同名資源，而不是產生第二個 JobSet。
        # 其他 API 錯誤保持拋出，讓背景 worker 留待下一輪重試。
        if exc.status != 409:
            raise
        response = api.get_namespaced_custom_object(
            group='jobset.x-k8s.io', version='v1alpha2', namespace=NAMESPACE,
            plural='jobsets', name=manifest['metadata']['name'], _request_timeout=15,
        )
        if response.get('metadata', {}).get('labels', {}).get('platform-job-id') != job_id:
            raise RuntimeError('Existing JobSet is not owned by this platform job') from exc

    return response["metadata"]["name"]
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week4/day3-job-identity.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 POST 提交／GET 查詢，MPI 由獨立 worker 執行；主 overlay 的手動 /worker/* 端點停用。
> **閱讀順序**：先學本文基礎，再讀[Week4 現行對照與檢核](../learning-guide.md#week4)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week4 Day3 - Job Identity

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理

---

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
