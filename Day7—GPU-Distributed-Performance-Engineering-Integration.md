# Week16 Day7 — GPU Distributed Performance Engineering Integration

## 今日目標

完成 Week16 GPU / Distributed Training Performance Engineering 整合。

Day7 不新增 benchmark，而是整理 Day1～Day6 建立的能力：

- Kubernetes GPU Scheduling
- GPU Workload Deployment
- NCCL Benchmark
- PyTorch Distributed Training
- Scaling Analysis
- PyTorch Profiler Bottleneck Analysis

形成完整 HPC AI Performance Engineering Workflow。

---

# Week16 完整流程

    Kubernetes GPU Platform
            |
            v
    GPU Workload Scheduling
            |
            v
    NCCL Communication Benchmark
            |
            v
    PyTorch Distributed Training
            |
            v
    Scaling Measurement
            |
            v
    Profiler Analysis
            |
            v
    Bottleneck Diagnosis

---

# 已完成能力

## 1. Kubernetes GPU Scheduling

建立 GPU workload deployment。

Kubernetes 透過 NVIDIA Device Plugin 將 GPU 暴露為 Kubernetes Resource。

GPU request：

    resources:
      limits:
        nvidia.com/gpu: 1

Scheduler 根據：

    nvidia.com/gpu

將 Pod 分配到 GPU Node。

架構：

    Pod
     |
     v
    Kubernetes Scheduler
     |
     v
    NVIDIA Device Plugin
     |
     v
    GPU Node
     |
     v
    CUDA Runtime

---

# 2. NCCL Benchmark

使用：

    NVIDIA nccl-tests

測試：

    AllReduce

目的：

驗證 GPU Communication 能力。

Multi GPU 架構：

    GPU0
      |
      | NCCL Communication
      |
    GPU1

觀察：

- Latency
- Algorithm Bandwidth
- Bus Bandwidth

---

# 單 GPU NCCL 限制

測試：

    GPU count = 1

結果：

    bus bandwidth = 0

原因：

AllReduce 主要用於：

    GPU-to-GPU synchronization

單 GPU：

    GPU0
      |
     GPU0

沒有實際 GPU communication。

因此單 GPU NCCL：

可以驗證：

- NCCL runtime 是否正常
- CUDA environment 是否正常

不能驗證：

- GPU interconnect bandwidth
- Multi GPU scaling performance

---

# 3. Distributed Training Scaling

使用：

    PyTorch DistributedDataParallel
    torchrun

流程：

    torchrun

        |
        |

    Worker0
    Worker1

        |
        |

    Forward

        |
        |

    Backward

        |
        |

    Gradient Synchronization

---

# Scaling Experiment

## 1 Worker Baseline

結果：

    backend=gloo
    device=cpu
    workers=1

    samples=400000

    duration=68.802s

    throughput=5813.76 samples/s


---

## 2 Workers

結果：

    backend=gloo
    device=cpu
    workers=2

    samples=400000

    duration=84.156s

    throughput=4753.08 samples/s

---

# Scaling Analysis

## Speedup

公式：

    Speedup =
    N worker throughput /
    1 worker throughput


計算：

    4753.08 / 5813.76

    = 0.818x


---

## Scaling Efficiency

公式：

    Efficiency =
    Speedup / Worker Count


計算：

    0.818 / 2

    = 40.9%

---

# Negative Scaling Analysis

結果：

    Worker 增加

    Throughput 下降


代表：

    Negative Scaling

---

# 4. Profiler Bottleneck Analysis

使用：

    PyTorch Profiler


分析：

    Training execution time


分類：

    Compute

    Communication

    Data Loading

    Resource Contention

---

# Profiler Result

主要 CPU Operation：

    aten::addmm        33.78%

    aten::mm           33.56%

    ProfilerStep       10.74%

---

# Bottleneck Diagnosis

## Compute Bottleneck

主要：

    aten::mm

    aten::addmm


兩者合計：

    約 67% CPU Time


代表主要時間花在：

    Matrix Multiplication


也就是：

    Model Compute


---

## Communication Bottleneck

檢查：

    gloo

    all_reduce

    c10d


結果：

沒有占主要 CPU Time。

判斷：

    DDP Communication
    不是主要 bottleneck


---

## Data Loading Bottleneck

Profiler：

    DataLoader

    Self CPU 約 3%


判斷：

    Data Pipeline
    不是主要 bottleneck


---

## Resource Contention

目前環境：

    Single GKE Node

    4 vCPU


兩個 worker：

    Worker0

    Worker1


共享：

    CPU cores

    CPU cache

    Memory bandwidth


造成：

    Worker 增加

          |

          v

    CPU contention 增加

          |

          v

    Compute efficiency 下降

          |

          v

    Throughput decrease

---

# Performance Engineering Workflow

    Benchmark
        |
        v
    Measure Throughput
        |
        v
    Scale Workers
        |
        v
    Calculate Speedup / Efficiency
        |
        v
    Detect Performance Issue
        |
        v
    Profiler Analysis
        |
        v
    Identify Bottleneck
        |
        v
    Optimization Decision

---

# Optimization Direction

## 短期

增加 CPU Resource：

    更多 vCPU

降低：

    CPU contention


---

## 中期

Multi-node Distributed Training：

    Node A

    Worker0


    Node B

    Worker1


驗證：

    Distributed Scaling


---

## GPU Environment

從：

    CPU + Gloo


提升到：

    GPU + NCCL


分析：

- GPU utilization
- NCCL bandwidth
- GPU scaling efficiency

---

# Week16 Final Summary

完成：

- Kubernetes GPU Scheduling
- NVIDIA GPU Workload Deployment
- NCCL AllReduce Benchmark
- PyTorch Distributed Training
- Worker Scaling Experiment
- Speedup Calculation
- Scaling Efficiency
- PyTorch Profiler Analysis
- Bottleneck Diagnosis

---

# Limitations

目前：

    CPU + Gloo

    Single Node


尚未驗證：

    Multi GPU NCCL Scaling

    Multi Node Training

    GPU Communication Optimization


需要：

    2+ GPU Environment


才能分析：

- NCCL Bandwidth
- GPU Communication Efficiency
- Distributed GPU Scaling

---

# Interview Review

## Q1：Distributed Training scaling 不佳時，你如何定位問題？

先建立 baseline，再增加 worker 計算 speedup 與 efficiency。如果 scaling 不符合預期，使用 profiler 分析 compute、communication、data pipeline 與 resource contention，找出主要 bottleneck。

## Q2：為什麼單 GPU NCCL benchmark 不能代表 GPU communication performance？

因為 NCCL 的核心用途是 GPU-to-GPU communication。單 GPU 沒有 GPU interconnect communication，因此只能驗證 NCCL runtime，不代表 Multi GPU bandwidth 或 scaling performance。
