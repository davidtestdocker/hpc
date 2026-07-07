# Week6 Day2 - Pod Foundation

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

