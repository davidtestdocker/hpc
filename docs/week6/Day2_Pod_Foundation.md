<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day2 — Pod 的範圍

[上一課](<Day1_Kubernetes_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day3_Deployment_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

同一 Pod 的容器共用網路，可透過 localhost 通訊；不同 Pod 要用服務／網路連線。Pod Running 不保證應用 Ready，更不保證工作 completed。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
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
            # ConfigMap 提供服務位址與輪詢設定；密碼沿用外部建立的 Secret。
            - configMapRef:
                name: {{ include "api.fullname" . }}-config
            - secretRef:
                name: postgres-secret
          resources:
            # requests 供排程器計算容量，limits 限制容器 CPU／記憶體上限。
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week6/Day2_Pod_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day2 - Pod Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)

---

## 今日平台增加什麼

今天建立 Kubernetes 最重要的核心概念：

```text
Container

↓

Pod
```

理解：

> Pod 是 Kubernetes 最小的部署單位（Smallest Deployable Unit）。

而不是：

```text
Container
```

---

# Platform Problem

目前平台：

```text
Docker Compose

api Container
redis Container
postgres Container
```

目前：

```text
1 Service

=

1 Container
```

如果未來：

API 需要：

* Log Agent
* Monitoring Agent
* Service Mesh Proxy

Docker 會變成：

```text
api Container

log Container

otel Container
```

Container 彼此沒有共同生命週期。

---

# Kubernetes 如何解決？

Kubernetes 增加：

```text
Pod
```

例如：

```text
api Pod
│
├── api Container
├── log-agent Container
└── otel-agent Container
```

Pod 內所有 Container：

* 共用 Network Namespace
* 共用 localhost
* 共用 Volume
* 一起建立
* 一起刪除

因此：

Pod 才是 Kubernetes 的最小部署單位。

---

# Docker 與 Kubernetes

Docker：

```text
Container
```

Kubernetes：

```text
Pod
```

目前：

```text
1 Pod

=

1 Container
```

但：

```text
Pod

≠

Container
```

一個 Pod 可以有多個 Container。

---

# 今日知識鏈

```text
Container
      │
      ▼
Pod
      │
      ▼
Pod Lifecycle
```

---

# Pod Lifecycle

Pod 常見生命週期：

```text
Pending

↓

Running

↓

Succeeded / Failed

↓

Deleted
```

說明：

Pending

Image 尚未下載完成，或等待排程。

Running

Pod 已建立完成，Container 正常執行。

Succeeded

工作型 Pod 已成功完成。

Failed

Pod 執行失敗。

Deleted

Pod 已被 Kubernetes 移除。

---

# Pod 架構

目前平台：

```text
api Pod
│
└── api Container

redis Pod
│
└── redis Container

postgres Pod
│
└── postgres Container
```

目前：

```text
3 Pods

3 Containers
```

只是目前每個 Pod 都只有一個 Container。

未來：

```text
api Pod
│
├── api
├── envoy
└── otel-agent
```

仍然只有：

```text
1 Pod
```

---

# 為什麼 Kubernetes 不直接管理 Container？

Container 缺少：

* 共用生命週期
* 共用 Network Namespace
* 共用 localhost
* 共用 Storage

因此 Kubernetes 增加：

```text
Pod
```

讓相關 Container 成為一個部署單位。

---

# Platform Evolution

目前：

```text
Docker Host
│
├── api Container
├── redis Container
└── postgres Container
```

未來：

```text
Kubernetes Cluster
│
├── api Pod
│      └── api Container
│
├── redis Pod
│      └── redis Container
│
└── postgres Pod
       └── postgres Container
```

---

# 今日重點

* Pod 是 Kubernetes 最小部署單位。
* Container 永遠運行於 Pod 內。
* Pod 可以包含一個或多個 Container。
* 同一個 Pod 內的 Container 共用 Network、localhost 與 Volume。
* Pod 擁有共同生命週期。

---

# Interview Q&A

## Q1：Pod 和 Container 有什麼差別？

Container 是應用程式執行單位。

Pod 是 Kubernetes 管理 Container 的最小部署單位，可以包含一個或多個 Container，並提供共同的網路、儲存與生命週期。

---

## Q2：為什麼 Kubernetes 不直接管理 Container？

因為許多相關 Container 需要一起部署、一起停止、共享網路與儲存空間。

Pod 將這些 Container 包裝成同一個部署單位，使 Kubernetes 更容易管理與調度。

---

# 今日成果

建立 Kubernetes 最重要的第二個核心觀念：

```text
Container

↓

Pod
```

理解：

* Docker 管理 Container。
* Kubernetes 管理 Pod。
* Pod 是一個或多個 Container 的執行與部署單位。

---

# 下一步

Week6 Day3：

Deployment Foundation

開始學習：

```text
Pod

↓

ReplicaSet

↓

Deployment
```

理解 Kubernetes 如何透過 Deployment 維持 Pod 的期望數量（Desired State）、自動修復（Self Healing）與滾動更新（Rolling Update）。
