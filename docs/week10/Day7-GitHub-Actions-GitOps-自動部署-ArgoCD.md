# Week10 Day7 - GitHub Actions + GitOps 自動部署

## 今日新增

今天完成整套 GitOps CI/CD Pipeline。

流程如下：

```
Developer
    │
git push
    │
    ▼
GitHub Actions
    │
    ├── Python Syntax Check
    ├── Ruff
    ├── Pytest
    ├── Docker Build
    ├── Push Artifact Registry
    ├── 更新 Helm Image Tag
    └── Commit & Push
             │
             ▼
        Git Repository
             │
             ▼
          Argo CD
             │
        Detect Change
             │
             ▼
          Auto Sync
             │
             ▼
      Kustomize + Helm
             │
             ▼
        Kubernetes
             │
             ▼
      Rolling Update
```

---

# GitHub Actions

Workflow

```
.github/workflows/ci.yml
```

完成流程：

```
Checkout

↓

Python Syntax Check

↓

Ruff

↓

Pytest

↓

Docker Build

↓

Push Artifact Registry

↓

更新 values-dev.yaml

↓

Git Commit

↓

Git Push
```

---

# Image 更新

GitHub Actions 使用

```
${{ github.sha }}
```

更新

```
helm/api/values-dev.yaml
```

例如

```yaml
image:
  tag: 07d197082a66...
```

---

# Argo CD

Application

```
hpc-dev
```

監控

```
master

↓

kustomize/overlays/dev
```

Git 有變更

↓

Argo CD Detect

↓

Sync

↓

Apply

↓

Healthy

---

# Kustomize

Argo CD Sync

↓

讀取

```

kustomize/overlays/dev

```

↓

Helm Render

```

helm/api
helm/postgres
helm/redis

```

↓

產生 Kubernetes YAML

---

# Rolling Update

Deployment Template 發生變化

↓

建立新的 ReplicaSet

↓

建立新的 Pod

↓

舊 Pod Terminate

↓

完成 Rolling Update

---

# PostgreSQL 修正

GKE Persistent Disk

根目錄存在

```

lost+found

```

PostgreSQL 初始化失敗

```

initdb:
directory exists but is not empty

```

新增

```yaml
- name: PGDATA
  value: /var/lib/postgresql/data/pgdata
```

Database 初始化位置

```

/var/lib/postgresql/data/pgdata

```

避免直接初始化於 Mount Root。

---

# Commands

查看 Application

```bash
kubectl get app -n argocd
```

查看 Deployment

```bash
kubectl get deployment -n hpc-platform-dev
```

查看 ReplicaSet

```bash
kubectl get rs -n hpc-platform-dev
```

查看 Pods

```bash
kubectl get pods -n hpc-platform-dev
```

查看 Image

```bash
kubectl get deployment api \
-n hpc-platform-dev \
-o jsonpath='{.spec.template.spec.containers[0].image}'
```

查看 Workflow

```
Actions
```

查看 Image Tag

```bash
cat helm/api/values-dev.yaml
```

---

# Interview

## Q1

GitHub Actions 更新哪個檔案後，Argo CD 才會偵測到 Git 變更？

**A：**

```
helm/api/values-dev.yaml
```

Image Tag 改變後，Git Commit Push。

Argo CD 發現 Git 與 Cluster 不一致，就會開始 Sync。

---

## Q2

Argo CD 如何知道要部署哪個 Helm Chart？

**A：**

Application 指向

```
kustomize/overlays/dev
```

Kustomize 讀取

```
kustomization.yaml
```

其中

```yaml
helmCharts:
  - name: api
  - name: postgres
  - name: redis
```

再到

```
helm/
```

找到對應 Chart Render 成 Kubernetes YAML，最後套用到 Cluster。

---

# 今日成果

✅ GitHub Actions CI

✅ Docker Build

✅ Push Artifact Registry

✅ 更新 Helm Image Tag

✅ Git Commit & Push

✅ Argo CD Auto Sync

✅ Helm + Kustomize Render

✅ Rolling Update

✅ PostgreSQL PGDATA 修正

✅ 完成完整 GitOps CI/CD Pipeline
