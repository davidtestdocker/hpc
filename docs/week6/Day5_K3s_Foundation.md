# Week6 Day5 - K3s Foundation

## 今日平台增加什麼

今天平台正式新增：

```text
Kubernetes Runtime
```

也就是：

```text
K3s Cluster
```

平台從：

```text
Docker Compose
```

開始演進到：

```text
Kubernetes Cluster
```

---

# Platform Problem

目前平台使用 Docker Compose 管理：

```text
api
redis
postgres
```

Docker Compose 適合單機開發，但缺少：

* Desired State
* Self Healing
* Pod Scheduling
* Service Discovery
* Kubernetes Resource Model

因此需要建立 Kubernetes 環境，讓後續可以使用：

* Pod
* Deployment
* Service
* ConfigMap
* Secret
* Volume
* PVC

---

# 今日知識鏈

```text
Linux VM
    ↓
K3s
    ↓
Kubernetes Control Plane
    ↓
Node
    ↓
kubectl
```

---

# Hands-on

## 1. 確認環境乾淨

確認尚未安裝 K3s：

```bash
which k3s
which kubectl
```

如果沒有輸出，代表環境尚未安裝 K3s。

---

## 2. 安裝 K3s

執行：

```bash
curl -sfL https://get.k3s.io | sh -
```

這個安裝流程會：

* 下載 K3s binary
* 建立 systemd service
* 啟動 K3s server
* 建立 kubeconfig
* 提供 kubectl 操作能力

---

## 3. 驗證 K3s Service

檢查：

```bash
systemctl status k3s
```

確認：

```text
active (running)
```

---

## 4. 驗證 Kubernetes Node

執行：

```bash
kubectl get nodes
```

結果：

```text
NAME       STATUS   ROLES           VERSION
hpc-demo   Ready    control-plane   v1.36.2+k3s1
```

代表：

* K3s 安裝成功
* Kubernetes Control Plane 正常
* kubeconfig 正常
* kubectl 可以連線
* Node 已 Ready

---

## 5. 檢查 kube-system 元件

執行：

```bash
kubectl get pods -A
```

確認以下元件正常：

```text
coredns                  Running
local-path-provisioner   Running
metrics-server           Running
traefik                  Running
svclb-traefik            Running
```

---

# K3s 內建元件

## CoreDNS

負責 Kubernetes 內部 DNS。

例如未來 Pod 可以透過：

```text
redis-service
postgres-service
api-service
```

互相存取。

---

## local-path-provisioner

負責提供本機磁碟型 StorageClass。

之後 Redis / PostgreSQL 的 PVC 會用到。

---

## metrics-server

提供 Kubernetes Metrics API。

未來 HPA、資源監控會用到。

---

## Traefik

K3s 預設內建 Ingress Controller。

後面學 Ingress 時會用到。

---

## svclb-traefik

K3s 內建 Service LoadBalancer 機制。

讓 Traefik 能提供外部入口。

---

# 平台架構

```text
Ubuntu VM
    ↓
K3s Server
    ↓
Kubernetes Control Plane
    ↓
Node: hpc-demo
    ↓
kube-system
    ├── CoreDNS
    ├── local-path-provisioner
    ├── metrics-server
    ├── Traefik
    └── svclb-traefik
```

---

# 今日重點

* K3s 是輕量 Kubernetes Distribution。
* K3s 適合單機學習、Lab、Edge 與小型平台。
* `kubectl get nodes` 是確認 Cluster 是否可用的第一步。
* `kubectl get pods -A` 可以查看整個 Cluster 內所有 Namespace 的 Pod。
* `kube-system` 是 Kubernetes 系統元件所在的 Namespace。
* Node `Ready` 代表 Kubernetes 可以開始排程 Pod。

---

# Interview Q&A

## Q1：K3s 和 Kubernetes 是什麼關係？

K3s 是一個輕量化的 Kubernetes Distribution。

它保留 Kubernetes API 與核心功能，但將安裝與運維簡化，適合 Lab、Edge、單機環境與輕量平台。

---

## Q2：為什麼要先確認 `kubectl get nodes`？

因為 Node Ready 代表：

* Kubernetes API Server 可用
* kubeconfig 正確
* kubectl 能連線
* Control Plane 正常
* Node 可接受 Pod Scheduling

如果 Node 不是 Ready，後續 Deployment、Service、PVC 都可能無法正常運作。

---

# 今日成果

成功建立第一個 Kubernetes Cluster：

```text
hpc-demo
    ↓
K3s
    ↓
Ready Node
```

平台正式從：

```text
Docker Compose Platform
```

進入：

```text
Kubernetes Platform
```

---

# 下一步

Week6 Day6：

開始把目前的 HPC AI Benchmark Platform 從 Docker Compose 遷移到 Kubernetes。

內容包括：

* 建立 Namespace
* 建立 API Deployment
* 建立 API Service
* 建立 Redis Deployment / Service
* 建立 PostgreSQL Deployment / Service
* 驗證 FastAPI 在 Kubernetes 中正常啟動

