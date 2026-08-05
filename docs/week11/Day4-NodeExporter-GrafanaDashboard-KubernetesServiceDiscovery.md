# Week11 Day4 - Node Exporter、Grafana Dashboard、Kubernetes Service Discovery

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
