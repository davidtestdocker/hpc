<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day2 — Helm 的 values 與模板

[上一課](<Day1_GitOps_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day3_Helmize_Platform.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

.Values 讀 chart 設定，.Release 帶入 release 資訊，include 可共用命名模板。模板中的大括號不是合法的最終 Kubernetes 欄位，要先 render 才能判讀。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
# Helm 的 if 只在 worker.enabled=true 時渲染此資源；操作見自動 worker runbook。
{{- if .Values.worker.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "api.fullname" . }}-worker
  namespace: {{ .Release.Namespace }}
spec:
  # Demo 使用一個副本；每筆工作的 Redis lease 額外提供重複處理協調。
  replicas: 1
  strategy:
    # Recreate 先停舊版再啟新版，避免小型 system-pool 承擔升級 surge 容量。
    type: Recreate
  selector:
    # selector 與下方 Pod labels 相符，讓 Deployment 管理自己的 worker Pods。
    matchLabels:
      app: {{ include "api.fullname" . }}-worker
  template:
    metadata:
      labels:
        app: {{ include "api.fullname" . }}-worker
    spec:
      # 沿用 namespace 最小 RBAC 身分，允許建立／讀取 JobSet 與回收 launcher log。
      serviceAccountName: {{ .Values.worker.serviceAccountName }}
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week8/Day2_Helm_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 overlay 是 gpu-sg-platform；Argo dev 仍指 overlays/dev，不能宣稱主環境已完成 GitOps 對齊。
> **閱讀順序**：先學本文基礎，再讀[Week8 現行對照與檢核](../learning-guide.md#week8)及[對應現行入口](../../kustomize/overlays/gpu-sg-platform/kustomization.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week8 Day2 - Helm Foundation

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
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/api-ingress.yaml](../../k8s/api-ingress.yaml)
- [k8s/api-service.yaml](../../k8s/api-service.yaml)

---

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
