<!-- readable-curriculum: 2026-09-22 -->
# Week16 Day1 — 多 GPU 基本概念與單卡限制

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-pytorch-ddp.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

資料平行每个 rank 通常有自己的模型副本，模型平行把模型拆分；兩者通訊模式不同。time-sharing 不是新裝置，不能把四 shares 當成四個 CUDA device。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[runtime/pytorch/distributed_scaling.py](<../../runtime/pytorch/distributed_scaling.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))

    distributed = world_size > 1

    use_cuda = torch.cuda.is_available()

    if distributed:
        # 條件運算式 A if 條件 else B：GPU 選 NCCL，CPU 選 Gloo。
        backend = "nccl" if use_cuda else "gloo"
        # 初始化分散式通訊群組；torchrun 提供 rank、world size 與 rendezvous 環境。
        dist.init_process_group(backend=backend)

    rank = dist.get_rank() if distributed else 0

    if use_cuda:
        # 把本程序綁到 local_rank 對應的 GPU，避免同節點所有程序使用同一張卡。
        torch.cuda.set_device(local_rank)
        device = torch.device(f"cuda:{local_rank}")
    else:
        device = torch.device("cpu")

    backend = "nccl" if use_cuda else "gloo"

```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week16/day1-multi-gpu-fundamentals.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：CPU／Gloo DDP、單 rank NCCL 與新單 L4 訓練是不同證據，未驗證多 GPU／RDMA scaling。
> **閱讀順序**：先學本文基礎，再讀[Week16 現行對照與檢核](../learning-guide.md#week16)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->



## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

下方 DDP 程式是現有 CPU／Gloo 實驗，供理解 rank 與同步；不代表已驗證多 GPU。

- [helm/pytorch-runtime/templates/ddp-test-job.yaml](../../helm/pytorch-runtime/templates/ddp-test-job.yaml)
- [runtime/pytorch/ddp_test.py](../../runtime/pytorch/ddp_test.py)：CPU／Gloo DDP 實驗

---
# Week16 Day1 — Multi-GPU & Distributed Training Fundamentals

## 1. Day1 Goal

Week15 已完成單 GPU AI Runtime Platform。

Week16 開始進入：

```text
Distributed AI Performance Engineering
```

原規劃使用：

```text
2 Nodes
×
1 GPU / Node
=
2 GPUs
```

目前受到 GCP GPU Quota 限制，因此 Day1 先完成：

```text
Distributed Training Fundamentals
```

目前狀態：

```text
Real Multi-GPU Validation
=
Pending

Distributed Concepts
=
Completed
```

---

# 2. Distributed Training Basic Architecture

理想的 Week16 Multi-node 架構：

```text
Node A                         Node B
│                              │
├── Process / Worker           ├── Process / Worker
│      │                       │      │
│      ▼                       │      ▼
│    GPU 0                     │    GPU 0
│      │                       │      │
│    Rank 0                    │    Rank 1
│                              │
└──────────── Network ─────────┘
```

整個 Distributed Job：

```text
WORLD_SIZE = 2
```

---

# 3. Node / Process / GPU

## Node

```text
Node
=
一台實體或虛擬機器
```

例如：

```text
GKE GPU Node
```

---

## Process / Worker

真正執行 Training Code 的程序。

```text
Process
=
Training Worker
```

Distributed Training 通常：

```text
1 GPU
↔
1 Training Process
```

例如：

```text
Node A
├── Process 0
└── GPU 0

Node B
├── Process 1
└── GPU 0
```

---

# 4. RANK

`RANK` 是：

```text
Distributed Job 中
每個 Worker 的全域唯一 ID
```

例如：

```text
WORLD_SIZE = 2

Rank 0
Rank 1
```

重要：

```text
RANK
≠
GPU ID

RANK
≠
Node ID
```

它代表：

```text
Global Worker ID
```

---

# 5. LOCAL_RANK

`LOCAL_RANK` 是：

```text
Worker 在自己 Node 內的編號
```

例如：

```text
2 Nodes
1 GPU / Node
```

會是：

```text
Node A

