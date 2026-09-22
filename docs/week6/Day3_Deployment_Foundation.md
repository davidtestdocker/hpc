<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day3 — Deployment 與副本

[上一課](<Day2_Pod_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day4_Service_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Deployment 管理 replica 與更新策略。worker 用一副本、Recreate，降低 demo 升級時的容量需求；但程序被重新建立不等於工作狀態消失，接續靠外部 record。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  strategy:
    # Recreate 先停舊版再啟新版，避免小型 system-pool 承擔升級 surge 容量。
    type: Recreate
  selector:
    # selector 與下方 Pod labels 相符，讓 Deployment 管理自己的 worker Pods。
    matchLabels:
      app: {{ include "api.fullname" . }}-worker
  template:
    metadata:
      labels:
        app: {{ include "api.fullname" . }}-worker
    spec:
      # 沿用 namespace 最小 RBAC 身分，允許建立／讀取 JobSet 與回收 launcher log。
      serviceAccountName: {{ .Values.worker.serviceAccountName }}
      # 預設排入 system-pool；worker 負責協調，自己不申請 GPU。
      nodeSelector:
        {{- toYaml .Values.worker.nodeSelector | nindent 8 }}
      containers:
        - name: worker
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          # 覆寫映像預設的 Uvicorn 命令，啟動獨立 Python worker。
          command: ["python", "-m", "api.worker"]
          envFrom:
```

## 已有結果與解讀

### CPU 叢集重建：已保存的驗收結果

日期：2026-09-21。環境：隔離 CPU-only GKE 重建驗收；不是主環境的多 GPU 實驗。該次叢集已清理，讀這份結果不需要重新建立。

```json
{
  "recorded_at": "2026-09-21",
  "scope": "fresh CPU-only GKE bootstrap and platform acceptance; excludes GPU and MPI execution",
  "result": "pass",
  "terraform": {
    "apply": "3 added",
    "post_apply_plan": "No changes",
    "destroy": "3 destroyed",
    "state_resources_after_destroy": 0,
    "cluster_lookup_after_destroy": "404 Not Found"
  },
  "controllers": {
    "jobset": "v0.12.0 Ready on system-pool with 100m CPU request",
    "kueue": "v0.19.2 Ready on system-pool with Recreate deployment strategy"
  },
  "platform": {
    "api": "Running on system-pool; /health healthy",
    "redis": "Running on system-pool; connected; PVC Bound",
    "postgres": "Running on system-pool; jobs table query succeeded; PVC Bound",
    "overlay_diff_after_apply": "empty"
  },
  "security": {
    "postgres_secret": "created from external env file; value not captured",
    "mpi_ssh_key": "generated in temporary directory; value not captured",
    "api_service_account_create_jobsets": "yes",
    "api_service_account_delete_pods": "no"
  },
  "limitations": [
    "gpu-pool had zero nodes because project-wide GPU quota was exhausted",
    "no MPI workload was submitted in this CPU-only rehearsal",
    "database initialization used create_all rather than schema migration"
  ]
}
```

解讀：Terraform 建立 3 個資源、無 drift，JobSet／Kueue controllers 和 API／Redis／DB 驗收成功；create JobSet 權限允許，delete Pod 權限拒絕。最後 destroy 3、state 空、cluster 查詢 404，證明當次隔離叢集已刪除。**不包含 GPU 或 MPI 執行驗收**，也不是所有雲端資源的停費證明。

來源：[原始 CPU bootstrap JSON](<../evidence/cpu-bootstrap-acceptance-20260921.json>)。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week6/Day3_Deployment_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day3 - Deployment Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/redis-deployment.yaml](../../k8s/redis-deployment.yaml)

---

## 今日平台增加什麼

今天建立 Kubernetes 最重要的控制器（Controller）：

```text
Deployment
```

平台知識鏈從：

```text
Container
    ↓
Pod
```

演進成：

```text
Container
    ↓
Pod
    ↓
ReplicaSet
    ↓
Deployment
```

Deployment 是 Kubernetes 中最常使用的 Workload Resource。

---

# Platform Problem

如果只有 Pod：

```text
api Pod
```

當：

```text
kubectl delete pod api-xxxxx
```

結果：

```text
Pod 消失
```

Kubernetes **不會自動建立新的 Pod**。

原因：

沒有人告訴 Kubernetes：

```text
應該要有幾個 Pod
```

因此需要：

```text
Deployment
```

來描述：

```text
Desired State
```

---

# Desired State

Deployment 的核心概念：

```text
Desired State
```

例如：

```yaml
replicas: 3
```

代表：

```text
API

應該永遠保持：

3 Pods
```

如果：

```text
api-2 Crash
```

目前：

```text
Actual State = 2 Pods
```

Deployment：

比較：

```text
Desired = 3

Actual = 2
```

建立新的 Pod：

```text
api-new
```

恢復：

```text
3 Pods
```

這就是：

```text
Self Healing
```

---

# Deployment 的責任

Deployment 不直接管理：

* Container
* Node

Deployment 管理：

```text
Deployment
      │
      ▼
ReplicaSet
      │
      ▼
Pod
      │
      ▼
Container
```

因此：

真正操作的是：

```text
Deployment
```

而不是：

```text
Pod
```

---

# ReplicaSet

Deployment 不直接建立 Pod。

真正建立 Pod 的是：

```text
ReplicaSet
```

架構：

```text
Deployment
      │
      ▼
ReplicaSet
      │
      ▼
Pods
```

ReplicaSet 負責：

* 建立 Pod
* 維持 Pod 數量

Deployment：

負責：

* 管理 ReplicaSet
* Rolling Update
* Rollback

---

# Scaling

Deployment：

除了 Self Healing。

另一個重要功能：

```text
Scaling
```

例如：

```yaml
replicas: 1
```

修改：

```yaml
replicas: 5
```

Deployment：

自動建立：

```text
5 Pods
```

不需要人工建立。

---

# Rolling Update

Deployment：

更新 Image：

```text
api:v1

↓

api:v2
```

不是：

```text
全部刪除

↓

全部建立
```

而是：

```text
v1

↓

v1 + v2

↓

全部 v2
```

降低服務中斷時間。

---

# 今日知識鏈

```text
Container
      │
      ▼
Pod
      │
      ▼
ReplicaSet
      │
      ▼
Deployment
```

Deployment 是 Kubernetes 中管理 Pod 的主要入口。

---

# Platform Evolution

Docker：

```text
Docker

↓

Container
```

Kubernetes：

```text
Deployment
      │
ReplicaSet
      │
Pods
      │
Containers
```

平台管理對象：

從：

```text
Container
```

變成：

```text
Deployment
```

---

# 今日重點

Deployment：

負責：

* Desired State
* Self Healing
* Scaling
* Rolling Update

ReplicaSet：

負責：

* 建立 Pod
* 維持 Pod 數量

Pod：

負責：

* 執行 Container

三者職責不同。

---

# Interview Q&A

## Q1：Deployment 與 Pod 有什麼差別？

Pod 是應用程式執行單位。

Deployment 是管理 Pod 的 Controller。

Deployment 會根據 Desired State 建立、更新與維護 Pod。

---

## Q2：為什麼 Deployment 可以做到 Self Healing？

Deployment 持續比較：

```text
Desired State

vs

Actual State
```

如果實際 Pod 數量不足，就會透過 ReplicaSet 建立新的 Pod，恢復到預期數量。

---

# 今日成果

建立 Kubernetes Workload 模型：

```text
Deployment
      │
      ▼
ReplicaSet
      │
      ▼
Pod
      │
      ▼
Container
```

理解：

* Deployment 管理 ReplicaSet。
* ReplicaSet 管理 Pod。
* Pod 執行 Container。
* Kubernetes 透過 Desired State 維持平台正常運作。

---

# 下一步

Week6 Day4：

Service Foundation

建立 Kubernetes 網路模型：

```text
Deployment
      │
      ▼
Pods
      ▲
      │
Service
```

理解：

* Stable Endpoint
* Load Balancing
* Service Discovery
* Pod IP 為什麼不能直接使用
