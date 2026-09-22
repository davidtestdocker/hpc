<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day4 — Helm 條件與共用命名

[上一課](<Day3_Helmize_Platform.md>) · [本週目錄](README.md) · [下一課](<Day5_Kustomize_Foundation.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 revision 敘述。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

Helm history 不是永遠保留的保證，也不是資料庫 rollback。API helper 名稱可變，但 postgres-secret 等仍固定，多 release 同 namespace 未必互不影響。主部署使用 Kustomize 呼叫 Helm 渲染再 apply，不會因此建立可 helm rollback 的同名 Release。

## 程式／設定與來源

本次核對：[helm/api/templates/_helpers.tpl](<../../helm/api/templates/_helpers.tpl>)、[helm/api/templates/deployment.yaml](<../../helm/api/templates/deployment.yaml>)、[helm/postgres/templates/secret.yaml](<../../helm/postgres/templates/secret.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day4_Helm_Advanced.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Revision4
```

Revision1～4 是文內敘述，沒有 helm history 原始列；不能代表目前主叢集的 release 管理狀態。

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

# Week8 Day4 - Helm Advanced

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/api/Chart.yaml](../../helm/api/Chart.yaml)
- [helm/api/templates/_helpers.tpl](../../helm/api/templates/_helpers.tpl)
- [helm/api/templates/deployment.yaml](../../helm/api/templates/deployment.yaml)
- [helm/api/values.yaml](../../helm/api/values.yaml)

---

## 本日成果

完成 Helm Release 管理與 Helm Helper（`_helpers.tpl`）的學習，平台正式具備企業級 Helm Chart 的基本架構。

---

# 今日目標

完成 Helm 的核心能力：

* Helm Install
* Helm Upgrade
* Helm History
* Helm Rollback
* Helper Template
* define
* include

---

# Helm 與 kubectl 的角色

Helm：

負責：

* Chart
* Release
* Revision
* Values
* 部署管理

kubectl：

負責：

* Pod
* Deployment
* Service
* Log
* Debug
* Cluster 狀態

因此：

部署：

```bash
helm upgrade api ./api -n hpc-platform
```

驗證：

```bash
kubectl get pods -n hpc-platform
```

查看 Log：

```bash
kubectl logs -n hpc-platform deployment/api
```

---

# Helm Install

第一次部署：

```bash
helm install api ./api -n hpc-platform
```

建立：

Release：

```text
api
```

---

# Helm Upgrade

修改：

```yaml
replicaCount
```

更新：

```bash
helm upgrade api ./api -n hpc-platform
```

Helm：

自動比較差異。

更新 Kubernetes Resource。

---

# Helm History

查看：

```bash
helm history api -n hpc-platform
```

平台：

完成：

```text
Revision1

↓

Revision2

↓

Revision3

↓

Revision4
```

完整保留部署歷史。

---

# Helm Rollback

Rollback：

```bash
helm rollback api 2 -n hpc-platform
```

注意：

Rollback：

不是：

回到 Revision2。

而是：

建立：

新的：

```text
Revision4
```

內容：

等同：

Revision2。

History：

永遠保留。

方便：

Audit。

---

# Release

目前：

Release：

```text
api
```

Chart：

```text
api
```

Chart：

可以建立：

多個：

Release。

例如：

```text
api

api-dev

api-stage

api-prod
```

互不影響。

---

# _helpers.tpl

Helm：

提供：

```text
_helpers.tpl
```

作為：

共用 Template。

避免：

每個 YAML：

重複相同內容。

---

# define

建立：

Helper：

例如：

```tpl
{{ define "api.labels" }}
...
{{ end }}
```

建立：

可重複使用 Template。

---

# include

使用：

Helper：

```tpl
{{ include "api.labels" . }}
```

如同：

Python：

```python
function()
```

概念。

---

# selectorLabels

Deployment：

Selector：

```yaml
matchLabels:
```

Pod：

Labels：

```yaml
labels:
```

Service：

Selector：

```yaml
selector:
```

全部：

改為：

```tpl
{{ include "api.selectorLabels" . }}
```

避免：

Selector 不一致。

---

# labels

Deployment：

Metadata：

Labels：

改為：

```tpl
{{ include "api.labels" . }}
```

由：

Helper：

統一管理。

---

# fullname

平台：

開始使用：

```tpl
{{ include "api.fullname" . }}
```

建立：

Resource Name。

例如：

Service：

```text
api-service
```

ConfigMap：

```text
api-config
```

Secret：

```text
api-secret
```

未來：

若：

Release：

改為：

```text
api-dev
```

Render：

自動變成：

```text
api-dev-service

api-dev-config

api-dev-secret
```

避免：

不同 Release：

互相衝突。

---

# Helper 化資源

目前：

完成：

* Deployment Labels
* Deployment Selector
* Pod Labels
* Service Selector
* ConfigMap Name
* Secret Name
* Service Name

開始使用：

Helper。

---

# Helm Chart 能力提升

目前 Chart：

已具備：

* Values 管理
* Helper Template
* Release Name
* Dynamic Resource Name
* Dynamic Selector
* Dynamic Labels

開始符合企業 Helm Chart 設計方式。

---

# 今日重點

Helm：

不是：

取代 kubectl。

Helm：

負責：

Release。

kubectl：

負責：

Cluster。

企業：

日常流程：

```text
helm upgrade

↓

kubectl rollout status

↓

kubectl get pods

↓

kubectl logs
```

---

# Interview Q&A

## Q1：Helm Rollback 為什麼會建立新的 Revision？

Rollback 不會修改歷史，而是重新部署指定 Revision 的內容，因此會建立新的 Revision，保留完整部署紀錄。

---

## Q2：為什麼需要 `_helpers.tpl`？

將名稱、Labels、Selector 等共用邏輯集中管理，避免重複並提升 Helm Chart 的可維護性。

---

## Q3：Helm 與 kubectl 的差別？

Helm 負責 Chart、Release 與版本管理；kubectl 負責操作及觀察 Kubernetes Cluster 中的實際資源。

---

# 今日成果

平台已完成：

* Helm Release 管理
* Helm History
* Helm Rollback
* Helper Template
* define
* include
* Dynamic Labels
* Dynamic Selector
* Dynamic Resource Name

Helm Chart 已具備企業實務中常見的設計模式。

---

# 下一步

Week8 Day5：

Kustomize

學習：

* Base
* Overlay
* Patch
* Strategic Merge
* JSON6902 Patch
* dev / stage / prod 環境管理
* 與 Helm 的搭配方式