RANK       = 0
LOCAL_RANK = 0
GPU        = 0
```

```text
Node B

RANK       = 1
LOCAL_RANK = 0
GPU        = 0
```

因此：

```text
RANK
0
1
```

但：

```text
LOCAL_RANK
0
0
```

因為兩個 Worker 位於不同 Node。

---

# 6. Single-node Multi-GPU Rank Example

如果是：

```text
1 Node
2 GPUs
```

則：

```text
Node A

Process 0
├── RANK = 0
├── LOCAL_RANK = 0
└── GPU 0

Process 1
├── RANK = 1
├── LOCAL_RANK = 1
└── GPU 1
```

此時：

```text
WORLD_SIZE = 2
```

---

# 7. Multi-node Rank Example

假設：

```text
3 Nodes
2 GPUs / Node
```

總 Worker：

```text
3 × 2
=
6
```

因此：

```text
WORLD_SIZE = 6
```

Rank：

```text
Node 1

GPU0
RANK=0
LOCAL_RANK=0

GPU1
RANK=1
LOCAL_RANK=1
```

```text
Node 2

GPU0
RANK=2
LOCAL_RANK=0

GPU1
RANK=3
LOCAL_RANK=1
```

```text
Node 3

GPU0
RANK=4
LOCAL_RANK=0

GPU1
RANK=5
LOCAL_RANK=1
```

---

# 8. WORLD_SIZE

`WORLD_SIZE`：

```text
整個 Distributed Job
Worker / Process 的總數量
```

通常：

```text
WORLD_SIZE
=
Node Count
×
Processes Per Node
```

如果：

```text
4 Nodes
×
2 Processes
```

則：

```text
WORLD_SIZE = 8
```

---

# 9. Rendezvous

Distributed Workers 一開始彼此不知道：

```text
其他 Worker 在哪裡？
總共有幾個 Worker？
誰的 Rank 是多少？
要從哪裡開始建立連線？
```

因此需要：

```text
Rendezvous
```

可以理解成：

```text
Distributed Workers
第一次集合與互相發現的機制
```

初始化流程：

```text
Worker Start
↓
Rendezvous
↓
Workers 找到彼此
↓
建立 Distributed Environment
```

---

# 10. MASTER_ADDR

例如：

```text
Node A
10.10.0.5

Node B
10.10.0.8
```

如果選：

```text
Node A
```

作為 Rendezvous Endpoint：

```text
MASTER_ADDR=10.10.0.5
```

---

# 11. MASTER_PORT

例如：

```text
MASTER_PORT=29500
```

則 Rendezvous Endpoint：

```text
10.10.0.5:29500
```

可以理解成：

```text
MASTER_ADDR
=
Workers 到哪台機器集合

MASTER_PORT
=
從哪個 TCP Port 建立初始化連線
```

重要：

```text
MASTER_ADDR
≠
所有 Training Compute 的主機
```

Rank 1 不會把自己的 Training 工作丟給 Rank 0 計算。

---

# 12. Distributed Compute Model

正確流程：

```text
Rank 0
↓
自己的 Data
↓
自己的 Forward / Backward
```

同時：

```text
Rank 1
↓
自己的 Data
↓
自己的 Forward / Backward
```

也就是：

```text
Each Rank Computes Locally
```

Rank 0 並不是：

```text
Central Compute Server
```

---

# 13. Process Group

Workers Rendezvous 成功後：

```text
建立 Process Group
```

Process Group 可以理解成：

```text
一組可以互相執行
Distributed Communication
的 Workers
```

例如：

```text
Process Group

├── Rank 0
└── Rank 1
```

之後才能執行：

```text
AllReduce
AllGather
Broadcast
Barrier
```

等 Collective Operation。

---

# 14. Communication Backend

PyTorch Process Group 可以使用不同 Backend。

GPU Distributed Training 常見：

```text
NCCL
```

CPU Distributed Training 可以使用：

```text
Gloo
```

概念：

```text
PyTorch Process Group
        │
        ▼
