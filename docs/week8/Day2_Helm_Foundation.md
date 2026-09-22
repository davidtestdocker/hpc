<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day2 — Helm 的 values 與模板

[上一課](<Day1_GitOps_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day3_Helmize_Platform.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 scaffold 渲染示例。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

nginx 是舊 scaffold 示例，不是現行 API chart 映像。repo 根目錄 chart 路徑是 helm/api，不是 ./api。helm template 只產生 YAML，不能證明 admission、排程、資料庫或應用正常。

## 程式／設定與來源

本次核對：[helm/api/Chart.yaml](<../../helm/api/Chart.yaml>)、[helm/api/values.yaml](<../../helm/api/values.yaml>)、[helm/api/templates/deployment.yaml](<../../helm/api/templates/deployment.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day2_Helm_Foundation.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
image: nginx:1.16.0
```

沒有當時完整渲染檔或執行 log；不把 chart 語法示例當成現在部署成功。

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
