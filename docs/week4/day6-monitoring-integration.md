# Week4 Day6 - Monitoring Integration

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

