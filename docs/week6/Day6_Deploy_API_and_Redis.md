# Week6 Day6 - Deploy API and Redis to Kubernetes

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

