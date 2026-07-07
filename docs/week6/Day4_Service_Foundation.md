# Week6 Day4 - Service Foundation

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

