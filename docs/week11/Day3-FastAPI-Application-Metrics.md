# Week11 Day3 - FastAPI Application Metrics

---

# 今日目標

今天完成以下內容：

- FastAPI 整合 Prometheus Metrics
- 建立 `/metrics`
- Prometheus 成功 Scrape API
- API Target 由 DOWN 變成 UP
- 理解 Prometheus Instrumentator
- 理解 Application Metrics

---

# 今日平台架構

```text
                   Client
                      │
                      ▼
                FastAPI API
           ┌─────────┴─────────┐
           │                   │
           ▼                   ▼
      REST API            /metrics
                               │
                               ▼
                         Prometheus
                               │
                               ▼
                          Targets = UP
```

---

# 一、安裝 Prometheus Instrumentator

requirements.txt 新增：

```text
prometheus-fastapi-instrumentator
```

作用：

提供 FastAPI 與 Prometheus 整合。

---

# 二、FastAPI 整合 Metrics

新增：

```python
from prometheus_fastapi_instrumentator import Instrumentator
```

建立 FastAPI 後：

```python
app = FastAPI(
    title=APP_NAME,
    version="0.1.0"
)

Instrumentator().instrument(app).expose(app)
```

---

# 三、Instrumentator 做了什麼

```python
Instrumentator()
```

建立 Metrics 收集器。

---

```python
.instrument(app)
```

攔截所有 FastAPI Request。

例如：

```text
GET /

GET /jobs

POST /benchmark

GET /health
```

全部都會自動統計。

---

```python
.expose(app)
```

自動建立：

```text
GET /metrics
```

不用自行撰寫：

```python
@app.get("/metrics")
```

---

# 四、原本 Metrics API 衝突

原本：

```python
@app.get("/metrics")
def metrics():
```

回傳：

```json
{
    "total_jobs": 10,
    "queued_jobs": 2,
    "completed_jobs": 8
}
```

屬於：

Business Metrics API。

Instrumentator 也會建立：

```text
/metrics
```

因此會發生：

Route 衝突。

---

修改為：

```python
@app.get("/job-metrics")
def job_metrics():
```

結果：

```text
/metrics
```

Prometheus 使用。

```text
/job-metrics
```

保留原本 JSON 統計功能。

---

# 五、GitOps 部署流程

修改完成後：

```bash
git add .

git commit

git pull --rebase origin master

git push origin master
```

GitHub Actions：

```text
Build Image

↓

Push Artifact Registry

↓

更新 values-dev.yaml

↓

Argo CD Sync

↓

Rolling Update API
```

---

# 六、Prometheus Target

原本：

```text
api

DOWN
```

錯誤：

```text
unsupported Content-Type

application/json
```

原因：

API 沒有 Prometheus Metrics。

---

修改後：

```text
api

UP
```

代表：

Prometheus 已成功：

```text
GET /metrics
```

並成功解析 Metrics。

---

# 七、驗證 Metrics

使用：

```bash
kubectl port-forward \
-n hpc-platform-dev \
svc/api-service \
8000:8000
```

瀏覽：

```text
http://localhost:8000/metrics
```

成功看到：

```text
# HELP ...

# TYPE ...

python_gc_objects_collected_total

process_virtual_memory_bytes

process_cpu_seconds_total
```

代表：

FastAPI 已成功輸出 Prometheus Metrics。

---

# 八、為什麼不是 JSON

以前：

```text
Content-Type

application/json
```

例如：

```json
{
    "status": "healthy"
}
```

Prometheus：

不能解析。

---

現在：

```text
Content-Type

text/plain
```

例如：

```text
# HELP process_cpu_seconds_total

# TYPE process_cpu_seconds_total counter

process_cpu_seconds_total 0.18
```

Prometheus：

可以解析。

因此：

```text
Target

↓

UP
```

---

# 九、目前 Application Metrics

目前已自動產生：

Python Runtime：

```text
python_gc_objects_collected_total

python_gc_collections_total

python_info
```

---

Process：

```text
process_cpu_seconds_total

process_virtual_memory_bytes

process_resident_memory_bytes

process_open_fds
```

---

HTTP：

Instrumentator 自動收集：

- HTTP Request Count
- HTTP Status Code
- Request Duration
- In Progress Requests

之後可直接使用 PromQL 查詢。

---

# 十、平台目前能力

目前平台：

```text
FastAPI

├── REST API

├── /health

├── /benchmark

├── /jobs

├── /job-metrics

└── /metrics
```

Prometheus：

```text
Prometheus

↓

GET /metrics

↓

Application Metrics

↓

TSDB
```

---

# 十一、目前 Observability 架構

```text
                 Client
                    │
                    ▼
               FastAPI API
             ┌─────────────┐
             │             │
             ▼             ▼
      Business API     /metrics
                             │
                             ▼
                       Prometheus
                             │
                             ▼
                          TSDB
```

---

# 今日重點整理

- FastAPI 整合 Prometheus Instrumentator
- Instrumentator 自動建立 `/metrics`
- `.instrument(app)` 自動統計所有 HTTP Request
- `.expose(app)` 自動建立 Metrics Endpoint
- 原本 `/metrics` JSON API 改為 `/job-metrics`
- Prometheus 成功 Scrape API
- API Target 由 DOWN 變成 UP
- `/metrics` 必須回傳 Prometheus Metrics 格式
- Prometheus 開始收集 Application Metrics

---

# Interview QA

## Q1：為什麼原本的 `/metrics` 要改成 `/job-metrics`？

### Answer

`prometheus-fastapi-instrumentator` 會自動建立 `/metrics` Endpoint，提供 Prometheus 標準 Metrics。如果保留原本回傳 JSON 的 `/metrics`，兩個路由會衝突，因此將原本的業務統計 API 改名為 `/job-metrics`，讓 Prometheus 使用 `/metrics`，而業務統計仍可透過 `/job-metrics` 存取。

---

## Q2：Prometheus 為什麼能將 API Target 從 DOWN 變成 UP？

### Answer

Prometheus 會定期向 `/metrics` 發送 HTTP GET 請求。原本 API 回傳的是 `application/json`，Prometheus 無法解析，因此 Target 顯示 DOWN。整合 Instrumentator 後，`/metrics` 改為回傳 Prometheus 規範的 `text/plain` Metrics 格式，Prometheus 成功解析並開始收集 Metrics，因此 Target 狀態變為 UP。
