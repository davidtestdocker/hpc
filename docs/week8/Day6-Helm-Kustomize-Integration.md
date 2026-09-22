<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day6 — Helm 與 Kustomize 整合

[上一課](<Day5_Kustomize_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day7-GitOps_Multi_Environment_Integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

本專案先讓 Kustomize 使用 helmCharts 產生資源，再套 patches。load restrictor 設定允許引用 repo 內 chart；這不是對叢集發起 apply。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[scripts/platform.py](<../../scripts/platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def render():
    # 只渲染 Kustomize／Helm，不會套用任何資源到叢集。
    return command([
        "kubectl", "kustomize", "kustomize/overlays/gpu-sg-platform",
        "--enable-helm", "--load-restrictor", "LoadRestrictionsNone",
    ])


def ready_nodes(nodes, pool, gpu=False):
    # Ready 還不夠：節點也必須可排程；GPU 檢查另外要求公布 NVIDIA 資源。
    for node in nodes.get("items", []):
        if node["metadata"].get("labels", {}).get("cloud.google.com/gke-nodepool") != pool:
            continue
        if node.get("spec", {}).get("unschedulable", False):
            continue
        status = node.get("status", {})
        ready = any(c["type"] == "Ready" and c["status"] == "True"
                    for c in status.get("conditions", []))
        if ready and (not gpu or int(status.get("allocatable", {}).get("nvidia.com/gpu", 0)) > 0):
            return True
    return False


def inspect(context, require_gpu=True):
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week8/Day6-Helm-Kustomize-Integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
