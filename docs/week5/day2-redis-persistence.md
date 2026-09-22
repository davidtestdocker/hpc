<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day2 — Redis 持久化

[上一課](<day1-redis-foundation.md>) · [本週目錄](README.md) · [下一課](<day3-reliable-worker-state-machine.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

PVC 使資料能跨 Pod 替換保存，AOF 是 Redis 的持久化機制；磁碟、程序與邏輯資料的故障範圍不同。PVC 不等於離線備份，也不保證任何資料遺失都可恢復。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[helm/redis/templates/deployment.yaml](<../../helm/redis/templates/deployment.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
              mountPath: /data
          {{- end }}
      {{- if .Values.persistence.enabled }}
      volumes:
        - name: redis-data
          persistentVolumeClaim:
            claimName: {{ .Values.persistence.claimName }}
      {{- end }}
```

## 已有結果與解讀

### Redis 持久化：已保存結果

日期：2026-09-21。環境：`gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg`／`hpc-platform-dev`。驗收前所有來源 DB 為空，不是非空資料備份還原。

```json
{
  "passed": true,
  "steps": [
    {
      "time": "2026-09-21T09:24:19.579997+00:00",
      "step": "preconditions passed",
      "source_uid": "1857a5ad-ebd4-4728-bcf1-49d021c738a6",
      "api_replicas": 1
    },
    {
      "time": "2026-09-21T09:24:20.630917+00:00",
      "step": "API stopped; HPA with minReplicas > 0 is inactive at zero replicas"
    },
    {
      "time": "2026-09-21T09:24:22.142971+00:00",
      "step": "writes paused; all databases confirmed empty"
    },
    {
      "time": "2026-09-21T09:24:23.553226+00:00",
      "step": "Redis deployment and new PVC applied"
    },
    {
      "time": "2026-09-21T09:24:41.853190+00:00",
      "step": "Redis ready",
      "pvc_phase": "Bound"
    },
    {
      "time": "2026-09-21T09:24:55.278216+00:00",
      "step": "marker survived Pod replacement; test marker removed"
    },
    {
      "time": "2026-09-21T09:25:12.885888+00:00",
      "step": "API restored; empty-database migration and graceful restart verified"
    }
  ]
}
```

解讀：PVC Bound 後，測試 marker 在 Pod replacement 後仍存在，API 隨後恢復。這證明當次 graceful Pod replacement 的持久化，不等於磁碟遺失、非空遷移或完整災難恢復。無須你再停一次服務。

來源：[原始 Redis 驗收 JSON](<../evidence/redis-persistence-migration-20260921.json>)。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week5/day2-redis-persistence.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day2 - Redis Persistence

> 現行入口（2026-09-21）：[平台部署與 Redis 遷移](../runbooks/platform-bootstrap.md)。已將空 Redis 移至 PVC，並驗證 Pod 替換後測試資料保留；不代表非空資料遷移或 HA。本文以下保留原始學習紀錄。

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

本文記錄 Redis persistence 實驗；目前 Compose 設定不代表已保留當時所有持久化選項。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [compose.yaml](../../compose.yaml)：本機服務組合

---

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
