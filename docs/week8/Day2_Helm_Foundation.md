# Week8 Day2 - Helm Foundation

## 本週成果

平台開始導入 Helm。

建立第一個 Helm Chart，理解 Helm Template 的運作方式，為後續 Helm 化整個 HPC AI Benchmark Platform 做準備。

---

# 今日平台增加什麼

建立：

```text
helm/
└── api/
```

第一個 Helm Chart。

平台開始從：

```text
手動管理 YAML
```

進化為：

```text
Template

↓

Render

↓

Kubernetes YAML
```

---

# Platform Problem

目前平台：

```text
k8s/

api-deployment.yaml

api-service.yaml

api-ingress.yaml
```

如果：

```text
dev

stage

prod
```

三個環境。

通常就會變成：

```text
deployment-dev.yaml

deployment-stage.yaml

deployment-prod.yaml
```

大量重複 YAML。

維護成本很高。

---

# Helm 是什麼？

Helm 是：

> Kubernetes Template Engine + Package Manager。

真正重要的是：

```text
Template Engine
```

Helm 並不是新的 Kubernetes Resource。

它只是：

```text
Template

+

Values

↓

Render

↓

真正的 Kubernetes YAML
```

---

# Helm 四個核心概念

## Chart

Chart 代表一個應用程式。

例如：

```text
api
```

就是一個 Chart。

---

## Template

例如：

```yaml
replicas: {{ .Values.replicaCount }}
```

Template 並不是合法 YAML。

必須先 Render。

---

## Values

Values 提供 Template 所需的參數。

例如：

```yaml
replicaCount: 3

image:
  repository: hpc-ai-benchmark-platform-api
  tag: latest
```

不同環境可以使用不同 values。

---

## Release

同一個 Chart：

```text
api
```

可以建立：

```text
api-dev

api-stage

api-prod
```

每一個安裝實例都稱為：

```text
Release
```

---

# Helm Chart 結構

建立：

```bash
helm create api
```

產生：

```text
api/

├── Chart.yaml
├── values.yaml
├── charts/
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    ├── serviceaccount.yaml
    ├── NOTES.txt
    └── tests/
```

---

# Chart.yaml

Chart 的 Metadata。

例如：

```text
name

version

description

appVersion
```

描述 Chart 本身。

不是 Kubernetes Resource。

---

# values.yaml

所有可調整參數。

例如：

```text
replicaCount

image

service

ingress

resources
```

真正部署時會讀取這些值。

---

# templates/

存放 Kubernetes Template。

例如：

```text
deployment.yaml

service.yaml

ingress.yaml
```

Template 使用：

```text
{{ .Values.xxx }}
```

取得 values。

---

# Helm Render

執行：

```bash
helm template api ./api
```

Helm：

```text
Templates

+

Values

↓

Render

↓

Deployment

Service

Ingress

...
```

輸出真正 Kubernetes YAML。

---

# Render 結果

預設：

Deployment：

```yaml
image: nginx:1.16.0

replicas: 1
```

Service：

```yaml
type: ClusterIP

port: 80
```

這些內容來自：

```text
values.yaml
```

而不是直接寫死在 Deployment。

---

# 平台架構

```text
Chart
      │
values.yaml
      │
templates/
      │
helm template
      │
Rendered YAML
      │
Kubernetes
```

---

# 今日重點

* Helm 是 Kubernetes Template Engine。
* Chart 代表一個應用程式。
* Values 提供 Template 所需參數。
* Template 必須 Render 後才會變成 Kubernetes YAML。
* helm template 不會部署，只會產生 YAML。

---

# Interview Q&A

## Q1：Helm 是 Kubernetes 嗎？

不是。

Helm 是 Kubernetes 的 Template Engine 與 Package Manager。

最終仍然產生 Kubernetes YAML。

---

## Q2：helm template 會部署到 Cluster 嗎？

不會。

它只會 Render Templates，輸出 Kubernetes YAML。

---

## Q3：Chart 和 Release 差在哪？

Chart 是應用程式模板。

Release 是 Chart 的一個安裝實例。

同一個 Chart 可以建立多個 Release。

---

# 今日成果

平台已建立第一個 Helm Chart：

```text
helm/

└── api/
```

理解：

```text
Chart

↓

Values

↓

Template

↓

Rendered YAML
```

開始建立 Helm 思維，準備將整個 HPC AI Benchmark Platform Helm 化。

---

# 下一步

Week8 Day3：

將目前：

```text
k8s/
```

中的 Deployment、Service、Ingress、ConfigMap、Secret、HPA

全部逐步改造成 Helm Chart，讓平台具備真正可參數化的部署能力。

