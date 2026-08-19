# Week16 Day5 — Distributed Training Scaling

## 今日成果

建立正式 distributed scaling workload：

```text
runtime/pytorch/distributed_scaling.py
```

整合進既有：

```text
Helm
→ Kustomize
→ ArgoCD
→ Kubernetes Job
→ torchrun
→ PyTorch DDP
→ Gloo
```

目標：

```text
比較 1 worker 與 2 workers 的 Training Throughput
→ 計算 Speedup
→ 計算 Scaling Efficiency
```

---

## Scaling 指標

### Speedup

```text
Speedup
= N-worker Throughput / 1-worker Throughput
```

### Scaling Efficiency

```text
Scaling Efficiency
= Speedup / Worker 數
```

---

## Benchmark Workload

使用：

```text
PyTorch
torchrun
DistributedDataParallel
DistributedSampler
Gloo
```

目前因 GPU quota 只有 1 張 L4，因此本日採：

```text
CPU + Gloo
```

做真實 distributed scaling 驗證。

Worker 數由 Helm 控制：

```yaml
distributedScaling:
  workers: 1
```

實際啟動：

```bash
torchrun \
  --standalone \
  --nproc-per-node=1 \
  /runtime/distributed_scaling.py
```

2 workers：

```yaml
distributedScaling:
  workers: 2
```

等同：

```bash
torchrun \
  --standalone \
  --nproc-per-node=2 \
  /runtime/distributed_scaling.py
```

---

## Kubernetes Resource 設定

### 1 Worker

```yaml
workers: 1
cpuRequest: "2"
cpuLimit: "2"
```

### 2 Workers

最初設定：

```yaml
cpuRequest: "4"
cpuLimit: "4"
```

因 GKE node 雖為 4 vCPU，但 Kubernetes 可排程資源需扣除 system workload，Pod 發生：

```text
Insufficient cpu
```

最後調整為：

```yaml
workers: 2
cpuRequest: "2"
cpuLimit: "4"
```

重要觀念：

```text
CPU Capacity
≠
Kubernetes 可直接全部 Request 的 CPU

request
→ Scheduler 必須保證的資源

limit
→ Container 最多能使用的資源
```

---

## 真實 Benchmark 結果

### 1 Worker

```text
backend=gloo
device=cpu
workers=1
samples=400000
duration=68.802s
throughput=5813.76 samples/s
```

### 2 Workers

```text
backend=gloo
device=cpu
workers=2
samples=400000
duration=72.073s
throughput=5549.91 samples/s
```

---

## Scaling Analysis

```text
Speedup
= 5549.91 / 5813.76
≈ 0.955x
```

```text
Scaling Efficiency
= 0.955 / 2
≈ 47.7%
```

結果：

```text
1 Worker → 5813.76 samples/s
2 Workers → 5549.91 samples/s

Speedup → 0.955x
Efficiency → 47.7%
```

2 workers throughput 反而下降約：

```text
4.5%
```

屬於：

```text
Negative Scaling
```

---

## 為什麼增加 Worker 反而變慢

目前 2 workers 仍位於同一個 4-vCPU Node：

```text
Worker 0
   ↕
Gloo Gradient Synchronization
   ↕
Worker 1
```

兩個 process 共享：

```text
CPU
Memory Bandwidth
Node Resources
```

同時增加：

```text
Process Coordination
Gradient Synchronization
Communication Overhead
Context Switching
```

當這些 overhead 大於 parallel compute 帶來的收益時：

```text
Worker ↑
但 Throughput ↓
```

因此增加 worker 不代表一定會得到線性效能提升。

`torchrun` 本次也自動設定：

```text
OMP_NUM_THREADS=1
```

避免多 process 過度使用 CPU threads。

---

## 本日結論

```text
Distributed Scaling 必須實測
不能假設 Worker 越多一定越快
```

目前實測：

```text
CPU / Gloo
1 → 2 Workers
Speedup = 0.955x
Scaling Efficiency = 47.7%
```

這組結果將直接作為 Day6 Communication Bottleneck Analysis 的分析案例。

GPU/NCCL scaling 尚未實測，需等待至少 2 張 GPU。

---

## Quick Review

```text
Throughput
→ 每秒處理多少 Samples

Speedup
→ N Workers 相對 1 Worker 快幾倍

Scaling Efficiency
→ 實際 Speedup 距離理想線性 Scaling 多近

Negative Scaling
→ 增加 Worker 後反而變慢
```

---

## Interview Review

### Q1：為什麼增加 DDP Worker 不一定會提升 Throughput？

因為 Worker 增加後也會增加 gradient synchronization、process coordination 與 resource contention；若 communication overhead 大於 parallel compute 收益，就會出現 negative scaling。

### Q2：本次 1→2 Workers 的 Scaling 結果如何？

Throughput 從 5813.76 降至 5549.91 samples/s，Speedup 約 0.955x，Scaling Efficiency 約 47.7%，屬於 negative scaling。
