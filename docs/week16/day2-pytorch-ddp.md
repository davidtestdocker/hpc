
# Week16 Day2 — PyTorch DDP

## 1. Day Goal

Day2 目標：

```text
理解並實際操作 PyTorch DDP
```

目前只有 1 張 GPU，因此本日使用：

```text
CPU
+
2 Worker Processes
+
Gloo
+
torchrun
```

驗證 Distributed Training Control Flow。

---

# 2. Platform Capability Added

Week15：

```text
Single-process PyTorch Training
```

Week16 Day2：

```text
Kubernetes Job
↓
torchrun
↓
2 Worker Processes
↓
PyTorch DDP
↓
Gloo Communication Backend
```

目前屬於：

```text
Real DDP Validation
```

但不是：

```text
Real Multi-GPU Validation
```

---

# 3. Core Tools

## torchrun

PyTorch 官方 Distributed Launcher。

本次：

```bash
torchrun \
  --standalone \
  --nproc-per-node=2 \
  /runtime/ddp_test.py
```

重要參數：

```text
--standalone
=
自動建立單機 Rendezvous

--nproc-per-node=2
=
在同一個 Node 啟動 2 個 Worker Processes
```

結果：

```text
RANK=0
RANK=1
WORLD_SIZE=2
```

---

## PyTorch DDP

DDP：

```text
DistributedDataParallel
```

作用：

```text
每個 Worker 維護一份相同 Model
↓
各自執行 Forward / Backward
↓
同步 Gradient
↓
各自執行 Optimizer Step
↓
Model Replicas 保持一致
```

程式核心：

```python
model = torch.nn.Linear(4, 1)
model = DDP(model)
```

---

## Gloo

本次 Communication Backend：

```python
dist.init_process_group(
    backend="gloo"
)
```

Gloo 用於：

```text
Process-to-Process Distributed Communication
```

本次因為：

```text
Device = CPU
```

所以使用：

```text
Gloo
```

未來真正 Multi-GPU DDP：

```text
GPU
↓
NCCL
```

---

# 4. Runtime Architecture

本次實際架構：

```text
GKE hpc-gpu-sg
        │
        ▼
     GPU Node
     4 vCPU
        │
        ▼
Kubernetes Job
pytorch-ddp-cpu-test
        │
        ▼
     torchrun
        │
   ┌────┴────┐
   │         │
Worker 0   Worker 1
RANK=0     RANK=1
   │         │
   └────┬────┘
        │
      Gloo
        │
        ▼
   PyTorch DDP
```

注意：

```text
Job 沒有 request nvidia.com/gpu
```

因此本次 Worker 實際使用：

```text
CPU
```

L4 沒有參與 DDP Compute。

---

# 5. GitOps Integration

沿用既有平台：

```text
Git
↓
ArgoCD
↓
Kustomize
↓
Helm
↓
Kubernetes
```

PyTorch Runtime Code：

```text
runtime/pytorch/ddp_test.py
↓
Kustomize configMapGenerator
↓
pytorch-runtime-code
↓
mount /runtime
```

`gpu-sg` overlay：

```yaml
configMapGenerator:
  - name: pytorch-runtime-code
    files:
      - runtime.py=../../../runtime/pytorch/runtime.py
      - train.py=../../../runtime/pytorch/train.py
      - ddp_test.py=../../../runtime/pytorch/ddp_test.py
```

---

# 6. Kubernetes DDP Job

新增：

```text
helm/pytorch-runtime/templates/ddp-test-job.yaml
```

核心：

```yaml
command:
  - torchrun

args:
  - --standalone
  - --nproc-per-node=2
  - /runtime/ddp_test.py
```

CPU Resources：

```yaml
resources:
  requests:
    cpu: "2"
    memory: "2Gi"

  limits:
    cpu: "3"
    memory: "4Gi"
```

刻意沒有：

```yaml
nvidia.com/gpu
```

因此：

```text
CPU DDP Test
```

而不是 Multi-GPU DDP。

---

# 7. DDP Test Code

核心初始化：

```python
dist.init_process_group(
    backend="gloo"
)
```

取得 Distributed Runtime 資訊：

```python
rank = dist.get_rank()
world_size = dist.get_world_size()
local_rank = int(os.environ["LOCAL_RANK"])
```

使用 DDP：

```python
model = DDP(model)
```

Training：

```text
Forward
↓
Loss
↓
Backward
↓
DDP Gradient Synchronization
↓
Optimizer Step
```

