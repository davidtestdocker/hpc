<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day5 — Kustomize overlay

[上一課](<Day4_Helm_Advanced.md>) · [本週目錄](README.md) · [下一課](<Day6-Helm-Kustomize-Integration.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史三環境 render 描述。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

文內 base/ 與 ingress-patch 是舊結構；現在 overlays 直接組 Helm charts。文內未加 --enable-helm 的指令不是現行入口。client dry-run 不能证明 controller、依賴或 workload 可執行；namespace 變換也不等於建立 Namespace 物件。

## 程式／設定與來源

本次核對：[kustomize/overlays/dev/kustomization.yaml](<../../kustomize/overlays/dev/kustomization.yaml>)、[kustomize/overlays/stage/kustomization.yaml](<../../kustomize/overlays/stage/kustomization.yaml>)、[kustomize/overlays/prod/kustomization.yaml](<../../kustomize/overlays/prod/kustomization.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day5_Kustomize_Foundation.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
CPU Request : 50m
```

資源數值為當時配置摘要；/tmp 渲染產物未保存，三環境成功敘述不升級成當前已部署。

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

# Week8 Day5 - Kustomize Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

文中的 `base/`、`ingress-patch.yaml` 與 `/tmp/*.yaml` 為歷史結構或產物；目前可追蹤的是以下 overlays。

- [kustomize/overlays/dev/deployment-patch.yaml](../../kustomize/overlays/dev/deployment-patch.yaml)
- [kustomize/overlays/dev/kustomization.yaml](../../kustomize/overlays/dev/kustomization.yaml)
- [kustomize/overlays/prod/deployment-patch.yaml](../../kustomize/overlays/prod/deployment-patch.yaml)
- [kustomize/overlays/prod/kustomization.yaml](../../kustomize/overlays/prod/kustomization.yaml)
- [kustomize/overlays/stage/deployment-patch.yaml](../../kustomize/overlays/stage/deployment-patch.yaml)
- [kustomize/overlays/stage/kustomization.yaml](../../kustomize/overlays/stage/kustomization.yaml)

---

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
