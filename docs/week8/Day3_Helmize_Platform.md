<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day3 — 平台 Chart 拆分

[上一課](<Day2_Helm_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day4_Helm_Advanced.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：參數化示例與現存模板。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

目前 Secret 模板在 postgres chart，不在 API；API 仍引用固定 postgres-secret，原文 secret.*／secretName 不都被現行模板使用。主環境用外部既有 Secret，不將帳密放 values。values 出現欄位不代表 template 已讀取；例如若未引用 securityContext 設定也不會生效。

## 程式／設定與來源

本次核對：[helm/api/values.yaml](<../../helm/api/values.yaml>)、[helm/api/templates/deployment.yaml](<../../helm/api/templates/deployment.yaml>)、[helm/postgres/templates/secret.yaml](<../../helm/postgres/templates/secret.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day3_Helmize_Platform.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
replicas: {{ .Values.replicaCount }}
```

原文稱渲染一致但無完整 diff；目前模板已加入獨立 worker、條件 replicas 等差異，不能說和舊 k8s YAML 完全相同。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 overlay 是 gpu-sg-platform；Argo dev 仍指 overlays/dev，不能宣稱主環境已完成 GitOps 對齊。
> **閱讀順序**：先學本文基礎，再讀[Week8 現行對照與檢核](../learning-guide.md#week8)及[對應現行入口](../../kustomize/overlays/gpu-sg-platform/kustomization.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week8 Day3 - Helmize HPC AI Performance Engineering Platform

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/api/Chart.yaml](../../helm/api/Chart.yaml)
- [helm/api/templates/_helpers.tpl](../../helm/api/templates/_helpers.tpl)
- [helm/api/templates/configmap.yaml](../../helm/api/templates/configmap.yaml)
- [helm/api/templates/deployment.yaml](../../helm/api/templates/deployment.yaml)
- [helm/api/templates/hpa.yaml](../../helm/api/templates/hpa.yaml)
- [helm/api/templates/ingress.yaml](../../helm/api/templates/ingress.yaml)
- [helm/api/templates/service.yaml](../../helm/api/templates/service.yaml)
- [helm/api/values-dev.yaml](../../helm/api/values-dev.yaml)
- [helm/api/values-prod.yaml](../../helm/api/values-prod.yaml)
- [helm/api/values-stage.yaml](../../helm/api/values-stage.yaml)
- [helm/api/values.yaml](../../helm/api/values.yaml)
- [helm/postgres/Chart.yaml](../../helm/postgres/Chart.yaml)
- [helm/postgres/templates/pvc.yaml](../../helm/postgres/templates/pvc.yaml)
- [helm/postgres/templates/secret.yaml](../../helm/postgres/templates/secret.yaml)
- [helm/postgres/templates/service.yaml](../../helm/postgres/templates/service.yaml)
- [helm/postgres/templates/statefulset.yaml](../../helm/postgres/templates/statefulset.yaml)
- [helm/postgres/values.yaml](../../helm/postgres/values.yaml)
- [helm/redis/Chart.yaml](../../helm/redis/Chart.yaml)
- [helm/redis/templates/deployment.yaml](../../helm/redis/templates/deployment.yaml)
- [helm/redis/templates/service.yaml](../../helm/redis/templates/service.yaml)
- [helm/redis/values.yaml](../../helm/redis/values.yaml)
- [k8s/api-configmap.yaml](../../k8s/api-configmap.yaml)
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/api-hpa.yaml](../../k8s/api-hpa.yaml)
- [k8s/api-ingress.yaml](../../k8s/api-ingress.yaml)
- [k8s/api-service.yaml](../../k8s/api-service.yaml)

---

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
