<!-- readable-curriculum: 2026-09-22 -->
# Week11 Day4 — Node Exporter 與 dashboard

[上一課](<Day3-FastAPI-Application-Metrics.md>) · [本週目錄](README.md) · [下一週](../week12/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Node Exporter 描述 host 資源，不直接知道模型 tokens/s；Grafana 圖表正確性取決於 query 和 labels。第三方 chart 原文保留，教學不修改其來源檔假裝是自製。

## 在現在的專案中

監控 manifests 和歷史 dashboard 保留為獨立路徑；不宣稱即時 target 健康。

本課對照：[helm/prometheus/values.yaml](<../../helm/prometheus/values.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
# scrapeInterval 15 秒抓一次所有 Metrics
# evaluationInterval 15 秒重新計算一次 Rules
config:
  # Prometheus 抓取指標的時間間隔。
  scrapeInterval: 15s
  # Prometheus 評估規則的時間間隔。
  evaluationInterval: 15s
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week11/Day4-NodeExporter-GrafanaDashboard-KubernetesServiceDiscovery.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：舊監控環境／dashboard 不等於即時健康；9/22 訓練保存的是 nvidia-smi 遙測與 CUDA traces。
> **閱讀順序**：先學本文基礎，再讀[Week11 現行對照與檢核](../learning-guide.md#week11)及[對應現行入口](../evidence/README.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week11 Day4 - Node Exporter、Grafana Dashboard、Kubernetes Service Discovery

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

Node Exporter／Grafana 連結包含保存的第三方 Chart 設定及 dashboard，供對照當時監控實驗。

- [helm/grafana-10.5.15/grafana/dashboards/custom-dashboard.json](../../helm/grafana-10.5.15/grafana/dashboards/custom-dashboard.json)
- [helm/grafana-10.5.15/grafana/values.yaml](../../helm/grafana-10.5.15/grafana/values.yaml)
- [helm/prometheus-node-exporter-4.56.1/prometheus-node-exporter/values.yaml](../../helm/prometheus-node-exporter-4.56.1/prometheus-node-exporter/values.yaml)
- [helm/prometheus/templates/clusterrole.yaml](../../helm/prometheus/templates/clusterrole.yaml)
- [helm/prometheus/templates/clusterrolebinding.yaml](../../helm/prometheus/templates/clusterrolebinding.yaml)
- [helm/prometheus/templates/configmap.yaml](../../helm/prometheus/templates/configmap.yaml)
- [helm/prometheus/templates/serviceaccount.yaml](../../helm/prometheus/templates/serviceaccount.yaml)

---

## 今日新增

建立完整 Kubernetes Node Monitoring。

使用 **Node Exporter** 收集每台 Node 的 Metrics，由 **Prometheus** 自動收集，再透過 **Grafana Dashboard** 視覺化呈現，最後改用 **Kubernetes Service Discovery** 自動發現 Targets，並建立完整 RBAC。

---

# 今日目標

- 部署 Node Exporter
- Prometheus 收集 Node Metrics
- Grafana 顯示 Node Dashboard
- 使用 Kubernetes Service Discovery
- 建立 Prometheus RBAC

---

# 今日架構

```text
                     Kubernetes API Server
                              ▲
                              │
              list/watch Pods、Services、Endpoints
                              │
                       ServiceAccount
                              │
                    ClusterRoleBinding
                              │
                        ClusterRole
                              ▲
                              │
                        Prometheus
                       /          \
                      /            \
             Grafana Dashboard   Node Exporter
                                       ▲
                                       │
                                   DaemonSet
                                       │
                ┌──────────────────────┴──────────────────────┐
                │                                             │
             GKE Node1                                   GKE Node2
```

---

# Node Exporter

## 什麼是 Node Exporter？

Node Exporter 是 Prometheus 官方提供的 Exporter。

用途：

收集 Linux 主機 Metrics。

例如：

- CPU
- Memory
- Disk
- Filesystem
- Network
- Load Average
- Context Switch
- File Descriptor

它只負責：

```text
Linux
    │
    ▼
收集 Metrics
    │
    ▼
提供 /metrics
```

Prometheus 才負責定期抓取。

---

# 為什麼使用 DaemonSet？

Node Exporter 必須：

**每台 Node 都有一個。**

因此使用：

```text
DaemonSet
```

而不是：

```text
Deployment
```

Deployment：

```text
Node1

Pod
```

DaemonSet：

```text
Node1

Node Exporter

────────────

Node2

Node Exporter
```

每新增一台 Node，

DaemonSet 都會自動建立一個 Node Exporter。

---

# Node Exporter Service

Node Exporter 提供：

```text
9100
```

Prometheus 透過：

```
/metrics
```

取得 Metrics。

---

# Prometheus 收集 Node Exporter

一開始使用：

```yaml
scrape_configs:
  - job_name: node-exporter

    static_configs:
      - targets:
          - node-exporter-prometheus-node-exporter:9100
```

流程：

```text
Prometheus
      │
      ▼
Service DNS
      │
      ▼
Node Exporter
```

---

# Static Config 缺點

- Target 必須手動設定
- Pod IP 改變需要重新設定
- 不適合 Kubernetes

因此改成：

Kubernetes Service Discovery。

---

# Grafana

建立 Grafana。

設定 Prometheus Datasource：

```text
http://prometheus:9090
```

Save & Test：

```text
Successfully connected.
```

---

# Dashboard

先建立自己的 Dashboard。

加入：

- CPU Usage
- Memory Usage
- Disk Usage

了解：

Grafana

```
Dashboard
    │
    ├── Panel
    ├── Panel
    └── Panel
```

每個 Graph 都是一個 Panel。

---

# 匯入官方 Dashboard

使用：

```text
Node Exporter Full

Dashboard ID

1860
```

Dashboard 可直接顯示：

- CPU
- Memory
- Filesystem
- Network
- Load
- Disk IO

---

# Kubernetes Service Discovery

由：

```yaml
static_configs
```

改成：

```yaml
- job_name: node-exporter

  kubernetes_sd_configs:
    - role: endpoints

  relabel_configs:
    - source_labels:
        - __meta_kubernetes_service_name
      action: keep
      regex: node-exporter-prometheus-node-exporter

    - source_labels:
        - __meta_kubernetes_endpoint_port_name
      action: keep
      regex: metrics
```

---

# kubernetes_sd_configs

用途：

向 Kubernetes API 自動查詢：

- Services
- Endpoints
- Pods

建立所有 Scrape Targets。

流程：

```text
Prometheus
      │
      ▼
Kubernetes API
      │
      ▼
Services
      │
      ▼
Endpoints
      │
      ▼
Node Exporter Pod
```

---

# relabel_configs

用途：

過濾 Kubernetes API 找到的 Targets。

保留：

```
Service

node-exporter-prometheus-node-exporter
```

以及：

```
metrics
```

Port。

---

# 為什麼需要 RBAC？

Static Config：

```text
Prometheus
      │
      ▼
Service DNS
```

不需要查 Kubernetes API。

---

Service Discovery：

```text
Prometheus
      │
      ▼
Kubernetes API
```

需要：

- Pods
- Services
- Endpoints
- EndpointSlices

因此必須建立 RBAC。

---

# ServiceAccount

建立：

```text
prometheus
```

Deployment：

```yaml
serviceAccountName: prometheus
```

不再使用：

```text
default
```

ServiceAccount。

---

# ClusterRole

授予：

Core API

```text
Pods
Services
Endpoints
Nodes
```

Discovery API

```text
EndpointSlices
```

權限：

```text
get
list
watch
```

---

# 為什麼 apiGroups 要拆成兩個？

Core API：

```yaml
apiGroups: [""]
```

包含：

- Pods
- Services
- Endpoints
- Nodes

Discovery API：

```yaml
apiGroups:
- discovery.k8s.io
```

包含：

- EndpointSlices

不同 API Group，

因此 RBAC 必須拆成不同 Rules。

---

# ClusterRoleBinding

將：

```text
ServiceAccount
```

綁定：

```text
ClusterRole
```

流程：

```text
Prometheus
      │
      ▼
ServiceAccount
      │
      ▼
ClusterRoleBinding
      │
      ▼
ClusterRole
      │
      ▼
Kubernetes API
```

---

# Debug 紀錄

## 1.

Targets：

```text
0 / 0 UP
```

原因：

沒有使用 Kubernetes API 成功取得 Targets。

---

## 2.

RBAC：

```text
cannot list endpoints

cannot list pods

cannot list services
```

原因：

Prometheus 使用：

```text
default
```

ServiceAccount。

---

## 3.

Helm：

```text
yaml:
did not find expected key
```

原因：

ConfigMap YAML 縮排錯誤。

---

## 4.

Prometheus：

```text
CrashLoopBackOff
```

Log：

```text
did not find expected '-' indicator
```

原因：

`kubernetes_sd_configs`

沒有縮排到：

```
job_name
```

底下。

---

## 5.

修正後：

Prometheus：

```
Status

↓

Targets
```

結果：

```text
node-exporter

2 / 2 UP
```

Grafana：

Node Exporter Dashboard

正常顯示兩台 Node Metrics。

---

# 今日完成

- ✅ Node Exporter Helm Chart
- ✅ DaemonSet
- ✅ Node Metrics
- ✅ Prometheus Scrape
- ✅ Grafana Datasource
- ✅ Grafana Dashboard
- ✅ Node Exporter Full Dashboard
- ✅ Kubernetes Service Discovery
- ✅ ServiceAccount
- ✅ ClusterRole
- ✅ ClusterRoleBinding
- ✅ Prometheus RBAC
- ✅ 自動發現 Node Exporter
- ✅ Targets 2 / 2 UP

---

# Interview

## Q1

為什麼 Node Exporter 使用 DaemonSet，而不是 Deployment？

**Ans**

因為每台 Kubernetes Node 都需要執行一個 Node Exporter 收集主機 Metrics，因此使用 DaemonSet，當新增或移除 Node 時，Pod 也會自動跟著建立或刪除。

---

## Q2

為什麼使用 Kubernetes Service Discovery 後需要建立 RBAC？

**Ans**

因為 Prometheus 需要向 Kubernetes API 查詢 Pods、Services、Endpoints、EndpointSlices，因此必須授予 `get`、`list`、`watch` 權限，才能自動發現所有 Scrape Targets。
