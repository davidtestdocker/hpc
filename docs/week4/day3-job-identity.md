<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day3 — Job identity

[上一課](<day2-rest-api-design.md>) · [本週目錄](README.md) · [下一課](<day4-memory-queue.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：UUID 佔位示例，非真實 job 證據。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

UUID4 碰撞機率極低，不是數學上絕不碰撞。每次 POST 都新建 UUID，沒有以 client idempotency key 去重；請求重送仍可能建立多筆工作。Pydantic 在這裡驗證欄位型別，未驗證 benchmark 名稱屬於支援集合。

## 程式／設定與來源

本次核對：[api/main.py](<../../api/main.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day3-job-identity.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

原文 job_id 是佔位符，不能当成已保存的一筆 UUID 執行紀錄。現行程式確實呼叫 uuid4()，但程式存在與當次請求成功是不同證據。

**仍缺的證據／不能證明的事：** 本課沒有真實 job_id 的原始 HTTP capture。缺 body 的 422 記載屬舊文，不冒充本次測試。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
