# Week6 Day1 - Kubernetes Foundation

## 今日平台增加什麼

今天沒有安裝 Kubernetes。

今天建立的是 Kubernetes 最重要的觀念：

```text
Docker

↓

Kubernetes
```

理解：

> Docker 負責執行 Container。

> Kubernetes 負責管理 Container。

---

# Platform Problem

目前平台：

```text
Docker Compose

├── api
├── redis
└── postgres
```

查看：

```bash
docker ps
```

結果：

```text
api
redis
postgres
```

平台共有：

```text
3 Containers
```

架構：

```text
Docker Host
│
├── api Container
├── redis Container
└── postgres Container
```

---

# Docker 的限制

假設：

```text
api

↓

api × 3
```

變成：

```text
api-1
api-2
api-3
redis
postgres
```

如果：

```text
api-2 Crash
```

Docker 不會：

* 自動建立新 Container
* 維持固定數量
* 自動修復

需要人工：

```bash
docker compose restart api
```

或：

```bash
docker compose up -d
```

---

# Kubernetes 解決什麼？

Kubernetes 不負責建立 Container。

Kubernetes 負責：

```text
Desired State
```

例如：

```text
API

我要 3 個
```

如果：

```text
api-2 Crash
```

Kubernetes：

```text
重新建立新的 Pod
```

自動恢復到：

```text
API = 3
```

這就是：

```text
Self Healing
```

---

# Docker vs Kubernetes

Docker：

```text
Build Image

Run Container
```

Kubernetes：

```text
Scheduling

Scaling

Self Healing

Service Discovery

Container Orchestration
```

兩者不是互相取代，而是合作。

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

Week6 全部內容都圍繞這條知識鏈展開。

---

# 今日重點

Docker：

```text
Container Runtime
```

Kubernetes：

```text
Container Orchestrator
```

Container 是 Docker 的核心。

Pod 是 Kubernetes 的核心。

Kubernetes 管理的是：

```text
Pod
```

不是：

```text
Container
```

---

# 用目前的平台理解

現在：

```text
Docker Compose

api
redis
postgres
```

未來：

```text
api Pod
└── api Container

redis Pod
└── redis Container

postgres Pod
└── postgres Container
```

目前每個 Pod 都只有一個 Container。

因此：

```text
Pod ≠ Container
```

只是目前：

```text
1 Pod = 1 Container
```

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
│     └── api Container
│
├── redis Pod
│     └── redis Container
│
└── postgres Pod
      └── postgres Container
```

---

# Interview Q&A

## Q1：Docker 和 Kubernetes 的差別？

Docker 負責建立與執行 Container。

Kubernetes 負責管理大量 Container，提供自動修復、擴展、排程與服務管理。

---

## Q2：為什麼 Docker Compose 不夠？

Docker Compose 適合單機開發。

當服務需要：

* 自動修復
* 自動擴展
* 高可用
* 多台主機管理

就需要 Kubernetes。

---

# 今日成果

建立 Kubernetes 最重要的基礎觀念：

```text
Docker
    │
    ▼
Container
```

以及：

```text
Kubernetes
    │
    ▼
Pod
```

理解：

* Docker 管理 Container。
* Kubernetes 管理 Pod。
* Kubernetes 透過 Desired State 維持平台運作。

---

# 下一步

Week6 Day2：

Pod Foundation

學習內容：

* Pod 是什麼
* Pod 與 Container 的差別
* Pod Lifecycle
* 第一個 Pod YAML
* 使用 kubectl 建立與查看 Pod

