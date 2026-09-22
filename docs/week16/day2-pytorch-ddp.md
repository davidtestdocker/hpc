<!-- readable-curriculum: 2026-09-22 -->
# Week16 Day2 — CPU／Gloo DDP

[上一課](<day1-multi-gpu-fundamentals.md>) · [本週目錄](README.md) · [下一課](<day3-nccl-fundamentals.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史CPU Gloo DDP輸出。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

加總且只印六位小數相同，不足證明所有參數逐元素一致；現行程式沒有跨rank assert。兩程序在同Pod，不是跨node；改成NCCL還需要裝置分配與GPU硬體，不只換backend字串。

## 程式／設定與來源

本次核對：[runtime/pytorch/ddp_test.py](<../../runtime/pytorch/ddp_test.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day2-pytorch-ddp.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
PARAM_CHECKSUM=-0.000516
```

兩rank不同loss相同加總支持同步流程，非完整數值正確性／多GPU效能驗收。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：CPU／Gloo DDP、單 rank NCCL 與新單 L4 訓練是不同證據，未驗證多 GPU／RDMA scaling。
> **閱讀順序**：先學本文基礎，再讀[Week16 現行對照與檢核](../learning-guide.md#week16)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->



## 對應檔案

2026-09-22：單 GPU 的新訓練／CUDA profiling 見 [causal LM 報告](../performance/causal-lm-l4-20260922.md)。
本文保留原 CPU／Gloo DDP 紀錄；新單 GPU 實驗不取代多節點或多 GPU 的驗證。

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/pytorch-runtime/templates/ddp-test-job.yaml](../../helm/pytorch-runtime/templates/ddp-test-job.yaml)
- [helm/pytorch-runtime/values.yaml](../../helm/pytorch-runtime/values.yaml)
- [kustomize/overlays/gpu-sg/kustomization.yaml](../../kustomize/overlays/gpu-sg/kustomization.yaml)
- [runtime/pytorch/ddp_test.py](../../runtime/pytorch/ddp_test.py)：CPU／Gloo DDP 實驗
- [runtime/pytorch/train.py](../../runtime/pytorch/train.py)：GPU 訓練與 profiler

---
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
