# Week8 Day1 - GitOps Foundation

## 本週成果

建立 Production Deployment Pipeline。

平台將從：

```text
手動 kubectl apply
```

進化為：

```text
Git

↓

Argo CD

↓

Kubernetes
```

開始建立企業級 GitOps 部署流程。

---

# 今日平台增加什麼

今天建立 GitOps 核心概念。

新增：

```text
gitops/
```

目錄，作為後續 GitOps 相關檔案與部署流程的起點。

目前專案：

```text
hpc-ai-benchmark-platform/

├── api/
├── benchmark/
├── docs/
├── k8s/
├── monitoring/
├── loadtest/
└── gitops/
```

---

# Platform Problem

目前平台部署方式：

```bash
kubectl apply -f api-deployment.yaml

kubectl apply -f api-service.yaml

kubectl apply -f api-ingress.yaml
```

這種方式稱為：

```text
Imperative Deployment
```

雖然簡單，但存在許多問題：

* 不知道誰修改了設定
* Deployment 歷史難以追蹤
* Cluster 容易與 Git 不一致
* 無法自動修正 Drift

---

# GitOps 是什麼？

GitOps 的核心理念：

> **Git 是唯一事實來源（Single Source of Truth）。**

所有 Kubernetes 設定都以 Git Repository 為準。

任何部署都必須先修改 Git，再同步到 Cluster。

---

# 傳統部署流程

```text
Engineer
     │
kubectl apply
     │
Kubernetes Cluster
```

工程師直接操作 Cluster。

---

# GitOps 部署流程

```text
Engineer
     │
git commit
     │
git push
     │
Git Repository
     │
Argo CD
     │
Kubernetes Cluster
```

工程師不直接修改 Cluster。

所有修改都經過 Git。

---

# Desired State

Git Repository：

```yaml
replicas: 2
```

代表：

平台應該有：

```text
2 Pods
```

這就是：

```text
Desired State
```

---

# Actual State

目前 Cluster：

```text
5 Pods
```

代表：

Cluster 與 Git 已經不同。

這就是：

```text
Configuration Drift
```

---

# Reconciliation

Argo CD 持續比較：

```text
Desired State
```

與：

```text
Actual State
```

如果不同：

```text
Git

2 Pods

↓

Cluster

5 Pods

↓

Argo CD

↓

Scale 回 2 Pods
```

這個持續同步的過程稱為：

```text
Reconciliation
```

---

# Self Heal

若有人直接執行：

```bash
kubectl scale deployment api --replicas=10
```

Git：

```text
replicas = 2
```

Argo CD 偵測到 Drift 後：

```text
10 Pods

↓

2 Pods
```

自動恢復到 Git 定義的狀態。

這就是：

```text
Self Heal
```

---

# GitOps 架構

```text
Git Repository
        │
Desired State
        │
Argo CD
        │
Reconciliation
        │
Kubernetes Cluster
        │
Actual State
```

---

# Hands-on

建立：

```text
gitops/
```

指令：

```bash
mkdir gitops
```

確認：

```bash
tree -L 1
```

專案結構已新增：

```text
gitops/
```

---

# 今日重點

* GitOps 以 Git 作為唯一事實來源。
* 不直接修改 Kubernetes Cluster。
* Desired State 定義於 Git。
* Actual State 為 Cluster 現況。
* Argo CD 持續進行 Reconciliation。
* Self Heal 可自動修正 Configuration Drift。

---

# Interview Q&A

## Q1：什麼是 GitOps？

GitOps 是以 Git Repository 作為 Kubernetes 唯一設定來源，由 Git 控制部署與變更。

---

## Q2：什麼是 Desired State？

Desired State 是 Git Repository 中定義的平台狀態，例如 Deployment、Service、Ingress、Replica 數量等。

---

## Q3：什麼是 Reconciliation？

Reconciliation 是 GitOps Controller（例如 Argo CD）持續比較 Desired State 與 Actual State，並自動同步兩者的過程。

---

# 今日成果

平台開始從傳統部署方式：

```text
Engineer

↓

kubectl apply
```

邁向企業級 GitOps：

```text
Engineer

↓

Git Commit

↓

Git Push

↓

Argo CD

↓

Kubernetes
```

建立 GitOps 思維，為後續 Helm、Kustomize、Argo CD 做準備。

---

# 下一步

Week8 Day2：

Helm Foundation

學習：

* Helm Chart
* Chart.yaml
* values.yaml
* templates
* Helm Template Render
* 建立第一個 Helm Chart

