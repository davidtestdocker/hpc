# Week16 Day6 — Distributed Training Bottleneck Analysis

## 今日目標

Day5 完成 Distributed Training Scaling 後，發現增加 worker 後 throughput 下降。

Day5 結果：

```text
1 worker:
throughput = 5813.76 samples/s

2 workers:
throughput = 5549.91 samples/s
```

因此 Day6 目標：

使用 PyTorch Profiler 分析 distributed training bottleneck，找出效能下降原因。

分析：

- Compute bottleneck
- Communication bottleneck
- Data loading bottleneck
- Resource contention

---

# 今日新增能力

在 Day5 的 distributed scaling workload：

```text
runtime/pytorch/distributed_scaling.py
```

加入：

```text
PyTorch Profiler
```

原本流程：

```text
torchrun
    ↓
PyTorch DDP
    ↓
Training
    ↓
Throughput measurement
```

加入：

```text
PyTorch Profiler
    ↓
Operation timing analysis
    ↓
Bottleneck identification
```

目的：

從：

> training 變慢

提升到：

> 找出造成 slowdown 的主要原因。

---

# 使用工具

## torchrun

用途：

啟動 distributed training process。

例如：

```bash
torchrun \
  --nproc-per-node=2 \
  distributed_scaling.py
```

建立：

```text
Worker 0
Worker 1
```

---

## PyTorch DistributedDataParallel (DDP)

用途：

讓多個 worker 同步 model gradient。

流程：

```text
Forward

Worker0
Worker1


Backward

Worker0 gradient
       |
       | AllReduce
       |
Worker1 gradient
```

---

## PyTorch Profiler

用途：

分析 training 時間分布。

觀察：

- Model compute
- Communication
- Memory operation
- Data loading

---

# Profiler 設定

目前測試環境：

```text
CPU + Gloo
```

因此使用：

```python
ProfilerActivity.CPU
```

原因：

目前 benchmark 為 CPU distributed training，尚未進入 GPU + NCCL profiling。

---

## 為什麼只讓 rank 0 收集 profiler？

DDP 有多個 process：

```text
Worker0
Worker1
```

如果每個 worker 都收集 profiler：

會產生重複資料。

因此：

```text
rank 0
負責 profiler 收集
```

---

# Benchmark Environment

## 1 Worker Baseline

設定：

```yaml
workers: 1
cpuRequest: "2"
cpuLimit: "2"
```

結果：

```text
backend=gloo
device=cpu
workers=1

samples=400000

duration=68.802s

throughput=5813.76 samples/s
```

---

## 2 Workers

設定：

```yaml
workers: 2
cpuRequest: "2"
cpuLimit: "4"
```

原因：

GKE node 雖然是 4 vCPU，但 Kubernetes Scheduler 使用的是 Allocatable CPU，而不是 Node Capacity。

需要扣除：

- OS
- kube-system workloads
- Kubernetes components

因此：

```yaml
cpuRequest: "4"
```

或：

```yaml
cpuRequest: "3"
```

會造成：

```text
Pending

Insufficient cpu
```

最後使用：

```yaml
cpuRequest: "2"
cpuLimit: "4"
```

成功執行。

結果：

```text
backend=gloo
device=cpu
workers=2

samples=400000

duration=84.156s

throughput=4753.08 samples/s
```

---

# Scaling Analysis

## Speedup

公式：

```text
Speedup
=
2 workers throughput / 1 worker throughput
```

計算：

```text
4753.08 / 5813.76

= 0.818x
```

---

## Scaling Efficiency

公式：

```text
Scaling Efficiency
=
Speedup / Worker Count
```

計算：

```text
0.818 / 2

= 40.9%
```

---

# Profiler Result

Top CPU operations：

```text
aten::addmm        33.78%

aten::mm           33.56%

ProfilerStep       10.74%
```

---

# Bottleneck Analysis

## 1. Compute Bottleneck

主要 operation：

```text
aten::addmm

aten::mm
```

兩者合計：

```text
≈67% CPU time
```

代表大量時間花在：

```text
Matrix Multiplication
```

對應模型：

```python
Linear(1024,4096)

Linear(4096,1)
```

因此：

```text
主要 bottleneck = Model Compute
```

---

## 2. Communication Bottleneck

檢查：

```text
gloo

all_reduce

c10d
```

結果：

沒有出現在主要 CPU operation。

因此：

```text
DDP communication
不是主要 bottleneck
```

---

## 3. Data Loading Bottleneck

Profiler：

```text
enumerate(DataLoader)

Self CPU = 3.06%
```

比例低。

因此：

```text
Data loading
不是主要 bottleneck
```

---

## 4. Resource Contention

目前環境：

```text
Single GKE Node

4 vCPU
```

兩個 worker：

```text
Worker0
Worker1
```

共享：

```text
CPU cores

CPU cache

Memory bandwidth
```

兩個 worker 同時執行：

```text
aten::mm

aten::addmm
```

造成：

```text
Worker 增加
        ↓
CPU contention 增加
        ↓
Throughput 下降
```

---

# 最終結論

本次 negative scaling 原因：

```text
CPU resource contention

+

Single-node limited compute resource
```

不是：

```text
DDP communication bottleneck

Gloo performance problem

DataLoader bottleneck
```

證據：

## Scaling Result

```text
1 worker:

5813.76 samples/s


2 workers:

4753.08 samples/s
```

---

## Profiler Evidence

```text
aten::mm + aten::addmm

≈67% CPU time
```

代表主要時間花在模型計算。

---

# Performance Engineer 分析流程

```text
Benchmark
    ↓
發現 Throughput 下降
    ↓
Profiler Analysis
    ↓
分類 Bottleneck

    ├── Compute
    ├── Communication
    ├── Data Pipeline
    └── Resource Contention
```

---

# 限制

目前測試：

```text
CPU + Gloo

Single Node
```

尚未驗證：

```text
GPU + NCCL

Multi GPU

Multi Node Training
```

未來 GPU environment 才能分析：

```text
NCCL bandwidth

GPU scaling efficiency

Distributed GPU performance
```

---

# Interview Review

## Q1：為什麼增加 DDP worker 後 throughput 可能下降？

因為增加 worker 不只增加 parallel compute，也會增加 synchronization 與 resource contention。如果新增計算收益低於額外成本，就會產生 negative scaling。

## Q2：如何判斷 Distributed Training bottleneck 是 communication 還是 compute？

使用 profiler 分析 operation 時間。如果 `all_reduce / gloo / c10d` 占主要時間，代表 communication bottleneck；如果 `aten::mm / aten::addmm` 占主要時間，代表 compute bottleneck。
