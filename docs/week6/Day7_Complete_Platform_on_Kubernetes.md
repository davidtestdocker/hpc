# Week6 Day7 - Complete Platform on Kubernetes

## 今日平台增加什麼

今天完成 HPC AI Benchmark Platform 的 Kubernetes 化。

平台從：

```text
Docker Compose
```

正式演進成：

```text
Kubernetes Platform
```

完成：

* PostgreSQL StatefulSet
* Persistent Volume Claim (PVC)
* PostgreSQL Service
* API ↔ Redis ↔ PostgreSQL 整合
* Rolling Update
* Platform Verification

---

# Platform Architecture

完成後平台架構：

```text
                     api-service
                          │
                    api Deployment
                          │
                      ReplicaSet
                          │
                          ▼
                      api Pod
                    /           \
                   ▼             ▼
          redis-service    postgres-service
                 │                  │
          redis Deployment    postgres StatefulSet
                 │                  │
             redis Pod         postgres-0
                                    │
                                    ▼
                             PersistentVolumeClaim
                                    │
                                    ▼
                             PersistentVolume
```

---

# 今日知識鏈

```text
StorageClass
      │
      ▼
PersistentVolumeClaim
      │
      ▼
PersistentVolume
      │
      ▼
StatefulSet
      │
      ▼
PostgreSQL
```

完成 Kubernetes Storage 與 Stateful Workload。

---

# Hands-on

## 1. 查看 StorageClass

執行：

```bash
kubectl get storageclass
```

結果：

```text
local-path (default)
```

Storage Provisioner：

```text
rancher.io/local-path
```

提供 Dynamic Provisioning。

---

## 2. 建立 PersistentVolumeClaim

建立：

```text
k8s/postgres-pvc.yaml
```

申請：

```text
1Gi
```

Storage。

第一次查看：

```bash
kubectl get pvc -n hpc-platform
```

狀態：

```text
Pending
```

原因：

StorageClass：

```text
WaitForFirstConsumer
```

等待 Pod 使用。

---

## 3. 建立 PostgreSQL StatefulSet

建立：

```text
k8s/postgres-statefulset.yaml
```

使用：

* postgres:16-alpine
* StatefulSet
* PVC
* volumeMount

資料掛載：

```text
/var/lib/postgresql/data
```

對應 Docker Compose：

```text
postgres_data:/var/lib/postgresql/data
```

---

## 4. PVC 自動 Bound

當 StatefulSet 建立 Pod：

```text
postgres-0
```

PVC：

由：

```text
Pending
```

變成：

```text
Bound
```

代表：

Dynamic Provisioning 成功。

---

## 5. 建立 PostgreSQL Service

建立：

```text
postgres-service
```

提供：

```text
ClusterIP
```

Service Discovery。

驗證：

```bash
kubectl get svc -n hpc-platform
kubectl get endpointslices -n hpc-platform
```

確認：

Service 已成功指向：

```text
postgres-0
```

---

## 6. 修改 API Database Connection

原本：

```text
postgres
```

修改：

```text
postgres-service
```

Kubernetes 內部：

透過 Service Name：

完成：

```text
DNS Service Discovery
```

---

## 7. Rolling Update

重新：

* Build Docker Image
* 匯入 K3s containerd
* Restart Deployment

執行：

```bash
kubectl rollout restart deployment api -n hpc-platform
```

驗證：

```bash
kubectl rollout status deployment api -n hpc-platform
```

結果：

```text
successfully rolled out
```

Deployment：

完成：

```text
Rolling Update
```

---

## 8. 驗證平台

API：

```bash
kubectl logs -n hpc-platform deployment/api
```

確認：

```text
Application startup complete
```

Redis：

```bash
curl http://localhost:8000/health/redis
```

成功：

```text
healthy
```

PostgreSQL：

第一次：

```sql
\dt
```

結果：

```text
Did not find any relations.
```

原因：

Kubernetes PostgreSQL 使用新的 Persistent Volume。

建立：

```sql
jobs
```

Table。

再次測試：

```bash
POST /benchmark
```

成功寫入：

* Redis
* PostgreSQL

---

# Platform Evolution

Week5：

```text
Docker Compose

api

redis

postgres
```

Week6：

```text
Kubernetes

Namespace

Deployment

Service

StatefulSet

PersistentVolumeClaim

PersistentVolume
```

平台正式遷移完成。

---

# 今日重點

## Deployment

適合：

* Stateless Application
* FastAPI
* Web API
* Backend

---

## StatefulSet

適合：

* PostgreSQL
* MySQL
* Redis Cluster
* Kafka
* MongoDB

提供：

* Stable Identity
* Stable Storage

---

## PVC

PVC：

不是 Storage。

PVC 是：

```text
Storage Request
```

真正 Storage：

來自：

```text
Persistent Volume
```

---

## Dynamic Provisioning

流程：

```text
PVC

↓

StorageClass

↓

Provisioner

↓

PV

↓

Pod
```

不用手動建立 PV。

---

# Interview Q&A

## Q1：Deployment 和 StatefulSet 有什麼差別？

Deployment 適合 Stateless Application，例如 API。

StatefulSet 適合 Stateful Application，例如 PostgreSQL。

StatefulSet 提供固定 Pod 名稱、固定 Storage 與穩定身分識別。

---

## Q2：為什麼 PVC 一開始是 Pending？

因為 K3s 預設 StorageClass 使用：

```text
WaitForFirstConsumer
```

PVC 會等 Pod 真正需要 Volume 時，才建立並綁定 Persistent Volume。

---

## Q3：為什麼 Kubernetes 的 PostgreSQL 沒有 jobs Table？

因為 Kubernetes 使用新的 Persistent Volume。

資料與 Docker Compose 的 Volume 完全獨立，因此需要重新建立 Schema 或透過 Migration 工具初始化資料庫。

---

# 今日成果

成功完成 HPC AI Benchmark Platform Kubernetes 化。

平台已包含：

* Namespace
* Deployment
* ReplicaSet
* Pod
* Service
* StatefulSet
* Persistent Volume Claim
* Persistent Volume
* Rolling Update
* Service Discovery
* API ↔ Redis ↔ PostgreSQL 整合

整個平台已可在 K3s Cluster 上正常運作。

---

# Week6 完成成果

完成 Kubernetes Foundation：

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
      │
      ▼
PersistentVolumeClaim
      │
      ▼
PersistentVolume
      │
      ▼
StatefulSet
```

並成功將 HPC AI Benchmark Platform 從 Docker Compose 遷移至 Kubernetes。

---

# 下一步

**Week7：Kubernetes Advanced**

內容包括：

* ConfigMap
* Secret
* Liveness Probe
* Readiness Probe
* Resource Requests / Limits
* Ingress（Traefik）
* Horizontal Pod Autoscaler（HPA）
* Kubernetes Debug Workflow
* 將平台提升至更接近生產環境的部署方式

