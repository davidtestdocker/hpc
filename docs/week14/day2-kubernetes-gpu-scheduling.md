<!-- readable-curriculum: 2026-09-22 -->
# Week14 Day2 — GPU scheduling

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day3-gpu-monitoring-architecture.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

GPU request 需要 device plugin 公布資源，taint／toleration 決定允不允許排入，nodeSelector 決定選哪些節點。toleration 不會強制挑 GPU node，更不保證 GPU runtime 成功。

## 在現在的專案中

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

本課對照：[benchmark/k8s/pytorch-gpu-pod.yaml](<../../benchmark/k8s/pytorch-gpu-pod.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
      resources:
        # 容器可使用的資源上限；GPU 份額的實際意義取決於裝置外掛設定。
        limits:
          # Request one NVIDIA GPU
          # NVIDIA 裝置外掛提供的 GPU 資源單位；time-slicing 時不等同實體卡數。
          nvidia.com/gpu: 1
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week14/day2-kubernetes-gpu-scheduling.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
