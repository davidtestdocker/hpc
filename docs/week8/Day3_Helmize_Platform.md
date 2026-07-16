# Week8 Day3 - Helmize HPC AI Performance Engineering Platform

## 本日成果

將原本以 `k8s/` 管理的 Kubernetes YAML，正式轉換為 Helm Chart。

平台開始具備可參數化部署能力。

---

# 今日目標

將：

```text
k8s/
```

中的 Kubernetes Resource：

* Deployment
* Service
* ConfigMap
* Secret
* Ingress
* HorizontalPodAutoscaler

全部移至：

```text
helm/api/templates/
```

並逐步以 `values.yaml` 管理可變參數。

---

# 為什麼要 Helm 化？

原本平台：

```text
k8s/

api-deployment.yaml
api-service.yaml
api-ingress.yaml
api-configmap.yaml
postgres-secret.yaml
api-hpa.yaml
```

所有值都直接寫死：

```yaml
replicas: 1

image:
  hpc-ai-benchmark-platform-api

nodePort: 30080

host: api.hpc.local
```

如果：

* dev
* stage
* prod

三個環境。

就需要維護多份 YAML。

---

# Helm 化流程

今天採用企業常見做法：

```text
原本 Kubernetes YAML

↓

搬進 templates/

↓

確認 Render 完全一致

↓

開始參數化
```

而不是重新撰寫所有 Deployment。

---

# Chart 結構

```text
helm/

└── api/

    Chart.yaml

    values.yaml

    templates/

        deployment.yaml
        service.yaml
        configmap.yaml
        secret.yaml
        ingress.yaml
        hpa.yaml
```

---

# Deployment

Deployment 保留原有 Kubernetes YAML。

逐步改為：

```yaml
replicas: {{ .Values.replicaCount }}
```

Image：

```yaml
image:
  repository
  tag
  pullPolicy
```

改由：

```yaml
.Values.image
```

控制。

---

# Service

Service：

原本：

```yaml
type: NodePort

port: 8000

targetPort: 8000

nodePort: 30080
```

改為：

```yaml
.Values.service
```

管理。

values：

```yaml
service:
  type: NodePort
  port: 8000
  targetPort: 8000
  nodePort: 30080
```

---

# ConfigMap

ConfigMap：

Redis：

```text
REDIS_HOST

REDIS_PORT
```

PostgreSQL：

```text
POSTGRES_HOST

POSTGRES_PORT

POSTGRES_DB
```

全部改由：

```yaml
.Values.config
```

管理。

---

# Secret

Secret：

改為：

```yaml
stringData
```

而非：

```yaml
data
```

避免手動 Base64。

values：

```yaml
secret:
  postgresUser: hpc
  postgresPassword: hpc_password
```

Render：

Kubernetes 自動完成 Base64。

---

# Ingress

Host：

```yaml
host: api.hpc.local
```

改為：

```yaml
.Values.ingress.hosts
```

管理。

Path：

```yaml
path: /

pathType: Prefix
```

也改由 values 控制。

---

# HorizontalPodAutoscaler

HPA：

改由：

```yaml
autoscaling:
```

控制。

包含：

```text
enabled

minReplicas

maxReplicas

targetCPUUtilizationPercentage
```

Template：

使用：

```yaml
{{ if .Values.autoscaling.enabled }}
```

控制是否 Render HPA。

---

# Resource Requests / Limits

Deployment：

改為：

```yaml
resources:
{{ toYaml .Values.resources | nindent 10 }}
```

values：

```yaml
resources:

  requests:

    cpu: 100m

    memory: 128Mi

  limits:

    cpu: 500m

    memory: 512Mi
```

避免 Deployment 直接寫死資源設定。

---

# Readiness Probe

Probe：

改為：

```yaml
.Values.readinessProbe
```

管理。

包含：

```text
path

port

initialDelaySeconds

periodSeconds
```

---

# Liveness Probe

Probe：

改為：

```yaml
.Values.livenessProbe
```

管理。

Deployment 不再寫死 Probe。

---

# Render 驗證

使用：

```bash
helm template api ./api
```

確認：

Render 結果：

與原本：

```text
k8s/
```

中的 Kubernetes YAML 一致。

證明 Helm Chart 可正確產生平台部署設定。

---

# 今日完成的參數化

目前已參數化：

```text
replicaCount

image.repository

image.tag

image.pullPolicy

service.type

service.port

service.targetPort

service.nodePort

config.*

secret.*

autoscaling.*

resources.*

readinessProbe.*

livenessProbe.*

configMapName

secretName

containerPort
```

---

# 平台架構

```text
values.yaml

        │

        ▼

Helm Templates

        │

        ▼

helm template

        │

        ▼

Rendered Kubernetes YAML

        │

        ▼

Kubernetes Cluster
```

---

# 今日重點

* Helm 化不是重寫 Kubernetes。
* 先保持 Render 與原始 YAML 一致，再逐步參數化。
* values.yaml 管理所有可變參數。
* templates 專注於 Kubernetes 資源結構。
* helm template 可驗證 Render 結果是否正確。

---

# Interview Q&A

## Q1：Helm 化時，為什麼先搬 YAML 再參數化？

可以先確保 Helm Render 的結果與原始 Kubernetes YAML 完全一致，再逐步降低風險地導入 Template。

---

## Q2：為什麼 Secret 使用 stringData？

stringData 可直接使用明文，Kubernetes 會自動轉換為 Base64，避免人工編碼。

---

## Q3：為什麼使用 toYaml 搭配 nindent？

`toYaml` 可將 values 中的物件轉為 YAML，`nindent` 則負責補上正確縮排，避免 Render 出錯。

---

# 今日成果

平台已完成第一版 Helm Chart。

Deployment、Service、ConfigMap、Secret、Ingress、HPA 全部由 Helm 管理。

平台開始具備真正可重複部署、可參數化的能力。

---

# 下一步

Week8 Day4：

Helm Advanced

學習：

* `_helpers.tpl`
* `define`
* `include`
* Labels
* Fullname
* `helm install`
* `helm upgrade`
* `helm uninstall`
* Helm Release 管理

將目前 Helm Chart 提升至企業常見的設計方式。

