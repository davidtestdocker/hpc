<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day6 — API 監控與健康

[上一課](<day5-dockerize-api.md>) · [本週目錄](README.md) · [下一週](../week5/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 health／log／metrics 摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現行 /metrics 由 Instrumentator 提供 Prometheus 格式；工作數量 JSON 位於 /job-metrics，不能照舊文向 /metrics 期待 JSON。/health 固定回 healthy，只表示路由可回應；Redis 檢查在 /health/redis，未等同 PostgreSQL、worker、Kubernetes 全鏈路健康。process_monitor.py 未接入這些端點，也不提供這裡的 jobs 指標。

## 程式／設定與來源

本次核對：[api/main.py](<../../api/main.py>)、[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day6-monitoring-integration.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
INFO:api.main:Received benchmark request: cpu
```

這行是舊文保存的 application log，僅表示收到請求，不證明工作執行成功。舊文另記 total_jobs=2、queued_jobs=1、completed_jobs=1，是當時數值，不是即時狀態。

**仍缺的證據／不能證明的事：** 缺這次教材對應的原始 HTTP headers、完整 application log 與即時依賴檢查；不以後來的實驗倒填成本課當時結果。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
