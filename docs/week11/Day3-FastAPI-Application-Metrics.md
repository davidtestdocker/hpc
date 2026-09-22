<!-- readable-curriculum: 2026-09-22 -->
# Week11 Day3 — FastAPI application metrics

[上一課](<Day2-Prometheus-ScrapeJob-Target與PullModel.md>) · [本週目錄](README.md) · [下一課](<Day4-NodeExporter-GrafanaDashboard-KubernetesServiceDiscovery.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Instrumentator 自動記錄 HTTP 請求，但 HTTP latency 不等於非同步 MPI 的 end-to-end latency。只量 POST /benchmark 會主要看提交路徑，而非計算時間。

## 在現在的專案中

監控 manifests 和歷史 dashboard 保留為獨立路徑；不宣稱即時 target 健康。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
Instrumentator().instrument(app).expose(app)

# class 定義 BenchmarkRequest 類別；括號內是繼承的父類別。
# 繼承 Pydantic BaseModel，FastAPI 依欄位型別驗證 JSON；simulate_failure 預設為 False。
class BenchmarkRequest(BaseModel):
    benchmark: str
    simulate_failure: bool = False


# 回傳 API 首頁資訊。
# @ 是 decorator：將下方函式註冊為指定 HTTP 方法與路徑的處理函式。
@app.get("/")
def root():
    return {
        "message": "HPC API DEV",
        "status": "running"
    }

# 回傳程序健康狀態；這個端點未檢查所有外部相依服務。
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week11/Day3-FastAPI-Application-Metrics.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：舊監控環境／dashboard 不等於即時健康；9/22 訓練保存的是 nvidia-smi 遙測與 CUDA traces。
> **閱讀順序**：先學本文基礎，再讀[Week11 現行對照與檢核](../learning-guide.md#week11)及[對應現行入口](../evidence/README.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week11 Day3 - FastAPI Application Metrics

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [helm/api/values-dev.yaml](../../helm/api/values-dev.yaml)
- [helm/prometheus/templates/configmap.yaml](../../helm/prometheus/templates/configmap.yaml)
- [requirements.txt](../../requirements.txt)

---

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