---

# 8. Verification Result

實際輸出：

```text
RANK=1
LOCAL_RANK=1
WORLD_SIZE=2
LOSS=1.048156
PARAM_CHECKSUM=-0.000516
```

```text
RANK=0
LOCAL_RANK=0
WORLD_SIZE=2
LOSS=1.645859
PARAM_CHECKSUM=-0.000516
```

確認：

```text
2 Workers
✓

WORLD_SIZE=2
✓

RANK=0 / RANK=1
✓

PyTorch DDP
✓

Gloo
✓
```

---

# 9. PARAM_CHECKSUM

`PARAM_CHECKSUM` 是本 Lab 自訂的驗證值。

產生方式：

```python
param_checksum = sum(
    parameter.sum().item()
    for parameter in model.parameters()
)
```

用途：

```text
把所有 Model Parameters 加總
↓
產生簡單 Checksum
```

流程：

```text
Backward
↓
DDP 同步 Gradients
↓
Optimizer Step
↓
Model Parameters 更新
↓
計算 PARAM_CHECKSUM
```

本次結果：

```text
Rank 0
PARAM_CHECKSUM=-0.000516

Rank 1
PARAM_CHECKSUM=-0.000516
```

因此可以確認：

```text
Model Replicas
維持一致
```

注意：

```text
PARAM_CHECKSUM
不是 PyTorch 官方 Metric
```

也不是：

```text
AllReduce Payload
```

它只是：

```text
Lab Validation Metric
```

真正同步的是：

```text
Gradient
```

---

# 10. Troubleshooting

本日遇到：

```text
kubectl logs
→ No agent available
```

原因：

```text
konnectivity-agent
Pending
```

進一步發現：

```text
GPU Node
具有 taint：

nvidia.com/gpu=present:NoSchedule
```

而：

```text
konnectivity-agent
沒有對應 toleration
```

因此無法排程。

Lab 暫時移除 taint：

```bash
kubectl taint nodes \
  <GPU_NODE> \
  nvidia.com/gpu:NoSchedule-
```

之後：

```text
konnectivity-agent
Running
```

恢復：

```text
kubectl logs
```

能力。

這屬於：

```text
Lab Workaround
```

GPU Node 正式環境不應長期移除 GPU taint。

---

# 11. Current Limitation

目前：

```text
Real CPU DDP
✓
```

尚未完成：

```text
Real Multi-GPU DDP
Real NCCL Backend
Real GPU-to-GPU Communication
Real Multi-node Scaling
```

原因：

```text
GCP GPU Quota
=
1 GPU
```

未來有至少：

```text
2 GPUs
```

後可將：

```text
Gloo
↓
NCCL
```

並執行真正：

```text
Multi-GPU Distributed Training
```

---

# 12. Quick Review

```text
torchrun
=
PyTorch Distributed Launcher
```

```text
DDP
=
DistributedDataParallel
```

```text
Gloo
=
本次 CPU Distributed Communication Backend
```

```text
NCCL
=
未來 Multi-GPU Communication Backend
```

```text
--nproc-per-node=2
=
啟動 2 個 Worker Processes
```

```text
WORLD_SIZE=2
=
Distributed Job 總共有 2 個 Workers
```

```text
RANK=0 / RANK=1
=
兩個 Worker 的 Global Worker ID
```

核心流程：

```text
torchrun
↓
Workers
↓
Process Group
↓
DDP
↓
Gradient Synchronization
↓
Optimizer Step
```

---

# 13. Day2 Result

Week16 Day2 完成：

```text
PyTorch DDP Control Flow
```

平台新增：

```text
Kubernetes Managed
Multi-process Distributed Training Runtime
```

目前為：

```text
CPU + Gloo
```

未來 GPU Quota 解決後升級：

```text
GPU + NCCL
```

---

# Interview Review

## Q1：torchrun 在 PyTorch DDP 裡負責什麼？

`torchrun` 是 PyTorch 官方 Distributed Launcher，負責啟動多個 Worker Process、提供 RANK / LOCAL_RANK / WORLD_SIZE 等 Distributed Runtime 資訊，並建立 Rendezvous 所需環境。

## Q2：Gloo 和 NCCL 的差別？

Gloo 是 PyTorch Distributed 的 Communication Backend，本次用來驗證 CPU DDP；NCCL 則是 NVIDIA 的 GPU Collective Communication Library，真正 Multi-GPU DDP 通常使用 NCCL。
