<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day4 — Service 與 selector

[上一課](<Day3_Deployment_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day5_K3s_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Service 依 labels 選端點，targetPort 指向容器服務；service name 的 DNS 解析需在適當 namespace。selector 不匹配時，Service 存在仍可能沒有可用 endpoints。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[helm/api/templates/service.yaml](<../../helm/api/templates/service.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  selector:
    {{- include "api.selectorLabels" . | nindent 4 }}

  # 連接埠設定清單；容器宣告埠號本身不會自動對外公開。
  ports:
    - port: {{ .Values.service.port }}
      # Service 將流量轉送至 Pod 的目標埠號或命名埠。
      targetPort: {{ .Values.service.targetPort }}
      {{- if eq .Values.service.type "NodePort" }}
      # 經節點 IP 開放的 Service 埠號，適用 NodePort／部分 LoadBalancer 配置。
      nodePort: {{ .Values.service.nodePort }}
      {{- end }}
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week6/Day4_Service_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day4 - Service Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-service.yaml](../../k8s/api-service.yaml)
- [k8s/redis-service.yaml](../../k8s/redis-service.yaml)

---

## 今日平台增加什麼

今天建立 Kubernetes 最重要的網路元件：

```text
Service
```

平台知識鏈從：

```text
Container
    ↓
Pod
    ↓
ReplicaSet
    ↓
Deployment
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
    ↓
Service
```

Service 負責讓 Pod 可以被穩定存取，而不需要依賴 Pod IP。

---

# Platform Problem

Deployment 已經可以建立多個 Pod。

例如：

```text
api Deployment

↓

api Pod A
api Pod B
api Pod C
```

每個 Pod 都有自己的 IP：

```text
api-a    10.42.0.10

api-b    10.42.1.25

api-c    10.42.3.41
```

但是：

Pod 並不是永久存在。

如果：

```text
api-b Crash
```

Deployment：

```text
建立新的 Pod
```

新的 Pod：

```text
api-d

IP

10.42.5.12
```

原本：

```text
10.42.1.25
```

已經不存在。

如果 Client 都直接連 Pod IP：

平台會持續中斷。

---

# Kubernetes 如何解決？

Kubernetes 增加：

```text
Service
```

架構：

```text
Client
    │
    ▼
Service
    │
    ├── api Pod A
    ├── api Pod B
    └── api Pod C
```

Client 永遠只需要知道：

```text
api-service
```

不用知道：

* Pod Name
* Pod IP

---

# Service 的責任

Service 不建立 Pod。

Service 不管理 Deployment。

Service 的責任：

```text
Stable Endpoint

+

Load Balancing
```

---

# Stable Endpoint

Service 提供固定入口：

```text
api-service
```

即使：

```text
api Pod Crash
```

Service 名稱仍然不變。

Client 永遠透過：

```text
api-service
```

存取 API。

---

# Load Balancing

假設：

```text
api Pod A

api Pod B

api Pod C
```

Client 發送：

```text
POST /benchmark
```

Service：

自動分配：

```text
Request 1

↓

Pod A

Request 2

↓

Pod B

Request 3

↓

Pod C
```

Client 不需要知道 Pod 數量與位置。

---

# Service Discovery

Kubernetes 每個 Service 都會有固定 DNS。

例如：

```text
redis-service

postgres-service

api-service
```

Pod 與 Pod 之間：

透過：

```text
Service Name
```

即可互相通訊。

不用使用：

* Pod Name
* Pod IP

---

# Deployment 與 Service

Deployment：

負責：

```text
Pod 數量
```

Service：

負責：

```text
Pod 存取
```

架構：

```text
Deployment
      │
      ▼
Pods
      ▲
      │
Service
```

兩者互相合作，但責任不同。

---

# Platform Evolution

目前平台：

```text
Docker Compose

api

redis

postgres
```

Docker Compose：

透過：

```text
Compose Network
```

互相連線。

例如：

```text
redis:6379
```

Kubernetes：

變成：

```text
api-service

redis-service

postgres-service
```

所有服務：

永遠透過：

```text
Service
```

互相通訊。

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
      │
      ▼
Service
```

至此完成 Kubernetes 最核心的五個基礎元件。

---

# 今日重點

Service 提供：

* Stable Endpoint
* Load Balancing
* Service Discovery

Deployment：

負責維持：

```text
Pod
```

Service：

負責提供：

```text
Pod 存取
```

Pod IP 不應該直接提供給 Client 使用。

---

# Interview Q&A

## Q1：為什麼不能直接使用 Pod IP？

Pod 是短生命週期資源。

Pod 重建後，IP 很可能改變。

因此應透過 Service 提供固定入口，避免 Client 依賴會變動的 Pod IP。

---

## Q2：Deployment 與 Service 有什麼差別？

Deployment 管理 Pod 的生命週期，例如：

* 建立
* 擴展
* 更新
* 自動修復

Service 管理 Pod 的存取方式，例如：

* 固定 DNS
* 負載平衡
* Service Discovery

兩者責任不同，但共同提供高可用服務。

---

# 今日成果

完成 Kubernetes 第一階段核心模型：

```text
Deployment
      │
ReplicaSet
      │
Pods
      ▲
      │
Service
```

理解：

* Deployment 維持 Pod 數量。
* ReplicaSet 建立 Pod。
* Service 提供固定入口與負載平衡。
* Client 永遠連 Service，不直接連 Pod。

---

# 下一步

Week6 Day5：

K3s Foundation

開始建立自己的 Kubernetes 環境，學習：

* K3s Architecture
* kubectl
* kubeconfig
* Node
* Namespace
* 第一個 Deployment 與 Service 實作

並開始將目前的 HPC AI Benchmark Platform 從 Docker Compose 遷移到 Kubernetes。
