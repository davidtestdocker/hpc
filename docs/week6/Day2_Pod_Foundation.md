<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day2 — Pod 的範圍

[上一課](<Day1_Kubernetes_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day3_Deployment_Foundation.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：概念課，無 Pod lifecycle 實測。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

Pod phase 有 Pending、Running、Succeeded、Failed、Unknown；Deleted 不是 phase。Running 不保證 Ready 或所有容器健康，原圖也不是必經單一路徑。[官方生命週期](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)。同 Pod 共用網路，但 volume 必須宣告並分別掛載，不是自動共用各容器整個檔案系統；容器可各自重啟，不能把共同生命週期理解成永遠同時啟停。[官方 Pod 說明](https://kubernetes.io/docs/concepts/workloads/pods/)。「Container 永遠在 Pod 內」僅適用 Kubernetes 工作負載語境。

## 程式／設定與來源

本次核對：[k8s/api-deployment.yaml](<../../k8s/api-deployment.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day2_Pod_Foundation.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Succeeded / Failed
```

這是原文生命週期示意，不是 kubectl 輸出。原文沒有保存本課建立的獨立 Pod YAML 或觀測各階段的 log，不能說已做過完整生命週期測試。

**仍缺的證據／不能證明的事：** 沒有三個 Pod 的完整資源快照；api＋log-agent＋otel 是構想，不是現有 API manifest 的容器清單。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day2 - Pod Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)

---

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
