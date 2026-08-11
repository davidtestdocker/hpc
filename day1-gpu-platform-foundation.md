# Week14 Day1 - GPU Platform Foundation

# 今天平台增加了什麼？

本日建立 GPU Platform Foundation。

目的不是立即使用 GPU，而是建立 Kubernetes GPU Platform 的核心觀念。

本日完成：

- CPU vs GPU
- GPU Hardware
- CUDA
- NVIDIA Driver
- NVIDIA Device Plugin
- GPU Scheduling Concept
- VRAM
- GPU Platform Architecture

---

# Key Takeaways

## 1.

GPU 是 Node 的硬體資源。

Pod 不會擁有 GPU。

Pod 只能向 Kubernetes 申請 GPU。

---

## 2.

GPU 不是 Kubernetes 內建 Resource。

GPU 必須透過：

NVIDIA Device Plugin

註冊成：

```text
nvidia.com/gpu
```

Scheduler 才能管理 GPU。

---

## 3.

Application

不會直接控制 GPU。

完整架構：

```text
Application

↓

CUDA Runtime

↓

NVIDIA Driver

↓

GPU Hardware
```

---

## 4.

GPU Scheduler

根據：

```text
nvidia.com/gpu
```

分配 GPU。

如果沒有 GPU Resource：

Pod 會維持：

```text
Pending
```

---

## 5.

CPU

可以切成：

```text
500m

1000m
```

GPU

預設：

以整張 GPU 分配。

---

## 6.

GPU 快：

不是因為時脈比較高。

而是：

GPU 擁有大量 CUDA Core。

能同時執行大量平行運算。

因此：

AI Training

Inference

Matrix Multiplication

速度遠高於 CPU。

---

## 7.

GPU

有自己的記憶體：

```text
VRAM
```

CPU：

使用：

```text
RAM
```

AI Model：

必須先載入 VRAM。

GPU

才能開始運算。

---

## 8.

GPU Platform

不是只有 CUDA。

而是：

```text
GPU

↓

Kubernetes

↓

Device Plugin

↓

Monitoring

↓

Benchmark

↓

Performance Analysis
```

---

# CPU vs GPU

CPU

適合：

- Logic
- API
- Database
- Operating System
- Scheduler

GPU

適合：

- AI
- Machine Learning
- Matrix Multiplication
- Parallel Computing

---

# Kubernetes GPU Architecture

```text
                    Kubernetes

                         │

                  Scheduler

                         │

          nvidia.com/gpu Resource

                         ▲

                         │

            NVIDIA Device Plugin

                         │

                  NVIDIA Driver

                         │

                    GPU Hardware
```

---

# CPU Node vs GPU Node

目前平台：

```text
Primary Pool

CPU

Memory
```

```text
Observability Pool

CPU

Memory
```

GPU Node：

未建立。

建立後：

Node Capacity

將新增：

```text
nvidia.com/gpu
```

---

# GPU Scheduling

GPU Pod：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

Scheduler：

會尋找：

具有：

```text
nvidia.com/gpu
```

的 Node。

若沒有：

GPU Resource：

Pod：

保持：

```text
Pending
```

---

# CUDA

CUDA

不是 GPU。

CUDA

提供：

Application

使用 GPU

的能力。

Application：

不直接控制 GPU。

而是：

```text
Application

↓

CUDA Runtime

↓

NVIDIA Driver

↓

GPU
```

---

# VRAM

GPU：

擁有：

自己的 Memory。

```text
CPU

↓

RAM
```

```text
GPU

↓

VRAM
```

AI Model：

必須先載入 VRAM。

GPU

才能開始運算。

---

# Hands-on

驗證目前 GKE Node：

```bash
kubectl get nodes
```

查看 Node Capacity：

```bash
kubectl describe node <node-name>
```

確認：

目前：

沒有：

```text
nvidia.com/gpu
```

因此：

目前平台：

仍為：

CPU Platform。

---

# Platform Engineering Insight

GPU Platform

並不是：

增加 GPU 即可。

完整流程：

```text
GPU Hardware

↓

Driver

↓

Device Plugin

↓

Kubernetes Resource

↓

GPU Scheduling

↓

GPU Workload

↓

Monitoring

↓

Performance Analysis
```

Platform Engineer

需要管理的是：

整個 GPU Platform。

而非單純執行 CUDA 程式。

---

# Interview Questions

## Q1

GPU 為什麼需要 Device Plugin？

Answer：

GPU

不是 Kubernetes 內建 Resource。

Device Plugin

負責將 GPU 註冊成：

```text
nvidia.com/gpu
```

Scheduler

才能管理 GPU。

---

## Q2

GPU 為什麼比 CPU 更適合 AI？

Answer：

GPU

具有大量 CUDA Core。

能同時執行大量平行運算。

AI 大量使用矩陣運算。

因此 GPU 遠比 CPU 更有效率。

---

## Q3

GPU 在 Pod 裡嗎？

Answer：

不是。

GPU

屬於 Node。

Pod

只是向 Kubernetes 申請使用 GPU。

---

# Completed

Week14 Day1 完成：

- GPU Platform Foundation
- CPU vs GPU
- CUDA
- NVIDIA Driver
- NVIDIA Device Plugin
- GPU Scheduling Concept
- VRAM
- Kubernetes GPU Architecture

---

# Next

Week14 Day2

Kubernetes GPU Scheduling

- NVIDIA Device Plugin
- nvidia.com/gpu
- GPU Pod YAML
- Pending Analysis
- GPU Resource Scheduling
