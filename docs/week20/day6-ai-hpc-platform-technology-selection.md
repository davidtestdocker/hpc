<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day6 — 架構選型與整體說明

[上一課](<day5-ai-hpc-production-troubleshooting.md>) · [本週目錄](README.md) · [整體展示](../../README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

FastAPI 接請求、Redis 保存接續 record、PostgreSQL 保存 metadata、Kueue 准入、JobSet 管理 MPI 群組；獨立 runner 做訓練。跨 DB 雙寫與結果儲存邊界仍在，不靠增加工具掩蓋。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[docs/architecture/platform-architecture.md](<../architecture/platform-architecture.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

````text
## Main Platform Flow

```mermaid
flowchart TD
    CLIENT["Client"]
    subgraph SERVICES["Platform service layer — system-pool"]
        API["FastAPI"]
        DB["PostgreSQL — initial job metadata"]
        QUEUE["Redis — job state / job_queue"]
        WORKER["api-worker — background polling / collector"]
    end
    subgraph ORCHESTRATION["Kubernetes resource orchestration"]
        KAPI["Kubernetes API"]
        JS["JobSet — distributed job lifecycle grouping"]
        KUEUE["Kueue — queue / quota / resource admission / TAS"]
        SCHED["Kubernetes Scheduler — Pod placement"]
    end
    subgraph COMPUTE["Distributed / GPU workload layer — gpu-pool"]
        LAUNCHER["MPI Launcher × 1"]
        WORKERS["MPI Workers × 3"]
        RANKS["mpirun — MPI ranks 0 / 1 / 2"]
    end
    CLIENT -->|"POST /benchmark"| API
    API -->|"insert initial metadata"| DB
````

## 已有結果與解讀

### 自動工作驗收：已保存的真實結果

日期：2026-09-22T04:58:58.875811+00:00。環境：GKE hpc-gpu-sg，既有單 L4 叢集上的 **CPU MPI**，不是 GPU 訓練。

| 情境 | 保存的結果 | 怎麼解讀 |
|---|---|---|
| 正常工作 `f2d8df72-aef3-48bf-9d6b-6863523daa65` | `completed`；ranks `[0, 1, 2]` | 真實 MPI 程序啟動、完成並自動收回結果 |
| worker 重啟 `a697300a-b267-4554-bdd5-2c82bb9c9eda` | `completed`；同 job 的 JobSet 數 `1` | 停止期间 Kubernetes 已完成，worker 恢復後接續收集 |
| 模擬 dispatch 失敗 `0852fb7b-8efd-4600-b8ac-d4205554f6f3` | `failed`；retry_count `3` | 模擬提交分支耗盡重試，不是 MPI kernel crash |

正常工作的 launcher log 原文摘錄（只省略 SSH known-host warning）：

```text
RANK=0 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-0-0
RANK=1 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-1-0
RANK=2 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-2-0
```

驗收後的 queue 與手動端點結果，取自同份 JSON：

```json
{
  "database_status": {
    "a697300a-b267-4554-bdd5-2c82bb9c9eda": "completed",
    "f2d8df72-aef3-48bf-9d6b-6863523daa65": "completed",
    "0852fb7b-8efd-4600-b8ac-d4205554f6f3": "failed"
  },
  "queues": {
    "job_queue": [],
    "processing_queue": [],
    "dead_letter_queue": [
      "0852fb7b-8efd-4600-b8ac-d4205554f6f3"
    ]
  },
  "manual_endpoint_rejections": {
    "process-next": 409,
    "collect-mpi": 409,
    "recover-stuck": 409
  }
}
```

空 job_queue／processing_queue 表示本次驗收工作已清理；failed ID 留在 dead-letter。409 是自動模式刻意拒絕手動推進端點，並非 API 故障。這些結果不保證跨 DB 原子交易、Redis 全失恢復或 node failover。

來源：[完整原始驗收 JSON](<../evidence/automatic-worker-20260922.json>)。無須再提交一次工作。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week20/day6-ai-hpc-platform-technology-selection.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：已驗證 worker 重啟接續；不等於 node failover、Redis 全失恢復或跨 DB 原子交易。
> **閱讀順序**：先學本文基礎，再讀[Week20 現行對照與檢核](../learning-guide.md#week20)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week20 Day6 — AI/HPC Platform 技術選型與架構比較

## 對應檔案

文中的 `job.slurm` 是示意檔名；OpenStack、HTCondor、LSF、DLRover 的選型討論未對應獨立部署檔案。

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[platform-architecture](../architecture/platform-architecture.md)。

---

## 今日目標

今天不做大量安裝與實作，重點是建立 AI/HPC Platform 的技術分層與選型能力。

需要能分清楚：

- OpenStack
- Slurm
- HTCondor
- LSF
- DLRover

它們不是同一層，也不是互相完全替代。

---

## 1. 技術總覽

| 技術 | 所在層 | 核心用途 | 適合場景 | 最重要關鍵字 |
|---|---|---|---|---|
| OpenStack | Infrastructure / IaaS | 建立與管理 VM、Network、Storage、Bare Metal | Private Cloud、Datacenter、AI/HPC Infrastructure | Nova、Neutron、Cinder、Glance、Keystone、Ironic |
| Slurm | HPC Scheduler | HPC Job 資源分配與排程 | MPI、多節點 GPU Training、HPC | Partition、GRES、Priority、FairShare |
| HTCondor | HTC Scheduler | 大量獨立 Job 的資源 Matchmaking | Simulation、Parameter Sweep、大量 Batch Jobs | ClassAd、Requirements、Rank、Matchmaking |
| LSF | Enterprise HPC Scheduler | 企業級 HPC Workload Management | EDA、半導體、Simulation、Enterprise HPC | Queue、Fair Share、Reservation、Backfill |
| DLRover | Distributed Training Orchestration | Training Worker Recovery / Elastic Training | 長時間、多節點 Distributed Training | Fault Tolerance、Elastic、Rendezvous、Recovery |

---

## 2. 整體架構層級

    Physical Hardware
            ↓
    OpenStack / Public Cloud
            ↓
    VM / Bare Metal
            ↓
    Kubernetes / Slurm / LSF / HTCondor
            ↓
    DLRover / Ray
            ↓
    PyTorch DDP
            ↓
    NCCL
            ↓
    GPU / Network

核心概念：

    OpenStack
    = Infrastructure

    Slurm / LSF / HTCondor
    = Workload Scheduler

    DLRover / Ray
    = Distributed Runtime / Training Orchestration

    PyTorch DDP
    = Distributed Training

    NCCL
    = GPU Communication

---

# 3. OpenStack

OpenStack 可以理解成：

    公司自己建立的 Cloud Platform

角色類似：

    AWS
    GCP
    Azure

但通常部署在企業自己的 Datacenter。

---

## OpenStack 核心元件

| 元件 | 功能 |
|---|---|
| Keystone | Identity / Authentication / Authorization |
| Nova | Compute / VM |
| Neutron | Network / Subnet / Port / IP |
| Cinder | Block Storage |
| Glance | VM Image |
| Ironic | Bare Metal Provisioning |

快速記：

    Keystone = Auth
    Nova = VM
    Neutron = Network
    Cinder = Disk
    Glance = Image
    Ironic = Bare Metal

---

## OpenStack 與 Terraform

Terraform 不是 OpenStack 的替代品。

關係：

    Terraform
        ↓
    OpenStack Provider
        ↓
    OpenStack API
        ↓
    Nova / Neutron / Cinder
        ↓
    VM / Network / Volume

因此：

    OpenStack
    = Cloud Platform

    Terraform
    = Infrastructure as Code Tool

---

## Nova Scheduler

Nova Scheduler 決定：

    VM 要放到哪一台 Physical Compute Host

它可能根據：

- CPU
- Memory
- NUMA
- GPU / PCI Device
- Availability Zone
- Host Aggregate

基本概念：

    Filter
    = 哪些 Host 可以跑

    Weigher
    = 符合條件後偏好哪一台

---

## Flavor

Flavor 是：

    VM 規格模板

例如：

    8 vCPU
    32 GB RAM
    1 GPU

概念接近：

    GCP Machine Type

---

## OpenStack 與 HPC 效能

高效能 workload 可能使用：

| 技術 | 用途 |
|---|---|
| PCI Passthrough | GPU 直接分配給 VM |
| SR-IOV | 高效能 NIC / RDMA Device 給 VM |
| CPU Pinning | vCPU 固定 Physical CPU Core |
| HugePages | 降低 Memory Translation Overhead |
| NUMA Affinity | CPU / GPU / NIC 盡量靠近 |
| Ironic | 直接 Provision Bare Metal |

Bare Metal：

    Physical Server
        ↓
    Linux
        ↓
    Slurm / Kubernetes / Application

沒有 VM。

---

# 4. HTCondor

HTCondor 主要面向：

    High Throughput Computing
    HTC

重點不是單一 Job 跑得多快，而是：

    大量 Job 的總吞吐量

典型 workload：

    100,000 個 independent jobs

例如：

- Simulation
- Parameter Sweep
- Research Batch
- Independent Inference Jobs

---

## HPC vs HTC

| HPC | HTC |
|---|---|
| 一個大型 Parallel Job | 大量獨立 Job |
| Multi-node Communication 很重要 | Job 通常彼此獨立 |
| MPI / NCCL / RDMA | Matchmaking / Throughput |
| Slurm 常見 | HTCondor 常見 |

---

## ClassAd

HTCondor 核心：

    Job ClassAd
        ↕
    Machine ClassAd

Machine 描述：

    CPU
    Memory
    GPU
    OS
    Architecture

Job 描述：

    RequestCpus
    RequestMemory
    Requirements
    Rank

---

## Requirements 與 Rank

    Requirements
    = 硬條件
    = 能不能跑

    Rank
    = 偏好
    = 符合條件後比較喜歡哪台

例如：

    Requirements:
    GPU >= 1

沒有 GPU 的 Machine 直接淘汰。

---

## HTCondor Submit

Slurm：

    sbatch job.slurm

HTCondor：

    condor_submit job.sub

注意：

    sbatch ≈ condor_submit

而不是：

    sbatch ≈ queue

HTCondor Submit File 裡：

    queue
    = 產生 Job

    queue 100
    = 一次產生 100 個 Jobs

---

## 常用 HTCondor 概念

| 概念 | 意義 |
|---|---|
| condor_q | 查看目前 Active Queue |
| condor_history | 查看歷史 Job |
| Idle | 等待適合的 Machine |
| Held | Job 被 Hold，需要處理問題 |
| Eviction | Running Job 被移出 Machine |
| Preemption | 因 Priority / Policy 把資源讓給其他 Job |
| Checkpoint | 被 Evict 後可從先前進度恢復 |

---

## HTCondor 架構

    Submit Node
        ↓
      schedd
        ↓
    Central Manager
    ├─ collector
    └─ negotiator
        ↓
    Execute Node
        ↓
      startd
        ↓
      starter
        ↓
    Application

核心 Daemon：

    schedd
    = Job Queue Manager

    collector
    = 收集 Pool 狀態

    negotiator
    = Matchmaking / Priority / Fairness

    startd
    = Execute Node Resource Agent

    starter
    = 啟動 Workload

---

# 5. LSF

LSF 是：

    Enterprise HPC Workload Scheduler

常見於：

- Semiconductor
- EDA
- Automotive
- Pharma
- Engineering Simulation
- Enterprise HPC

---

## 基本對照

| Slurm | LSF |
|---|---|
| sbatch | bsub |
| squeue | bjobs |
| Partition | Queue |
| Node | Host |

LSF Queue 通常同時包含：

- User / Group Access
- Priority
- Runtime Limit
- Resource Limit
- Preemption Policy

---

## 為什麼 EDA 常見 LSF

EDA Job 不只需要：

    CPU
    RAM

還可能需要：

    Software License Token

例如：

    CPU available = 1000 cores

但：

    License Token = 100

即使 CPU 還有很多，也不能同時跑超過 License 可支援的 Job。

因此企業 Scheduler 要同時管理：

    Compute Resource
    +
    Software License Resource

---

## Fair Share

目的：

    避免單一 User / Team 長期佔滿資源

Scheduler 可能考慮：

- Historical Usage
- User Weight
- Group Weight
- Priority
- Resource Share

---

## Reservation

Reservation 用來避免大型 Job Starvation。

例如：

    Job A 需要 8 GPUs

現在沒有完整 8 GPUs 可用，但：

    30 分鐘後可以湊齊

Scheduler 可以：

    預留未來資源

確保 Job A 不會一直被小 Job 插隊。

---

## Backfill

Backfill：

    在不影響 Reservation 的前提下
    利用暫時空閒資源跑短 Job

例如：

    大 Job 30 分鐘後開始

現在可以塞：

    只跑 10 分鐘的小 Job

提高 Cluster Utilization。

快速記：

    Reservation
    = 保證大 Job 未來能跑

    Backfill
    = 利用等待期間的空檔

---

# 6. Slurm vs HTCondor vs LSF

| 項目 | Slurm | HTCondor | LSF |
|---|---|---|---|
| 主要定位 | HPC | HTC | Enterprise HPC |
| 典型工作 | MPI / Distributed GPU | 大量 Independent Jobs | EDA / Enterprise HPC |
| Multi-node | 強 | 非主要定位 | 強 |
| GPU Cluster | 常見 | 支援 | 常見 |
| Opportunistic Resource | 非主要定位 | 強 | 可支援 |
| 商業支援 | Open Source Ecosystem | Open Source | Commercial |
| 常見環境 | Supercomputer / AI Cluster | Research / Batch Farm | Enterprise / Semiconductor |

---

# 7. DLRover

DLRover 位於：

    Distributed Training Orchestration Layer

它不負責：

    VM Provisioning
    Kubernetes Pod Scheduling
    Slurm Resource Allocation

它主要處理：

- Worker Lifecycle
- Failure Detection
- Restart
- Rendezvous
- Elastic Training
- Training Recovery

---

## DLRover vs PyTorch DDP

PyTorch DDP：

    Distributed Training
    Gradient Synchronization
    AllReduce

DLRover：

    Distributed Training Lifecycle
    Worker Recovery
    Elastic Training
    Fault Tolerance

簡化：

    DDP
    = 大家一起算

    DLRover
    = 大家怎麼活著、掛了怎麼恢復

---

## DLRover Recovery Flow

    Worker Failure
        ↓
    Detect Failure
        ↓
    Restart Worker
        ↓
    Rendezvous
        ↓
    Rebuild Process Group
        ↓
    Restore Checkpoint
        ↓
    Resume Training

---

## Rendezvous

Rendezvous：

    Distributed Workers 重新集合並確認：

- Rank
- World Size
- Master Address
- Master Port
- Process Group Membership

快速記：

    Restart
    = Worker 回來

    Rendezvous
    = Worker 重新加入 Distributed Group

---

## Checkpoint

Checkpoint 可保存：

- Model Weights
- Optimizer State
- Training Step
- Learning Rate Scheduler State

目的：

    Worker Failure
        ↓
    不需要從 Step 0 重跑

而是：

    從最近的 Checkpoint 繼續

---

## Elastic Training

Elastic Training：

    Worker 數量可以改變

例如：

    8 Workers
        ↓
    2 Workers Failure
        ↓
    6 Workers
        ↓
    Rendezvous
        ↓
    Training Continues

之後資源恢復：

    6 → 8 Workers

需要注意：

- Global Batch Size
- Learning Rate
- Throughput
- Training Stability

快速記：

    Fault Tolerance
    = 掛掉能恢復

    Elastic Training
    = Worker 數量改變仍能繼續

---

# 8. Kubernetes / DLRover / DDP / NCCL 分工

    Kubernetes
    = Pod / Node Placement

    DLRover
    = Training Worker Lifecycle / Recovery

    PyTorch DDP
    = Distributed Gradient Synchronization

    NCCL
    = GPU Communication

完整流程：

    Kubernetes
        ↓
    DLRover
        ↓
    PyTorch DDP
        ↓
    NCCL
        ↓
    GPU

---

# 9. 技術選型 Decision Table

| 需求 | 優先考慮 |
|---|---|
| 建立 Private Cloud | OpenStack |
| 建 VM / Network / Storage | OpenStack |
| Provision Bare Metal | OpenStack Ironic |
| Multi-node MPI | Slurm |
| 大型 Distributed GPU Training | Slurm |
| 大量 Independent Jobs | HTCondor |
| Parameter Sweep | HTCondor |
| Opportunistic Computing | HTCondor |
| Enterprise HPC | LSF |
| EDA / Semiconductor | LSF |
| Training Worker Recovery | DLRover |
| Elastic Distributed Training | DLRover |
| Online Service / API / Microservice | Kubernetes |

---

# 10. 一眼判斷

    我要建立 Infrastructure？
    → OpenStack

    我要排大型 HPC / Multi-node GPU Job？
    → Slurm

    我要跑大量彼此獨立的小 Job？
    → HTCondor

    我要企業 HPC / EDA / Commercial Scheduler？
    → LSF

    我的 Distributed Training Worker 掛掉後要恢復？
    → DLRover

---

# Day6 Outcome

完成：

- OpenStack Infrastructure Architecture
- Nova / Neutron / Cinder / Glance / Keystone / Ironic
- OpenStack VM / Bare Metal / HPC Performance Concepts
- HTCondor HTC Model
- ClassAd / Requirements / Rank / Matchmaking
- HTCondor Scheduling Architecture
- LSF Enterprise HPC Model
- Fair Share / Reservation / Backfill
- Slurm / HTCondor / LSF Selection
- DLRover Fault Tolerance
- Rendezvous / Checkpoint / Elastic Training
- AI/HPC Platform Layering

---

# Interview Review

## Q1. Slurm、HTCondor、LSF 最主要的差異是什麼？

Slurm 主要適合 MPI、多節點 GPU Training 等 HPC Workload；HTCondor 偏向大量彼此獨立的 High Throughput Jobs；LSF 則常用於企業 HPC、EDA 與需要商業支援和複雜資源政策的環境。

## Q2. DLRover、Kubernetes、PyTorch DDP 分別負責什麼？

Kubernetes 負責 Pod 與 Node Placement；DLRover 負責 Distributed Training Worker 的生命週期、Fault Tolerance、Elastic Recovery 與 Rendezvous；PyTorch DDP 則負責多個 Training Process 之間的 Gradient Synchronization。
