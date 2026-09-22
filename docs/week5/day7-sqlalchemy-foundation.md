<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day7 — SQLAlchemy Session

[上一課](<day6-postgresql-foundation.md>) · [本週目錄](README.md) · [下一週](../week6/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：有日期的 PostgreSQL 終態核對。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

原文「企業平台不會手寫 SQL」不正確；本專案選 ORM，不表示 SQL 不能用。SQLAlchemy 也不僅 ORM。create_all 只建立缺少的表，不是 schema migration。現行 POST 先 commit PostgreSQL 再發布 Redis，並非跨兩者同一交易，Redis 失敗可能留下 DB-only row。persist_job_status 只改 status，不同步 retry_count，模型也沒有 result 欄位。/test/db 會寫入新資料，不是唯讀健康檢查，失敗路徑沒有 finally 保證 session.close。

## 程式／設定與來源

本次核對：[api/database/connection.py](<../../api/database/connection.py>)、[api/database/models.py](<../../api/database/models.py>)、[api/database/init_db.py](<../../api/database/init_db.py>)、[api/database/session.py](<../../api/database/session.py>)、[api/main.py](<../../api/main.py>)、[api/worker.py](<../../api/worker.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<../evidence/automatic-worker-20260922.json>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
"database_status": {
      "a697300a-b267-4554-bdd5-2c82bb9c9eda": "completed",
      "f2d8df72-aef3-48bf-9d6b-6863523daa65": "completed",
      "0852fb7b-8efd-4600-b8ac-d4205554f6f3": "failed"
    }
```

這是 2026-09-22 GKE hpc-gpu-sg／hpc-platform-dev 的已保存自動 worker 驗收，不是 Week5 舊 Compose 的當日重跑。三筆 DB status 與驗收中的工作終態一致；這只核對 status，不是整列資料、retry_count 或完整結果一致。舊 /test/db 僅有成功敘述，沒有獨立 SELECT log。

**仍缺的證據／不能證明的事：** 沒有跨 DB／Redis 原子性、DB-only row 自動補發或完整結果長期歸檔證據；不能把三筆 status 一致推成所有資料永久一致。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
