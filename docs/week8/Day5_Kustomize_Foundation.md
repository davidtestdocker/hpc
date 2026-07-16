# Week8 Day5 - Kustomize Foundation

## 本日成果

完成 Kustomize 基礎架構，建立 Base / Overlay 多環境管理模式，並完成 dev、stage、prod 三個環境的 Render 與驗證。

> **注意：本日尚未整合 Helm。Helm + Kustomize Integration 將於 Week8 Day6 完成。**

---

# 今日目標

學習 Kustomize 的核心概念：

* Base
* Overlay
* Patch
* Namespace
* Images
* Resources
* Environment
* Ingress
* 多環境管理

---

# 為什麼需要 Kustomize？

Kustomize 並不是 Template Engine。

它的核心概念是：

```text
Base
    │
    ▼
Overlay
    │
    ▼
Patch
    │
    ▼
新的 Kubernetes YAML
```

它是在**既有 Kubernetes YAML** 上做修改，而不是重新產生 YAML。

---

# 建立目錄

建立：

```text
kustomize/

├── base
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── kustomization.yaml
│
└── overlays
    ├── dev
    │   ├── deployment-patch.yaml
    │   ├── ingress-patch.yaml
    │   └── kustomization.yaml
    │
    ├── stage
    │   ├── deployment-patch.yaml
    │   ├── ingress-patch.yaml
    │   └── kustomization.yaml
    │
    └── prod
        ├── deployment-patch.yaml
        ├── ingress-patch.yaml
        └── kustomization.yaml
```

---

# Base

Base 保存所有環境共用設定。

包含：

* Deployment
* Service
* Ingress

Base 不包含任何 dev、stage、prod 專屬設定。

---

# Overlay

Overlay 只保存環境差異。

例如：

```text
dev

↓

replicas = 2

image = :dev

APP_ENV = dev
```

Base 完全不用修改。

---

# Deployment Patch

Base：

```yaml
replicas: 1
```

Dev：

```yaml
replicas: 2
```

Stage：

```yaml
replicas: 3
```

Prod：

```yaml
replicas: 5
```

透過 Strategic Merge Patch 修改 Deployment。

---

# Namespace

各環境：

Dev：

```text
hpc-platform-dev
```

Stage：

```text
hpc-platform-stage
```

Prod：

```text
hpc-platform-prod
```

使用：

```yaml
namespace:
```

統一修改所有 Namespaced Resource，而不是逐一 Patch。

---

# Image Tag

Dev：

```text
hpc-ai-benchmark-platform-api:dev
```

Stage：

```text
hpc-ai-benchmark-platform-api:stage
```

Prod：

```text
hpc-ai-benchmark-platform-api:v1.0.0
```

使用：

```yaml
images:
```

修改，不需改 Deployment。

---

# APP_ENV

Base：

```text
APP_ENV=prod
```

Dev：

```text
APP_ENV=dev
```

Stage：

```text
APP_ENV=stage
```

Prod：

```text
APP_ENV=prod
```

利用 Deployment Patch 精準修改 Container Environment。

---

# Resources

Dev：

```text
CPU Request : 50m
CPU Limit   : 200m

Memory Request : 64Mi
Memory Limit   : 256Mi
```

Stage：

```text
CPU Request : 100m
CPU Limit   : 300m

Memory Request : 128Mi
Memory Limit   : 384Mi
```

Prod：

```text
CPU Request : 250m
CPU Limit   : 1000m

Memory Request : 256Mi
Memory Limit   : 1Gi
```

不同環境使用不同資源配置。

---

# Ingress Host

Dev：

```text
api-dev.hpc.local
```

Stage：

```text
api-stage.hpc.local
```

Prod：

```text
api.hpc.example.com
```

透過 Ingress Patch 管理。

---

# Render

Dev：

```bash
kubectl kustomize overlays/dev
```

Stage：

```bash
kubectl kustomize overlays/stage
```

Prod：

```bash
kubectl kustomize overlays/prod
```

成功產生三套不同環境的 Kubernetes YAML。

---

# Dry Run 驗證

建立 Render 結果：

```bash
kubectl kustomize overlays/dev > /tmp/dev.yaml
kubectl kustomize overlays/stage > /tmp/stage.yaml
kubectl kustomize overlays/prod > /tmp/prod.yaml
```

驗證：

```bash
kubectl apply --dry-run=client -f /tmp/dev.yaml
kubectl apply --dry-run=client -f /tmp/stage.yaml
kubectl apply --dry-run=client -f /tmp/prod.yaml
```

三個環境皆成功通過驗證。

---

# 三個環境

## Dev

* Namespace：hpc-platform-dev
* Replicas：2
* Image：hpc-ai-benchmark-platform-api:dev
* APP_ENV：dev
* Host：api-dev.hpc.local

---

## Stage

* Namespace：hpc-platform-stage
* Replicas：3
* Image：hpc-ai-benchmark-platform-api:stage
* APP_ENV：stage
* Host：api-stage.hpc.local

---

## Prod

* Namespace：hpc-platform-prod
* Replicas：5
* Image：hpc-ai-benchmark-platform-api:v1.0.0
* APP_ENV：prod
* Host：api.hpc.example.com

---

# 本日重點

Kustomize 並不是用來取代 Helm。

今天完成的是：

```text
Base Kubernetes YAML
        │
        ▼
Kustomize Overlay
        │
        ├── dev
        ├── stage
        └── prod
```

**今天尚未進行 Helm 整合。**

Helm + Kustomize 的整合流程將於 Day6 完成。

---

# Interview Q&A

## Q1：Kustomize 的 Base 與 Overlay 分別負責什麼？

Base 保存所有環境共用的 Kubernetes 資源；Overlay 只保存各環境的差異設定，避免複製整份 YAML。

---

## Q2：什麼情況下使用 `namespace:`，什麼情況使用 Patch？

如果整個環境的資源都要切換到同一個 Namespace，使用 `namespace:` 最簡單；只有個別資源需要不同 Namespace 時，才使用 Patch。

---

## Q3：今天完成 Helm 與 Kustomize 整合了嗎？

沒有。今天完成的是 Kustomize Foundation。Helm + Kustomize Integration 將於 Week8 Day6 完成。

---

# 今日成果

完成：

* Kustomize Base
* Kustomize Overlay
* Deployment Patch
* Ingress Patch
* Namespace 管理
* Image Tag 管理
* APP_ENV 管理
* Resource 管理
* Dev / Stage / Prod 三環境
* Render 驗證
* Client Dry Run 驗證

平台已具備企業常見的 Kustomize 多環境管理能力。

---

# 下一步

Week8 Day6：

**Helm + Kustomize Integration**

學習：

* Helm 與 Kustomize 的整合方式
* Helm Render 與 Kustomize Overlay 的關係
* 企業 GitOps 專案架構
* 為 Argo CD 做完整準備