Communication Backend
        │
        ├── NCCL
        │     └── GPU
        │
        └── Gloo
              └── CPU
```

目前沒有第二張 GPU，因此 Week16 後續會先使用：

```text
CPU
+
Multi-process
+
Gloo
```

驗證 Distributed Control Flow。

---

# 15. DDP

DDP：

```text
DistributedDataParallel
```

PyTorch 的 Distributed Data Parallel Training 機制。

核心：

```text
相同 Model
複製到多個 Worker / GPU
↓
每個 Rank 處理不同 Data
↓
各自 Forward
↓
各自 Backward
↓
同步 Gradient
↓
各自更新相同 Model
```

因此：

```text
DDP
=
Data Parallelism
```

---

# 16. DDP vs Model Parallelism

DDP：

```text
GPU0
└── 完整 Model
    └── Data A

GPU1
└── 完整 Model
    └── Data B
```

也就是：

```text
Same Model
Different Data
```

---

Model Parallelism：

```text
GPU0
└── Model Part A

GPU1
└── Model Part B
```

也就是：

```text
One Model
Split Across GPUs
```

Week16 主要學：

```text
DDP
```

---

# 17. DistributedSampler

如果 Dataset：

```text
8 Samples
```

兩個 Rank 不應該各自重複處理全部資料。

而是可以類似：

```text
Rank 0

0
2
4
6
```

```text
Rank 1

1
3
5
7
```

PyTorch 常使用：

```text
DistributedSampler
```

進行 Dataset Sharding。

核心：

```text
Different Rank
↓
Different Data
```

---

# 18. Global Batch Size

假設：

```text
WORLD_SIZE = 2

Per-GPU Batch Size = 32
```

則：

```text
Global Batch Size
=
32 × 2
=
64
```

公式：

```text
Global Batch Size
=
Per-Worker Batch Size
×
WORLD_SIZE
```

例如：

```text
4 GPUs
Batch Size / GPU = 16
```

則：

```text
Global Batch Size = 64
```

---

# 19. Gradient

Gradient 可以簡單理解成：

```text
告訴 Model Parameter：

往哪個方向改
以及改多少

才能讓 Loss 降低
```

Training：

```text
Forward
↓
Loss
↓
Backward
↓
Gradient
↓
Optimizer
↓
Update Parameters
```

---

# 20. Gradient Synchronization

假設：

```text
Rank 0
處理 Data A
↓
Gradient A
```

```text
Rank 1
處理 Data B
↓
Gradient B
```

如果完全不同步：

```text
Rank 0 Model
和
Rank 1 Model

會逐漸變成不同參數
```

因此 DDP 需要：

```text
Gradient Synchronization
```

---

# 21. AllReduce

AllReduce 是 DDP 非常重要的 Collective Operation。

假設：

```text
Rank 0 Gradient = 4
Rank 1 Gradient = 8
```

Reduce：

```text
4 + 8
=
12
```

如果再取平均：

```text
12 / 2
=
6
```

最後：

```text
Rank 0 Gradient = 6
Rank 1 Gradient = 6
```

因此兩邊：

```text
Optimizer Step
```

使用相同 Gradient。

---

# 22. Reduce vs AllReduce

Reduce：

```text
Rank 0 ─┐
        ├── Reduce
Rank 1 ─┘
        ↓
只有指定 Rank 拿到結果
```

AllReduce：

```text
Rank 0 ─┐
        ├── Reduce
Rank 1 ─┘
        ↓
所有 Rank 都拿到結果
```

因此 DDP Gradient Synchronization 常使用：

```text
AllReduce
```

---

# 23. NCCL

NCCL：

```text
NVIDIA Collective Communications Library
```

它是 NVIDIA 提供的：

```text
GPU Collective Communication Library
```

可以負責：

```text
AllReduce
AllGather
ReduceScatter
Broadcast
```

等 GPU Communication。

架構：

```text
PyTorch DDP
↓
NCCL Backend
↓
Collective Communication
↓
GPU ↔ GPU
```

簡單記：

```text
DDP
=
Distributed Training

