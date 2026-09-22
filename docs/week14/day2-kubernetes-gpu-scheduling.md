<!-- readable-curriculum: 2026-09-22 -->
# Week14 Day2 — GPU scheduling

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day3-gpu-monitoring-architecture.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：GPU 排程概念，無當日GPU測試。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

device plugin不只登記資源，也參與裝置分配；排程還受CPU、memory、taint與selector限制。Scheduled不等於容器能執行。現行只有一張L4，time-sharing份額不是多張GPU。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<day2-kubernetes-gpu-scheduling.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
<none>
```

<none>反映當日尚無GPU pool，不能算GPU workload成功。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行是一張 L4，time-sharing shares 不是多 GPU；舊 P100 監控結果保留原環境歸屬。
> **閱讀順序**：先學本文基礎，再讀[Week14 現行對照與檢核](../learning-guide.md#week14)及[對應現行入口](../evidence/README.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week14 Day2 - Kubernetes GPU Scheduling

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/k8s/pytorch-gpu-pod.yaml](../../benchmark/k8s/pytorch-gpu-pod.yaml)

---

# 今天平台增加了什麼？

本日建立 Kubernetes GPU Scheduling Foundation。

目的不是立即建立 GPU Node，而是理解 Kubernetes 如何管理 GPU Resource。

本日完成：

- NVIDIA Device Plugin
- Extended Resource
- nvidia.com/gpu
- GPU Scheduling
- GPU Pod YAML
- GPU Pending Analysis
- GPU Scheduling Flow

---

# Key Takeaways

## 1.

NVIDIA Device Plugin

不負責：

- 安裝 Driver
- 安裝 CUDA
- 執行 AI

它唯一的工作：

將 GPU 註冊給 Kubernetes。

形成：

```text
nvidia.com/gpu
```

---

## 2.

CPU、Memory

屬於 Kubernetes 內建 Resource。

GPU

屬於：

Extended Resource。

必須透過：

Device Plugin

註冊。

---

## 3.

Scheduler

永遠依照：

Requests

做排程。

GPU Resource：

因為：

```yaml
limits:
  nvidia.com/gpu: 1
```

Kubernetes

會自動建立：

```yaml
requests:
  nvidia.com/gpu: 1
```

因此：

GPU YAML

通常只需要寫：

```yaml
limits:
  nvidia.com/gpu: 1
```

---

## 4.

GPU Scheduler

只看：

```text
nvidia.com/gpu
```

哪台 Node

具有 GPU Resource，

就排到哪台。

---

## 5.

GPU Pod

不是只有 GPU。

仍然需要：

- CPU
- Memory
- GPU

Scheduler

會同時檢查：

CPU

Memory

GPU

三種 Resource。

任何一項不足，

Pod：

都會：

```text
Pending
```

---

## 6.

GPU Node

可以執行：

- CPU Pod
- GPU Pod

CPU Node

只能執行：

CPU Pod。

Production

通常利用：

- Taint
- Toleration
- NodeSelector
- Affinity

避免一般 Workload 使用 GPU Node。

---

## 7.

GPU Pod

Pending

最常見原因：

```text
Insufficient nvidia.com/gpu
```

第一步排查：

```bash
kubectl describe pod <pod-name>
```

查看：

Events。

---

## 8.

Driver

CUDA

Device Plugin

三者完全不同。

```text
Driver

↓

控制 GPU

CUDA

↓

Application 使用 GPU

Device Plugin

↓

Kubernetes 管理 GPU
```

---

# GPU Scheduling Flow

```text
GPU Pod

↓

Scheduler

↓

檢查：

CPU

↓

Memory

↓

nvidia.com/gpu

↓

全部符合

↓

Running

---------------------

任一不足

↓

Pending
```

---

# GPU Resource

GPU Node：

```text
Capacity

cpu: 4

memory: 16Gi

nvidia.com/gpu: 2
```

GPU Pod：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

結果：

```text
Pod1

↓

GPU1

----------------

Pod2

↓

GPU2

----------------

Pod3

↓

Pending
```

---

# GPU Pod YAML

```yaml
resources:
  requests:
    cpu: "1"
    memory: "2Gi"

  limits:
    cpu: "2"
    memory: "4Gi"
    nvidia.com/gpu: 1
```

GPU

不是取代 CPU。

GPU Pod

仍然需要：

CPU

Memory

GPU。

---

# Pending Analysis

GPU Pod：

```text
Pending
```

第一步：

```bash
kubectl describe pod <pod-name>
```

查看：

```text
Events
```

例如：

```text
Insufficient nvidia.com/gpu
```

代表：

目前沒有符合條件的 GPU Node。

---

# Device Plugin Architecture

```text
GPU Hardware

↓

NVIDIA Driver

↓

NVIDIA Device Plugin

↓

Kubernetes

↓

Node Capacity

↓

nvidia.com/gpu

↓

Scheduler
```

---

# Hands-on

確認目前 Cluster：

沒有 GPU Resource：

```bash
kubectl get nodes \
-o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu
```

結果：

```text
GPU

<none>
```

代表：

目前 Kubernetes

尚未管理任何 GPU。

---

# Platform Engineering Insight

GPU Scheduling

本質不是：

找到 GPU。

而是：

Scheduler

依照 Resource

進行排程。

GPU

只是：

其中一種 Resource。

因此：

CPU

Memory

GPU

都遵守 Kubernetes Scheduler 的排程機制。

---

# Interview Questions

## Q1

Device Plugin 的工作是什麼？

Answer：

將 GPU 註冊為：

```text
nvidia.com/gpu
```

讓 Kubernetes Scheduler 能管理 GPU。

---

## Q2

GPU Pod 為什麼 Pending？

Answer：

最常見原因：

Node 沒有可用：

```text
nvidia.com/gpu
```

第一步：

```bash
kubectl describe pod
```

查看 Events。

---

## Q3

GPU Pod 是否只需要 GPU？

Answer：

不是。

GPU Pod

仍然需要：

- CPU
- Memory
- GPU

Scheduler

同時檢查三種 Resource。

---

## Q4

Driver、CUDA、Device Plugin 有什麼差別？

Answer：

Driver：

控制 GPU。

CUDA：

提供 Application 使用 GPU。

Device Plugin：

提供 Kubernetes 管理 GPU。

---

# Completed

Week14 Day2 完成：

- NVIDIA Device Plugin
- Extended Resource
- nvidia.com/gpu
- GPU Scheduling
- GPU Resource Model
- GPU Pod YAML
- Pending Analysis
- Scheduler Flow
- Driver / CUDA / Device Plugin 關係

---

# Next

Week14 Day3

GPU Monitoring Architecture

- DCGM
- DCGM Exporter
- GPU Metrics
- Prometheus Integration
- Grafana GPU Dashboard Architecture
