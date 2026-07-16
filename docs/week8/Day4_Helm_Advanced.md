# Week8 Day4 - Helm Advanced

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

