<!-- readable-curriculum: 2026-09-22 -->
# Week16 Day2 — CPU／Gloo DDP

[上一課](<day1-multi-gpu-fundamentals.md>) · [本週目錄](README.md) · [下一課](<day3-nccl-fundamentals.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

torchrun 提供 rank 等環境變數，init_process_group 建立群組，DistributedSampler 分資料。DDP 同步梯度不會替你自動正確切資料或定義公平比較。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[runtime/pytorch/ddp_test.py](<../../runtime/pytorch/ddp_test.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    dist.init_process_group(backend="gloo")

    # torchrun automatically provides these distributed environment values.
    # rank 是全群組程序編號，world_size 是程序總數，local_rank 是本節點內編號。
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    local_rank = int(os.environ["LOCAL_RANK"])

    # Create a simple model.
    # Each DDP worker owns its own model replica.
    # 線性層把輸入特徵轉為指定輸出維度，包含可訓練權重與偏差。
    model = torch.nn.Linear(4, 1)

    # Wrap the model with DistributedDataParallel.
    # DDP automatically synchronizes gradients during backward().
    # DDP 包装本機模型副本，初始化時同步參數，backward 時同步梯度。
    model = DDP(model)

    # Create local input data for this worker.
    # Different workers may process different data,
    # so their local loss values do not need to be identical.
    # randn 產生標準常態隨機張量；此處每個 worker 各自產生 8 筆、每筆 4 個特徵。
    x = torch.randn(8, 4)
    y = torch.randn(8, 1)
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week16/day2-pytorch-ddp.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
