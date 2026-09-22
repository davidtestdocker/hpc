<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day6 — API 與 Redis 部署依賴

[上一課](<Day5_K3s_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day7_Complete_Platform_on_Kubernetes.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 startup log 摘錄及設定差異。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

目前舊 API YAML 已引用 api-config 與 postgres-secret，僅照本課套 API／Redis 檔案不足；Secret 範例 CHANGE_ME 也不是有效部署憑據。課文寫 ClusterIP，但連結的舊 Service 已是 NodePort；主 overlay 才明確用 ClusterIP。imagePullPolicy: Never 依賴目標節點已有映像，舊 K3s 匯入不能當作 GKE 部署步驟。舊 Redis manifest 沒有 volumeMount／PVC，不能套用 Compose 的持久化結論。主入口為 kustomize/overlays/gpu-sg-platform，不是逐份 apply 舊 k8s 檔。

## 程式／設定與來源

本次核對：[k8s/api-deployment.yaml](<../../k8s/api-deployment.yaml>)、[k8s/api-service.yaml](<../../k8s/api-service.yaml>)、[k8s/redis-deployment.yaml](<../../k8s/redis-deployment.yaml>)、[k8s/redis-service.yaml](<../../k8s/redis-service.yaml>)、[k8s/api-configmap.yaml](<../../k8s/api-configmap.yaml>)、[k8s/postgres-secret.example.yaml](<../../k8s/postgres-secret.example.yaml>)、[kustomize/overlays/gpu-sg-platform/kustomization.yaml](<../../kustomize/overlays/gpu-sg-platform/kustomization.yaml>)、[kustomize/overlays/gpu-sg-platform/api-values.yaml](<../../kustomize/overlays/gpu-sg-platform/api-values.yaml>)、[kustomize/overlays/gpu-sg-platform/redis-values.yaml](<../../kustomize/overlays/gpu-sg-platform/redis-values.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day6_Deploy_API_and_Redis.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Application startup complete
```

舊文保存此 startup 字串，表示曾記錄應用啟動訊息；/health/redis 部分只有成功流程描述，沒有完整 HTTP JSON。不能只靠 startup 字串推成 API→Redis→PostgreSQL 全部可用。

**仍缺的證據／不能證明的事：** 缺當時 image digest、EndpointSlice、HTTP capture；Namespace 也不自動提供網路隔離。此次只核對檔案，不執行匯入、刪 Pod、apply 或 port-forward。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