NCCL
=
GPU Communication
```

---

# 24. Current Hardware Limitation

目前 GCP Quota：

```text
NVIDIA_L4_GPUS
=
1

GPUS_ALL_REGIONS
=
1
```

因此目前無法建立：

```text
2 Nodes
×
1 L4
```

所以：

```text
Real NCCL Multi-GPU Validation
=
Pending
```

目前可以使用：

```text
CPU
+
2 Processes
+
Gloo
```

真的驗證：

```text
RANK
LOCAL_RANK
WORLD_SIZE
Rendezvous
Process Group
DistributedSampler
DDP Control Flow
```

但不能假裝驗證：

```text
GPU ↔ GPU NCCL Bandwidth
Multi-GPU Scaling
Inter-node GPU Communication
```

---

# 25. Speedup

Distributed Training 不只看：

```text
有沒有變快
```

還要量：

```text
Speedup
```

公式：

```text
Speedup
=
Multi-GPU Throughput
/
Single-GPU Throughput
```

例如：

```text
1 GPU
=
100 samples/s

2 GPUs
=
175 samples/s
```

則：

```text
Speedup
=
175 / 100
=
1.75x
```

---

# 26. Scaling Efficiency

公式：

```text
Scaling Efficiency
=
Speedup
/
GPU Count
```

例如：

```text
Speedup = 1.75x
GPU Count = 2
```

則：

```text
Scaling Efficiency
=
1.75 / 2
=
87.5%
```

---

# 27. Scaling Example

假設：

```text
1 GPU
=
120 samples/s

2 GPU
=
204 samples/s
```

則：

```text
Speedup
=
204 / 120
=
1.7x
```

Scaling Efficiency：

```text
1.7 / 2
=
85%
```

---

# 28. Why Multi-GPU Is Not Linear

理想：

```text
1 GPU = 100

2 GPU = 200

4 GPU = 400
```

實際通常：

```text
1 GPU = 100

2 GPU = 175

4 GPU = 320
```

原因是 Distributed Training 增加：

```text
Communication
Synchronization
Runtime Overhead
Data Pipeline Overhead
```

可以簡化：

```text
Total Step Time
=
Compute
+
Communication
+
Synchronization
+
Other Overhead
```

因此：

```text
GPU Count ↑
```

不代表：

```text
Performance
線性 ↑
```

---

# 29. Communication Bottleneck

例如：

```text
GPU Compute
=
100 ms

AllReduce
=
5 ms
```

Communication Cost 很低。

但如果：

```text
GPU Compute
=
100 ms

AllReduce
=
80 ms
```

則 Distributed Scaling 可能受到：

```text
Communication Bottleneck
```

限制。

後續 Week16 會分析：

```text
Compute Time
vs
Communication Time
```

---

# 30. Intra-node Communication

Intra-node：

```text
同一台 Node 裡面的 GPU Communication
```

例如：

```text
Node A

GPU0
↕
GPU1
```

可能經過：

```text
PCIe
NVLink
NVSwitch
```

實際取決於硬體平台。

---

# 31. Inter-node Communication

Inter-node：

```text
不同 Node 之間的 GPU Communication
```

例如：

```text
Node A                  Node B

GPU0                    GPU0
 │                       │
 └────── Network ────────┘
```

Communication Path 可能涉及：

```text
GPU
↓
PCIe / Host Path
↓
NIC
↓
Network
↓
NIC
↓
GPU
```

因此更容易受到：

```text
Network Bandwidth
Latency
NIC
Topology
Synchronization
```

影響。

---

# 32. Single-node vs Multi-node

Single-node：

```text
1 Node
├── GPU0
└── GPU1

主要：
Intra-node Communication
```

Multi-node：

```text
Node A
└── GPU0

     Network

Node B
└── GPU0

