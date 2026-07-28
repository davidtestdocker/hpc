# Week11 Day2 - Prometheus Scrape Job、Target 與 Pull Model

---

# 今日目標

今天完成以下內容：

- 理解 Prometheus Pull Model
- 理解 scrape_configs
- 理解 Job 與 Target
- 新增第二個 Scrape Job（API）
- 驗證 Prometheus Targets
- 理解 Prometheus Target 為何會 UP / DOWN
- 理解 Kubernetes Service Discovery

---

# 今日架構

```text
                 Kubernetes Cluster

        +-------------------------------+
        |                               |
        |   Prometheus                  |
        |        │                      |
        |        │ HTTP GET /metrics    |
        |        ▼                      |
        |   api-service                 |
        |        │                      |
        |        ▼                      |
        |      API Pod                  |
        |                               |
        +-------------------------------+
```

---

# 一、Prometheus Pull Model

Prometheus 採用 **Pull Model**。

意思是：

不是 API 主動送資料。

而是 Prometheus 定期去抓。

流程：

```text
Prometheus

↓

GET /metrics

↓

API

↓

回傳 Metrics

↓

Prometheus 存進 TSDB
```

目前每：

```yaml
scrape_interval: 15s
```

抓一次。

---

# 二、scrape_configs

Prometheus 最重要的設定：

```yaml
scrape_configs:
```

意思：

> 定義 Prometheus 要監控哪些 Target。

---

原本只有：

```yaml
scrape_configs:

  - job_name: prometheus

    static_configs:

      - targets:

          - localhost:9090
```

代表：

```text
Prometheus

↓

localhost:9090

↓

Prometheus 自己
```

---

# 三、新增 API Scrape Job

新增：

```yaml
scrape_configs:

  - job_name: prometheus
    static_configs:
      - targets:
          - localhost:9090

  - job_name: api
    static_configs:
      - targets:
          - api-service:8000
```

Render 驗證：

```bash
helm template prometheus helm/prometheus
```

確認：

```yaml
- job_name: api

  static_configs:

    - targets:

        - api-service:8000
```

---

# 四、Job 與 Target

Job：

代表一組 Scrape 工作。

例如：

```yaml
job_name: api
```

代表：

建立一個叫 api 的監控工作。

Target：

代表真正要抓的主機。

例如：

```yaml
targets:

  - api-service:8000
```

流程：

```text
Job

↓

Target

↓

HTTP GET

↓

Metrics
```

---

# 五、為什麼寫 api-service

不是：

```text
10.68.x.x
```

而是：

```text
api-service
```

原因：

Pod IP 會改變。

Service 不會。

流程：

```text
Prometheus

↓

api-service

↓

CoreDNS

↓

ClusterIP

↓

Service

↓

API Pod
```

---

# 六、Kubernetes Service Discovery

Prometheus 可以找到：

```text
api-service
```

不是 Helm。

不是 Kustomize。

真正原因：

Kubernetes：

- CoreDNS
- Service
- Endpoints
- CNI

共同完成。

流程：

```text
Prometheus

↓

api-service

↓

CoreDNS

↓

ClusterIP

↓

Service Selector

↓

API Pod
```

---

# 七、Namespace 關係

目前：

```text
Namespace

hpc-platform-dev

├── api

├── redis

├── postgres

└── prometheus
```

同 Namespace：

可以直接：

```text
api-service
```

不同 Namespace：

必須：

```text
api-service.hpc-platform-dev
```

---

# 八、Prometheus UI

進入：

```text
Status

↓

Targets
```

看到：

```text
prometheus

UP
```

代表：

Prometheus 已成功監控自己。

新增 API 後：

```text
api

DOWN
```

---

# 九、為什麼 API 是 DOWN

錯誤：

```text
received unsupported Content-Type

application/json
```

代表：

Prometheus 已成功連線：

```text
api-service:8000
```

但是：

API 回傳：

```http
Content-Type:

application/json
```

Prometheus 要求：

```http
Content-Type:

text/plain
```

Prometheus Metrics 格式：

```text
# HELP http_requests_total

# TYPE http_requests_total counter

http_requests_total 100
```

目前 API 尚未提供：

```text
/metrics
```

因此：

```text
Target

↓

DOWN
```

屬於預期結果。

---

# 十、Helm 驗證

Render：

```bash
helm template prometheus helm/prometheus
```

Lint：

```bash
helm lint helm/prometheus
```

GitOps：

```bash
git add .

git commit

git pull --rebase origin master

git push origin master
```

Argo CD：

自動同步更新 ConfigMap。

---

# 十一、Prometheus Rolling Update

更新 ConfigMap 後：

Deployment 建立新 Pod。

新 Pod 啟動時：

出現：

```text
opening storage failed:

lock DB directory:

resource temporarily unavailable
```

原因：

Prometheus TSDB 使用同一顆 PVC。

TSDB 尚未釋放 Lock。

Kubernetes 持續重試。

最終：

Pod 啟動成功。

因此：

```text
STATUS

Running

RESTARTS

9
```

代表：

歷史曾重啟 9 次。

目前已恢復正常。

---

# 今日重點整理

- Prometheus 採 Pull Model
- scrape_configs 定義所有監控工作
- Job 是一組 Scrape 工作
- Target 是真正要抓取的 Endpoint
- Prometheus 透過 Service 名稱監控 API
- Kubernetes 利用 CoreDNS 將 Service 名稱解析成 ClusterIP
- 同 Namespace 可直接使用 Service 名稱
- Prometheus 必須抓取 `/metrics`
- `/metrics` 必須回傳 Prometheus Metrics 格式
- application/json 代表 API 有回應，但不是 Metrics
- Target DOWN 不代表 Service 壞掉，可能只是 Metrics 格式錯誤

---

# Interview QA

## Q1：Prometheus 為什麼使用 api-service，而不是 Pod IP？

### Answer

Pod IP 在 Pod 重建後會改變，因此不適合作為固定監控目標。Prometheus 會透過 Kubernetes Service 名稱（例如 `api-service`）發送請求，由 CoreDNS 將 Service 名稱解析為 ClusterIP，再由 Service 根據 Selector 將流量轉送到目前存活的 API Pod，因此即使 Pod 重建，Prometheus 仍可持續監控。

---

## Q2：Prometheus Target 顯示 DOWN，但錯誤訊息為 `unsupported Content-Type "application/json"`，代表什麼？

### Answer

代表 Prometheus 已成功連線到 API，網路、DNS、Service 與 Pod 都正常；但 API 回傳的是 `application/json`，而不是 Prometheus 規定的 Metrics 格式（`text/plain`）。因此 Prometheus 無法解析 Metrics，Target 會顯示 DOWN。解決方式是在 API 實作 `/metrics` Endpoint，並回傳 Prometheus Metrics 格式。
