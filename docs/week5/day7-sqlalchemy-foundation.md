# Week5 Day7 - SQLAlchemy Foundation

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

