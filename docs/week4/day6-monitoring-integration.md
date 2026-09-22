<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day6 — API 監控與健康

[上一課](<day5-dockerize-api.md>) · [本週目錄](README.md) · [下一週](../week5/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

/health 目前只回程序層訊號；/health/redis 才 ping Redis，/metrics 則暴露 HTTP 指標。三者都不等於 MPI 工作完成，也不涵蓋全部資料庫失敗模式。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def health():
    return {
        "status": "healthy"
    }

# 以 ping 檢查 Redis，連線失敗轉成 HTTP 503。
@app.get("/health/redis")
def redis_health():
    try:
        redis_client.ping()

        return {
            "status": "healthy",
            "redis": "connected"
        }

    except ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Redis unavailable"
        )


# 列出 API 支援的 benchmark 名稱。
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week4/day6-monitoring-integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 POST 提交／GET 查詢，MPI 由獨立 worker 執行；主 overlay 的手動 /worker/* 端點停用。
> **閱讀順序**：先學本文基礎，再讀[Week4 現行對照與檢核](../learning-guide.md#week4)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week4 Day6 - Monitoring Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日平台增加什麼？

今天平台加入最基本的 **Observability（可觀測性）** 能力。

平台流程由：

```text
API
```

進化成：

```text
API
 │
 ├── Health
 ├── Logging
 └── Metrics
```

平台開始具備健康檢查、日誌紀錄與基本指標能力。

---

## 今日解決的 Platform Problem

平台除了提供 API 外，還必須回答：

```text
服務還活著嗎？
服務發生什麼事？
目前平台狀態如何？
```

因此需要：

* Health Check
* Logging
* Metrics

---

## 今日知識鏈

```text
Application
      │
      ▼
Observability
      │
 ┌────┼────┐
 ▼    ▼    ▼
Health Logging Metrics
```

---

## 今日實作

### 1. Health Check

新增：

```text
GET /health
```

回傳：

```json
{
  "status": "healthy"
}
```

用途：

* Docker
* Kubernetes
* Load Balancer
* Monitoring System

確認服務是否正常運作。

---

### 2. Logging

新增：

```python
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
```

於 `POST /benchmark` 紀錄：

```python
logger.info(
    "Received benchmark request: %s",
    request.benchmark
)
```

可透過：

```bash
docker compose logs api
```

查看 Application Log。

---

### 3. Metrics

新增：

```text
GET /metrics
```

回傳：

```json
{
  "total_jobs": 2,
  "queued_jobs": 1,
  "completed_jobs": 1
}
```

目前提供：

* total_jobs
* queued_jobs
* completed_jobs

作為平台最基本的運行指標。

---

## 今日驗證

### Health

```bash
curl http://localhost:8000/health
```

結果：

```json
{
  "status": "healthy"
}
```

---

### Logging

建立 Benchmark：

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu"}'
```

查看：

```bash
docker compose logs api
```

成功看到：

```text
INFO:api.main:Received benchmark request: cpu
```

---

### Metrics

```bash
curl http://localhost:8000/metrics
```

結果：

```json
{
  "total_jobs": 2,
  "queued_jobs": 1,
  "completed_jobs": 1
}
```

---

## 今日平台架構

```text
Client
    │
    ▼
FastAPI
    │
    ├──────────────┬──────────────┐
    ▼              ▼              ▼
Health         Logging        Metrics
    │              │              │
    ▼              ▼              ▼
Platform     docker logs      Platform Status
```

---

## 今日學到的重點

* Health 用於確認服務是否可用。
* Logging 用於記錄平台事件，方便除錯與追蹤。
* Metrics 用於量化平台目前狀態。
* Access Log 與 Application Log 是不同層級的資訊。
* Observability 是平台設計的重要基礎，而不只是監控工具。

---

## 它最後會變成平台哪一部分？

今天完成的是 **Observability Foundation**。

後續將演進成：

```text
Health
      ↓
Metrics
      ↓
Prometheus
      ↓
Grafana
      ↓
Alertmanager
      ↓
Performance Dashboard
```

Week11 將把今天的 Metrics 接入 Prometheus 與 Grafana，形成完整監控平台。

---

## Interview

### Q1：Health、Logging、Metrics 三者有什麼差別？

* Health：確認服務是否健康、是否可提供服務。
* Logging：記錄事件與錯誤，協助除錯。
* Metrics：提供可量化的系統狀態與趨勢，供監控系統分析。

---

### Q2：為什麼平台需要 Metrics，而不能只看 Log？

Log 適合追查單一事件；Metrics 適合持續觀察系統狀態，例如 Job 數量、Queue 長度與完成數，可直接用於儀表板、告警與容量分析。
