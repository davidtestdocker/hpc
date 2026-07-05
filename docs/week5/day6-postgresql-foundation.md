# Week5 Day6 - PostgreSQL Foundation

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