主要：
Inter-node Communication
```

---

# 33. Distributed Training Full Flow

完整流程：

```text
Workers Start
↓
Rendezvous
↓
MASTER_ADDR / MASTER_PORT
↓
Process Group
↓
RANK / LOCAL_RANK / WORLD_SIZE
↓
DistributedSampler
↓
Different Data Per Rank
↓
Forward
↓
Backward
↓
Gradient
↓
AllReduce
↓
Gradient Synchronization
↓
Optimizer Step
↓
Model Replicas Stay Consistent
```

---

# 34. Day1 Mental Model

今天最重要的架構：

```text
                 Distributed Job
                       │
             WORLD_SIZE = N
                       │
            ┌──────────┴──────────┐
            │                     │
          Rank 0                Rank 1
            │                     │
        Local Data            Local Data
            │                     │
         Forward               Forward
            │                     │
         Backward              Backward
            │                     │
         Gradient              Gradient
            │                     │
            └─────────┬───────────┘
                      │
                   AllReduce
                      │
                      ▼
             Synchronized Gradient
                      │
             ┌────────┴────────┐
             │                 │
        Optimizer Step    Optimizer Step
             │                 │
             ▼                 ▼
         Same Model         Same Model
```

---

# 35. Quick Review

快速複習只看這段：

```text
Node
=
一台機器

Process / Worker
=
Training 程序

RANK
=
全域 Worker ID

LOCAL_RANK
=
Node 內 Worker ID

WORLD_SIZE
=
全部 Worker 數量
```

```text
Rendezvous
=
Workers 找到彼此

Process Group
=
可以互相通訊的 Worker Group

MASTER_ADDR / PORT
=
Rendezvous Endpoint
```

```text
DDP
=
相同 Model
不同 Data
多 Worker 平行訓練

DistributedSampler
=
幫不同 Rank 分配不同 Data
```

```text
Gradient
=
Model Parameter 應該如何調整

AllReduce
=
同步各 Rank 的 Gradient

NCCL
=
NVIDIA GPU Collective Communication Library
```

```text
Speedup
=
Multi-GPU Throughput
/
Single-GPU Throughput
```

```text
Scaling Efficiency
=
Speedup
/
GPU Count
```

```text
Intra-node
=
同機 GPU Communication

Inter-node
=
跨 Node GPU Communication
```

---

# 36. Day1 Verification

Concept Verification：

```text
[✓] WORLD_SIZE 計算
[✓] RANK / LOCAL_RANK 區別
[✓] Rendezvous 概念
[✓] MASTER_ADDR / MASTER_PORT
[✓] Process Group
[✓] DDP Data Parallelism
[✓] DistributedSampler
[✓] Global Batch Size
[✓] Gradient
[✓] AllReduce
[✓] NCCL Role
[✓] Speedup
[✓] Scaling Efficiency
[✓] Intra-node / Inter-node
```

目前尚未驗證：

```text
[ ] Real Multi-GPU DDP
[ ] Real NCCL Communication
[ ] Real nccl-tests
[ ] Real Multi-node GPU Scaling
```

原因：

```text
GCP GPU Quota
```

後續有硬體後補做：

```text
Real Hardware Validation
```

---

# 37. Day1 Result

Week16 Day1 完成：

```text
Multi-GPU / Distributed Training Fundamentals
```

建立了後續：

```text
PyTorch DDP
↓
NCCL
↓
Distributed Training
↓
Scaling Analysis
↓
Communication Bottleneck Analysis
```

所需的底層知識。

---

# Interview Review

## Q1：RANK、LOCAL_RANK、WORLD_SIZE 有什麼差別？

`RANK` 是整個 Distributed Job 中 Worker 的全域唯一 ID；`LOCAL_RANK` 是 Worker 在自己 Node 內的編號；`WORLD_SIZE` 則是整個 Distributed Job 的 Worker 總數。

## Q2：PyTorch DDP 為什麼需要 AllReduce？

DDP 中每個 Rank 會處理不同資料並各自計算 Gradient，因此需要透過 AllReduce 同步 Gradient，讓所有 Worker 在 Optimizer Step 後維持一致的 Model Parameters。
