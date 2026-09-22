<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day6 — Helm 與 Kustomize 整合

[上一課](<Day5_Kustomize_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day7-GitOps_Multi_Environment_Integration.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史錯誤與整合設定。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

此為舊 K3s local-image 錯誤，現在 API 預設 IfNotPresent 與 registry 不同。Overlay 可透過 resources/generators 引入或產生物件，不是絕對「不建立 Resource」。目前主 overlay 獨立且開 worker；舊 dev 還引入監控與 runtime，不能混用套用。

## 程式／設定與來源

本次核對：[kustomize/overlays/dev/kustomization.yaml](<../../kustomize/overlays/dev/kustomization.yaml>)、[helm/api/values.yaml](<../../helm/api/values.yaml>)、[kustomize/overlays/gpu-sg-platform/kustomization.yaml](<../../kustomize/overlays/gpu-sg-platform/kustomization.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day6-Helm-Kustomize-Integration.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
ErrImageNeverPull
```

原文保留 image／patch／NodePort 錯誤字串，但缺完整 log；本次未 build/apply，亦不表示目前三環境都可成功。

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

# Week8 Day6 - Helm + Kustomize Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/api/Chart.yaml](../../helm/api/Chart.yaml)
- [helm/api/values-dev.yaml](../../helm/api/values-dev.yaml)
- [helm/api/values.yaml](../../helm/api/values.yaml)
- [kustomize/overlays/dev/deployment-patch.yaml](../../kustomize/overlays/dev/deployment-patch.yaml)
- [kustomize/overlays/dev/kustomization.yaml](../../kustomize/overlays/dev/kustomization.yaml)

---

## 學習目標

完成 Helm 與 Kustomize 整合，建立可支援 Dev / Stage / Prod 的多環境部署流程。

---

# 完成成果

✅ API Helm Chart

✅ Redis Helm Chart

✅ PostgreSQL Helm Chart

✅ Kustomize Dev / Stage / Prod Overlay

✅ Helm + Kustomize Integration

✅ Dev 環境成功部署

---

# 專案架構

```
helm/
├── api/
├── redis/
└── postgres/

kustomize/
└── overlays/
    ├── dev/
    ├── stage/
    └── prod/
```

---

# 部署流程

```
Developer
      │
      ▼
kustomize/overlays/dev
      │
      ▼
Helm Render
      │
      ├── api
      ├── redis
      └── postgres
      │
      ▼
Kustomize Patch
      │
      ▼
kubectl apply
      │
      ▼
Kubernetes
```

---

# Helm 實際讀取順序

```
Chart.yaml
      ↓
values.yaml
      ↓
values-dev.yaml
      ↓
templates/*
      ↓
Render YAML
```

---

# Kustomize 做什麼？

Overlay 不建立 Resource。

Overlay 只負責：

- 選擇 Helm Chart
- 指定 Namespace
- 套用 Patch
- 套用不同環境設定

例如：

- replicas
- APP_ENV
- host

---

# Chart 職責

## API

- Deployment
- Service
- ConfigMap
- HPA
- Ingress

## Redis

- Deployment
- Service

## PostgreSQL

- StatefulSet
- Service
- Secret
- PVC

---

# 部署指令

```bash
kubectl kustomize kustomize/overlays/dev \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone \
| kubectl apply -f -
```

---

# 今天踩到的重要坑

### 1. Helm Template 不要寫死 Namespace

❌

```yaml
namespace: hpc-platform
```

✅

```yaml
namespace: {{ .Release.Namespace }}
```

---

### 2. Patch 必須匹配正確 Namespace

否則：

```
no resource matches strategic merge patch
```

---

### 3. Secret 不要重複建立

PostgreSQL Chart：

建立 Secret

API Chart：

只引用 Secret

---

### 4. Dev 不使用 NodePort

避免：

```
provided port is already allocated
```

Dev 使用：

```
ClusterIP
```

---

### 5. imagePullPolicy: Never

代表：

Kubernetes 不會下載 Image。

新的 Image Tag 必須：

```
docker tag

↓

docker save

↓

k3s ctr images import
```

否則：

```
ErrImageNeverPull
```

---

### 6. replicaCount 不等於最終 Pod 數

```
Deployment replicas

↓

HPA

↓

依 CPU 自動 Scale
```

Deployment 的 replicas 只是初始值。

---

# Day6 完成後架構

```
Developer
      │
      ▼
Kustomize
      │
      ▼
Helm
      │
      ▼
Render YAML
      │
      ▼
Kubernetes
```

---

# Interview Q&A

## Q1：Helm 與 Kustomize 的角色差異？

**A：**

Helm 負責產生（Render）YAML。

Kustomize 負責依照不同環境修改 Render 後的 YAML。

---

## Q2：為什麼要拆成 api、redis、postgres 三個 Chart？

**A：**

因為每個服務可以獨立維護、升級、重複使用，符合企業實務。

---

## Q3：為什麼 Helm Template 不應寫死 Namespace？

**A：**

同一個 Chart 要能部署到 dev、stage、prod，不應綁定單一 Namespace。

---

## Q4：Deployment 的 replicas 為什麼最後會變？

**A：**

Deployment 的 replicas 是初始值，HPA 會依 CPU 使用率動態調整 Pod 數量。

---

## Q5：為什麼 Dev 使用 ClusterIP，而不是 NodePort？

**A：**

Dev 已經透過 Ingress 對外提供服務，使用 ClusterIP 可避免 NodePort 衝突並更符合實務部署方式。
