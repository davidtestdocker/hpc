<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day7 — SQLAlchemy Session

[上一課](<day6-postgresql-foundation.md>) · [本週目錄](README.md) · [下一週](../week6/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Session 管理一次資料庫互動，不是全域永久連線。add／commit／close 各有用途，finally 確保關閉；pool_pre_ping、connect timeout、statement timeout 分別防不同等待。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/database/connection.py](<../../api/database/connection.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
from sqlalchemy import create_engine

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres-service"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "hpc_platform"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "hpc"
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week5/day7-sqlalchemy-foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day7 - SQLAlchemy Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/database/connection.py](../../api/database/connection.py)：資料庫連線
- [api/database/init_db.py](../../api/database/init_db.py)：資料表初始化
- [api/database/models.py](../../api/database/models.py)：ORM 資料表模型
- [api/database/session.py](../../api/database/session.py)：資料庫 Session
- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理

---

## 今日平台增加什麼

今天的平台新增：

* SQLAlchemy
* ORM Model
* Database Engine
* Session Factory
* Job ORM
* API 寫入 PostgreSQL

平台從：

```text
FastAPI
    │
    ├── Redis
    └── PostgreSQL
```

演進成：

```text
                 FastAPI
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
        Redis             SQLAlchemy ORM
          │                     │
          │                 Session
          │                     │
          └──────────────► PostgreSQL
```

---

# Platform Problem

Day6 已經建立：

* PostgreSQL
* Database
* Schema
* jobs Table

但是：

所有 SQL 都必須：

```sql
INSERT ...
SELECT ...
UPDATE ...
```

手動執行。

企業平台不會直接在 API 裡手寫 SQL。

需要：

```text
Python Object
        │
        ▼
ORM
        │
        ▼
Database Row
```

---

# 今日知識鏈

```text
Engine
    │
    ▼
Session
    │
    ▼
ORM Model
    │
    ▼
Table
    │
    ▼
Row
```

---

# Hands-on

## 1. 安裝套件

安裝：

```text
SQLAlchemy
psycopg2-binary
```

理解：

```text
SQLAlchemy
        │
        ▼
psycopg2 Driver
        │
        ▼
PostgreSQL
```

---

## 2. 建立 Connection Layer

建立：

```text
api/database/connection.py
```

內容：

* DATABASE_URL
* SQLAlchemy Engine

用途：

建立 PostgreSQL Engine。

---

## 3. 建立 Declarative Base

建立：

```text
api/database/models.py
```

新增：

```python
class Base(DeclarativeBase):
    pass
```

所有 ORM Model 都繼承 Base。

---

## 4. 建立 Job ORM

建立：

```python
class Job(Base):
```

對應：

```text
public.jobs
```

完成：

* job_id
* benchmark
* status
* retry_count
* created_at

Python Class 正式對應 PostgreSQL Table。

---

## 5. 建立 Session Factory

建立：

```text
api/database/session.py
```

內容：

```python
SessionLocal
```

Session 負責：

* add
* commit
* rollback
* close

Engine 與 Session 職責正式分離。

---

## 6. 驗證 ORM

建立：

```text
POST /test/db
```

透過：

```python
session.add(...)
session.commit()
```

成功新增第一筆 ORM Data。

確認：

```sql
SELECT * FROM jobs;
```

成功看到 ORM 建立的資料。

---

## 7. 整合 Benchmark API

修改：

```text
POST /benchmark
```

流程變成：

```text
建立 Job
      │
      ├── Redis Queue
      │
      └── PostgreSQL Metadata
```

建立 Job 時：

* Redis 保存 Queue Runtime
* PostgreSQL 保存 Historical Metadata

---

# 平台架構

```text
                    Client
                       │
                       ▼
                    FastAPI
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
      Redis                     SQLAlchemy
 Queue Runtime                     │
        │                      Session
        │                           │
        ▼                           ▼
 job_queue                    PostgreSQL
 processing_queue              jobs Table
 dead_letter_queue
```

---

# 今日重點

* SQLAlchemy 是 ORM，不是 PostgreSQL Driver。
* psycopg2 負責與 PostgreSQL 通訊。
* Engine 負責建立資料庫連線能力。
* Session 負責 ORM 操作生命週期。
* ORM Model 對應 Database Table。
* API 建立 Job 時，同時寫入 Redis 與 PostgreSQL。
* Redis 與 PostgreSQL 各自負責不同角色，而不是互相取代。

---

# Interview Q&A

## Q1：SQLAlchemy 和 psycopg2 的差別？

SQLAlchemy 是 ORM，負責 Python Object 與 Database Table 的映射，以及 Session 管理。

psycopg2 是 PostgreSQL Driver，負責真正與 PostgreSQL 建立連線並傳送 SQL。

---

## Q2：為什麼需要 Session，而不是直接使用 Engine？

Engine 負責建立連線能力。

Session 則管理一連串資料庫操作，例如新增、修改、提交、回滾與關閉，是 ORM 操作的入口。

---

# 今日成果

平台正式完成三層架構：

```text
Client
    │
    ▼
FastAPI
    │
    ├── Redis
    │      ├─ Queue
    │      ├─ Worker
    │      ├─ Recovery
    │      └─ DLQ
    │
    └── PostgreSQL
           ├─ SQLAlchemy Engine
           ├─ Session
           ├─ ORM Model
           └─ Job Metadata
```

平台現在已具備：

* 非同步 Queue
* Retry Strategy
* Dead Letter Queue
* Persistent Metadata
* ORM Data Layer

---
