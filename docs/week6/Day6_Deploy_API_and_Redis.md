<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day6 — API 與 Redis 部署依賴

[上一課](<Day5_K3s_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day7_Complete_Platform_on_Kubernetes.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

主 overlay 用 Helm chart 加 patch 產生資源；不是依序手動 apply 所有 k8s 檔案。Redis PVC 掛載與 API 環境變數必須一致，bootstrap 也要先備妥 Secret。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[kustomize/overlays/gpu-sg-platform/kustomization.yaml](<../../kustomize/overlays/gpu-sg-platform/kustomization.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
helmCharts:
  - name: api
    releaseName: api
    namespace: hpc-platform-dev
    # 覆寫 Helm values 的設定檔路徑。
    valuesFile: api-values.yaml
    includeCRDs: false

  - name: redis
    releaseName: redis
    namespace: hpc-platform-dev
    valuesFile: redis-values.yaml
    includeCRDs: false

  - name: postgres
    releaseName: postgres
    namespace: hpc-platform-dev
    valuesFile: postgres-values.yaml
    includeCRDs: false

# 對選定資源套用局部修改。
patches:
  - path: system-pool-patch.yaml
    target:
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week6/Day6_Deploy_API_and_Redis.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day6 - Deploy API and Redis to Kubernetes

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

文中的舊稱 `docker-compose.yml`，目前儲存庫檔名為 `compose.yaml`。

- [compose.yaml](../../compose.yaml)：本機服務組合
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/api-service.yaml](../../k8s/api-service.yaml)
- [k8s/redis-deployment.yaml](../../k8s/redis-deployment.yaml)
- [k8s/redis-service.yaml](../../k8s/redis-service.yaml)

---

## 今日平台增加什麼

今天正式開始將 HPC AI Benchmark Platform 從 Docker Compose 遷移到 Kubernetes。

完成：

* Namespace
* API Deployment
* API Service
* Redis Deployment
* Redis Service
* API ↔ Redis 通訊

平台正式開始在 Kubernetes 運行。

---

# Platform Evolution

Docker Compose：

```text
docker-compose.yml

├── api
├── redis
└── postgres
```

演進成：

```text
Kubernetes

Namespace
    │
    ├── api Deployment
    │        │
    │        ▼
    │      api Pod
    │        │
    │        ▼
    │   api-service
    │
    └── redis Deployment
             │
             ▼
         redis Pod
             │
             ▼
       redis-service
```

---

# 今日知識鏈

```text
Cluster
    │
Namespace
    │
Deployment
    │
Pod
    │
Service
```

開始真正將平台部署到 Kubernetes。

---

# Hands-on

## 1. 建立 Namespace

建立：

```bash
kubectl create namespace hpc-platform
```

驗證：

```bash
kubectl get namespaces
```

新增：

```text
hpc-platform
```

---

## 2. 建立 Kubernetes Manifest

建立：

```text
k8s/
```

專門存放所有 Kubernetes YAML。

目前：

```text
k8s/

api-deployment.yaml

api-service.yaml

redis-deployment.yaml

redis-service.yaml
```

---

## 3. API Deployment

建立：

```text
api Deployment
```

內容包含：

* replicas
* selector
* labels
* image
* imagePullPolicy
* containerPort

部署：

```bash
kubectl apply -f k8s/api-deployment.yaml
```

---

## 4. Image 匯入 K3s

K3s 使用：

```text
containerd
```

而不是 Docker Image Store。

因此需要：

```bash
docker save hpc-ai-benchmark-platform-api:latest \
| sudo k3s ctr images import -
```

重新建立 Pod：

```bash
kubectl delete pod -n hpc-platform -l app=api
```

Deployment 自動建立新的 Pod。

---

## 5. API Service

建立：

```text
api-service
```

Service：

```text
ClusterIP
```

提供：

* Stable Endpoint
* Service Discovery

驗證：

```bash
kubectl get svc -n hpc-platform
```

以及：

```bash
kubectl get endpointslices -n hpc-platform
```

確認：

Service 已成功指向 API Pod。

---

## 6. Redis Deployment

建立：

```text
redis Deployment
```

Image：

```text
redis:7-alpine
```

驗證：

```bash
kubectl get pods -n hpc-platform
```

Redis Pod：

```text
Running
```

---

## 7. Redis Service

建立：

```text
redis-service
```

驗證：

```bash
kubectl get svc -n hpc-platform
kubectl get endpointslices -n hpc-platform
```

確認：

Service 成功指向 Redis Pod。

---

## 8. API 環境變數

修改：

```yaml
env:
  - name: REDIS_HOST
    value: redis-service

  - name: REDIS_PORT
    value: "6379"
```

重新：

```bash
kubectl apply
```

Deployment 自動 Rolling Update。

---

## 9. 驗證 API

查看：

```bash
kubectl logs -n hpc-platform deployment/api
```

確認：

```text
Application startup complete
```

代表：

API Pod 正常運作。

---

## 10. 驗證 API ↔ Redis

使用：

```bash
kubectl port-forward \
-n hpc-platform \
svc/api-service 8000:8000
```

另一個 Terminal：

```bash
curl http://localhost:8000/health/redis
```

成功：

```text
API

↓

redis-service

↓

Redis Pod
```

完成 Kubernetes Service Discovery。

---

# 平台架構

```text
Namespace: hpc-platform
│
├── api Deployment
│      │
│      ▼
│   ReplicaSet
│      │
│      ▼
│    api Pod
│      │
│      ▼
│  api-service
│
└── redis Deployment
       │
       ▼
    ReplicaSet
       │
       ▼
    redis Pod
       │
       ▼
  redis-service
```

---

# 今日重點

* Namespace 用來隔離平台資源。
* Deployment 負責維持 Pod。
* Service 提供固定入口。
* K3s 使用 containerd，不直接使用 Docker Image Store。
* `imagePullPolicy: Never` 代表使用本機 containerd Image。
* `kubectl logs` 是 Kubernetes 最重要的除錯工具。
* `kubectl port-forward` 可以將 ClusterIP Service 暫時映射到本機。
* Pod 之間透過 Service Name（DNS）互相通訊，而不是 Pod IP。

---

# Interview Q&A

## Q1：為什麼 K3s 找不到 Docker Image？

K3s 預設使用 containerd 作為 Container Runtime。

Docker Engine 的 Image Store 與 containerd 的 Image Store 是不同的，因此需要匯入 Image，或使用 Image Registry 讓 K3s 拉取。

---

## Q2：為什麼 API 要連 `redis-service`，而不是 Redis Pod IP？

Pod IP 屬於短生命週期資源，Pod 重建後可能改變。

Service 提供固定 DNS 與負載平衡，因此應透過 Service Name 存取。

---

# 今日成果

成功將平台第一階段遷移到 Kubernetes：

```text
FastAPI
     │
api Deployment
     │
api Pod
     │
api-service
     │
redis-service
     │
redis Pod
```

完成：

* Kubernetes Deployment
* Kubernetes Service
* Service Discovery
* API ↔ Redis Connectivity

平台正式開始在 Kubernetes 上運作。

---

# 下一步

Week6 Day7：

完成整個 HPC AI Benchmark Platform 的 Kubernetes 化。

內容包括：

* PostgreSQL Deployment
* PostgreSQL Service
* Persistent Volume
* Persistent Volume Claim
* API ↔ Redis ↔ PostgreSQL 三層整合
* 完整平台驗證與 Kubernetes Debug Workflow
