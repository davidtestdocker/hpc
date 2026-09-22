<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day6 — PostgreSQL 與交易邊界

[上一課](<day5-retry-strategy-and-deadletter-que.md>) · [本週目錄](README.md) · [下一課](<day7-sqlalchemy-foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

DB transaction 只涵蓋 DB 操作；session.commit 成功不會保證之後 Redis 也成功。終態 DB-first 可讓 worker 重試補上 Redis，但不能解決所有雙寫失敗。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def persist_job_status(job_id: str, status: str) -> None:
    """Keep the PostgreSQL status column aligned with the Redis lifecycle state."""
    session = SessionLocal()
    try:
        db_job = session.get(Job, UUID(job_id))
        if db_job is None:
            raise RuntimeError(f"database job not found: {job_id}")
        db_job.status = status
        session.commit()
    finally:
        session.close()


# 掃描已提交 MPI 工作，將 Kubernetes 終態與 launcher rank evidence 回寫平台狀態。
@app.post("/worker/collect-mpi")
def collect_submitted_mpi_jobs():
    if os.getenv('AUTOMATIC_WORKER', 'false').lower() == 'true':
        raise HTTPException(409, 'Automatic worker owns job collection')
    updated_jobs = []
    pending_jobs = []
    errors = []

    # SCAN 逐批走訪 keys，避免 KEYS 在資料量增加後阻塞 Redis。
    for key in redis_client.scan_iter(match="job:*"):
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week5/day6-postgresql-foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day6 - PostgreSQL Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/database/connection.py](../../api/database/connection.py)：資料庫連線
- [api/database/init_db.py](../../api/database/init_db.py)：資料表初始化
- [api/database/models.py](../../api/database/models.py)：ORM 資料表模型
- [api/database/session.py](../../api/database/session.py)：資料庫 Session
- [compose.yaml](../../compose.yaml)：本機服務組合
- [k8s/postgres-service.yaml](../../k8s/postgres-service.yaml)
- [k8s/postgres-statefulset.yaml](../../k8s/postgres-statefulset.yaml)

---

## 今日平台增加什麼

今天的平台新增：

* PostgreSQL Container
* PostgreSQL Volume
* PostgreSQL Database
* Database Schema
* 第一張 Table
* 第一筆 Job Metadata

平台從：

```text
FastAPI
    │
    ▼
Redis
```

演進成：

```text
              FastAPI
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
      Redis            PostgreSQL
   Queue Runtime      Job Metadata
```

---

# Platform Problem

目前平台所有 Job 都存在 Redis：

```text
job_queue
processing_queue
dead_letter_queue
job:<job_id>
```

Redis 很適合：

* Queue
* Cache
* Fast State

但不適合：

* 歷史查詢
* 統計分析
* 報表
* 長期保存

因此企業平台通常會分工：

```text
Redis
    │
    ├─ Queue
    ├─ Runtime State
    └─ Fast Access

PostgreSQL
    │
    ├─ Historical Data
    ├─ Metadata
    ├─ SQL Query
    └─ Reporting
```

---

# 今日知識鏈

```text
Docker Container
        │
        ▼
PostgreSQL Server
        │
        ▼
Database
        │
        ▼
Schema
        │
        ▼
Table
        │
        ▼
Row
```

---

# Hands-on

## 1. 建立 PostgreSQL Container

在 `compose.yaml` 新增：

* PostgreSQL Service
* `postgres_data` Volume

驗證：

```bash
docker compose config
docker compose up -d
docker ps
```

---

## 2. 登入 PostgreSQL

```bash
docker exec -it hpc-ai-benchmark-platform-postgres-1 \
psql -U hpc -d hpc_platform
```

成功看到：

```text
hpc_platform=#
```

---

## 3. 查看 Databases

```sql
\l
```

確認：

```text
hpc_platform
postgres
template0
template1
```

理解：

```text
PostgreSQL Server
        │
        ├── hpc_platform
        ├── postgres
        ├── template0
        └── template1
```

---

## 4. 確認目前 Database

```sql
SELECT current_database();
```

結果：

```text
hpc_platform
```

代表目前所有 SQL 都是在 `hpc_platform` Database 中執行。

---

## 5. 查看 Schema

```sql
\dn
```

結果：

```text
public
```

理解：

```text
Server
    │
Database
    │
Schema
```

---

## 6. 建立第一張 Table

```sql
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY,
    benchmark TEXT NOT NULL,
    status TEXT NOT NULL,
    retry_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);
```

驗證：

```sql
\dt
```

看到：

```text
public.jobs
```

---

## 7. 查看 Table Structure

```sql
\d jobs
```

確認：

* UUID Primary Key
* TEXT
* INTEGER
* TIMESTAMPTZ

以及：

```text
jobs_pkey
```

Primary Key Index 已建立。

---

## 8. 插入第一筆資料

```sql
INSERT INTO jobs (
    job_id,
    benchmark,
    status,
    retry_count,
    created_at
)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'cpu',
    'accepted',
    0,
    NOW()
);
```

查詢：

```sql
SELECT * FROM jobs;
```

成功看到第一筆 Job Metadata。

---

# Schema Review

## job_id UUID

用途：

平台唯一識別一筆 Job。

使用 UUID 可讓 API、Redis、PostgreSQL 共用相同 ID。

---

## benchmark TEXT

記錄 Benchmark 類型，例如：

```text
cpu
memory
disk_io
```

---

## status TEXT

記錄 Job Lifecycle：

```text
accepted
processing
retrying
completed
failed
```

---

## retry_count INTEGER

記錄 Retry 次數。

因為需要做數值比較：

```text
retry_count >= MAX_RETRY
```

因此使用 INTEGER。

---

## created_at TIMESTAMPTZ

記錄建立時間。

使用 UTC + Time Zone，方便跨時區平台整合。

---

# 平台架構

```text
               FastAPI
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
      Redis             PostgreSQL
  Queue Runtime        Job Metadata
        │                     │
        ▼                     ▼
   Current State       Historical Data
```

---

# 今日重點

* Redis Persistence 不等於 Database。
* PostgreSQL 是 Job Metadata 的長期保存位置。
* PostgreSQL 架構為：

```text
Server
    ↓
Database
    ↓
Schema
    ↓
Table
    ↓
Row
```

* `public` 是預設 Schema。
* `UUID` 適合作為分散式平台的唯一識別。
* `TIMESTAMPTZ` 適合保存平台事件時間。

---

# Interview Q&A

## Q1：Redis 已經有 RDB、AOF，為什麼還需要 PostgreSQL？

因為 Redis 的 Persistence 是為了恢復資料，不是為了提供關聯式查詢、報表、歷史分析與長期資料管理。

Redis 負責 Runtime State；PostgreSQL 負責 Historical Metadata。

---

## Q2：為什麼 `job_id` 使用 UUID，而不是 Auto Increment？

UUID 可以在不同 API Instance、Worker 或未來的分散式服務中自行產生，不依賴資料庫產號，更適合分散式平台設計。

---

# 今日成果

平台正式加入 Data Layer：

```text
FastAPI
    │
    ├── Redis
    │     ├─ Queue
    │     └─ Runtime State
    │
    └── PostgreSQL
          ├─ Database
          ├─ Schema
          ├─ jobs Table
          └─ Historical Metadata
```

---

# 下一步

Week5 Day7：

開始導入 SQLAlchemy。

建立：

* SQLAlchemy Engine
* ORM Model
* Session
* FastAPI 與 PostgreSQL 整合

讓 API 在建立 Job 時，同時寫入：

```text
Redis（Queue）

+

PostgreSQL（Metadata）
```
