<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day3 — 平台 Chart 拆分

[上一課](<Day2_Helm_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day4_Helm_Advanced.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

API、Redis、PostgreSQL 各有 chart，overlay 統一 namespace 與環境值。chart 的預設值未必是主環境實際值，必須再看 valuesFile 和 patch。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[kustomize/overlays/gpu-sg-platform/kustomization.yaml](<../../kustomize/overlays/gpu-sg-platform/kustomization.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
helmCharts:
  - name: api
    releaseName: api
    namespace: hpc-platform-dev
    # 覆寫 Helm values 的設定檔路徑。
    valuesFile: api-values.yaml
    includeCRDs: false

  - name: redis
    releaseName: redis
    namespace: hpc-platform-dev
    valuesFile: redis-values.yaml
    includeCRDs: false

  - name: postgres
    releaseName: postgres
    namespace: hpc-platform-dev
    valuesFile: postgres-values.yaml
    includeCRDs: false

# 對選定資源套用局部修改。
patches:
  - path: system-pool-patch.yaml
    target:
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week8/Day3_Helmize_Platform.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
