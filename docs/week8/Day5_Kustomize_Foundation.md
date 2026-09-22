<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day5 — Kustomize overlay

[上一課](<Day4_Helm_Advanced.md>) · [本週目錄](README.md) · [下一課](<Day6-Helm-Kustomize-Integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

overlay 描述環境差異，patch 的 target 決定影響哪些資源。nodeSelector patch 限制 system 服務位置，不等於所有工作都搬到 system-pool。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[kustomize/overlays/gpu-sg-platform/kustomization.yaml](<../../kustomize/overlays/gpu-sg-platform/kustomization.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
patches:
  - path: system-pool-patch.yaml
    target:
      kind: Deployment
      name: api|redis
  - path: system-pool-patch.yaml
    target:
      kind: StatefulSet
      name: postgres
  - path: api-serviceaccount-patch.yaml
    target:
      kind: Deployment
      name: api
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week8/Day5_Kustomize_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
