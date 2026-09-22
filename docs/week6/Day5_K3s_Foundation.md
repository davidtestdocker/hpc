<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day5 — K3s 與 GKE 邊界

[上一課](<Day4_Service_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day6_Deploy_API_and_Redis.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 K3s 節點輸出摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

which 沒輸出只能說 PATH 找不到，不能證明機器未安裝。原 curl | sh 安裝命令沒有固定版本，不是可重現版本證據，也不用重跑。Node Ready 與一次 kubectl 成功不能證明所有控制面、儲存、網路、應用功能正常；排程還受資源與限制影響。Compose 也有服務名稱解析，原文「缺少 Service Discovery」太絕對。列出的 kube-system 元件是舊案例，不可直接套到 GKE。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<Day5_K3s_Foundation.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
hpc-demo   Ready    control-plane   v1.36.2+k3s1
```

這是舊教材保存的 hpc-demo 節點文字，日期及完整原始 log 未保存。版本字串照原文保留，不等於今天安裝過該版本；目前主專案驗收使用 GKE，不是這台 K3s。

**仍缺的證據／不能證明的事：** 沒有 installer log、完整 nodes JSON、套件選項或系統 Pod 清單；不能用後來 GKE 驗收證明舊 K3s 各元件當時的狀態。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day5 - K3s Foundation

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day6_Deploy_API_and_Redis](Day6_Deploy_API_and_Redis.md)。

---

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
