# Week5 Day2 - Redis Persistence

## 今日平台增加什麼

今天的平台正式從：

```text
Stateless API
        │
        ▼
Redis (Memory Only)
```

演進成：

```text
Stateless API
        │
        ▼
Redis
        │
        ├── RDB
        ├── AOF
        └── Docker Volume
```

新增能力：

* Redis Persistence
* RDB Snapshot
* AOF Persistence
* Docker Named Volume
* Basic Redis Error Handling

今天的重點不是新增 API，而是讓平台開始具備 **資料可靠性（Reliability）**。

---

# Platform Problem

Week5 Day1 完成後，平台所有狀態都已經存放在 Redis：

```text
job:<job_id>

job_queue
```

但是 Redis 是一個 Container。

如果直接：

```bash
docker compose down
docker compose up -d
```

Container 被刪除後重新建立，Redis Memory 也會一起消失，導致：

* Queue 消失
* Job Status 消失
* Benchmark Result 消失
* Metrics 基礎資料消失

因此今天真正要解決的問題不是 Redis，而是：

> **Platform State 如何脫離 Container 的生命週期。**

---

# 今日知識鏈

```text
Application State
        │
        ▼
Redis Memory
        │
        ▼
Persistence
        │
        ├── RDB
        └── AOF
        │
        ▼
Docker Volume
        │
        ▼
Platform Reliability
```

---

# Hands-on

### 1. 驗證 Redis Persistence

確認：

* Redis Data Directory：`/data`
* RDB File：`dump.rdb`

並手動執行：

```bash
redis-cli SAVE
```

理解：

```text
Redis Memory
        │
        ▼
Snapshot
        │
        ▼
dump.rdb
```

---

### 2. 建立 Docker Named Volume

修改 `compose.yaml`：

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data

volumes:
  redis_data:
```

目的：

將 Redis 的 `/data` 掛載到 Docker Named Volume，讓資料不再跟著 Container 一起消失。

---

### 3. 啟用 AOF

啟用：

```text
appendonly yes
```

並確認：

```text
appendonlydir
```

已建立。

新增 Benchmark 後：

```text
appendonly.aof.1.incr.aof
```

由 0 Bytes 變成非 0 Bytes，代表 Redis 已開始記錄新的寫入操作。

---

### 4. Redis Error Handling

當 Redis 停止時：

原本：

```text
500 Internal Server Error
```

改善後：

```text
503 Service Unavailable
```

代表 API 已開始具備最基本的 Dependency Failure Handling。

---

# 驗證

本日完成以下驗證：

* ✅ `docker compose restart redis` 後資料仍存在。
* ✅ `docker compose down && up` 後，透過 Docker Volume 成功保留資料。
* ✅ 成功建立 `dump.rdb`。
* ✅ 成功啟用 AOF，並觀察到 `appendonlydir`。
* ✅ 建立新 Job 後，AOF Increment File 持續成長。
* ✅ Redis 停止時，`/health/redis` 正確回傳 HTTP 503。
* ✅ Redis 恢復後，`/health/redis` 回復 Healthy。

---

# 平台架構

```text
                Client
                   │
                   ▼
              FastAPI API
                   │
                   ▼
             Redis Client
                   │
                   ▼
             Redis Server
             ┌─────────────┐
             │             │
             ▼             ▼
        Redis Memory    Persistence
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
             dump.rdb           appendonlydir
                 │
                 ▼
      Docker Named Volume
```

---

# 今日重點

* Redis Memory 並不是可靠儲存。
* RDB 是 Snapshot，可能遺失最近尚未 Snapshot 的資料。
* AOF 是 Operation Log，可降低資料遺失風險。
* Docker Volume 保護的是 Redis `/data`，而不是 Redis Memory。
* `appendfsync everysec` 是企業最常見的效能與可靠性折衷方案。
* Dependency Failure 應轉換成正確的 HTTP Status，而不是直接回傳 500。

---

# Interview Q&A

### Q1：RDB、AOF 與 Docker Volume 各自負責什麼？

**回答：**

* **RDB**：定期將 Redis Memory 建立 Snapshot（`dump.rdb`）。
* **AOF**：持續記錄 Redis 寫入指令（Operation Log）。
* **Docker Volume**：保存 Redis `/data`，讓 Container 重建後仍可保留 RDB 與 AOF。

三者負責的層次不同：

```text
Redis Memory
        │
        ├── RDB
        ├── AOF
        │
        ▼
Docker Volume
```

---

### Q2：為什麼 Redis 掛掉時應回傳 503，而不是 500？

**回答：**

500 代表 API 本身發生未預期錯誤。

Redis 掛掉並不是 API 寫壞，而是依賴服務（Dependency）不可用，因此應回傳：

```text
503 Service Unavailable
```

讓 Client 能明確知道目前是外部服務不可用，而不是程式發生 Bug。

---

# 下一步

Week5 Day3：

開始建立更可靠的 Queue 與 Job State Management，讓 Producer / Consumer 不只是能運作，而是真正具備企業平台需要的可靠性與可恢復能力。

