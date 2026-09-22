<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day6 — PostgreSQL 與交易邊界

[上一課](<day5-retry-strategy-and-deadletter-que.md>) · [本週目錄](README.md) · [下一課](<day7-sqlalchemy-foundation.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 SQL 示例與資料庫文字摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現行 Job 模型只有 job_id、benchmark、status、retry_count、created_at，沒有 result／report 欄位；完整 MPI 結果仍在 Redis，不能說 DB 已保存全部成果。Redis 可持久化，與 PostgreSQL 的分工是本專案選擇，不是 Redis 絕對不能長期保存。舊 k8s 檔案 namespace 為 hpc-platform，不等於主環境 hpc-platform-dev。Compose 的 postgres 與程式預設 postgres-service 名稱不一致，不能當作目前 API 可直連的證明。

## 程式／設定與來源

本次核對：[api/database/connection.py](<../../api/database/connection.py>)、[api/database/models.py](<../../api/database/models.py>)、[api/database/init_db.py](<../../api/database/init_db.py>)、[api/database/session.py](<../../api/database/session.py>)、[api/main.py](<../../api/main.py>)、[compose.yaml](<../../compose.yaml>)、[k8s/postgres-service.yaml](<../../k8s/postgres-service.yaml>)、[k8s/postgres-statefulset.yaml](<../../k8s/postgres-statefulset.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<day6-postgresql-foundation.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
'11111111-1111-1111-1111-111111111111'
```

這是教材 INSERT 命令的固定 UUID，不是保存的 SELECT 結果。原文寫「成功看到第一筆」，但沒有該列完整輸出；current_database 的文內記錄為 hpc_platform，精確執行日期未保存。

**仍缺的證據／不能證明的事：** 缺舊 INSERT／SELECT 完整 log 與資料庫重啟還原測試；有 volume／PVC 設定不等於已驗證備份還原。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
