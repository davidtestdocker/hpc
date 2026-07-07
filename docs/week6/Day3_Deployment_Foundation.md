# Week6 Day3 - Deployment Foundation

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

