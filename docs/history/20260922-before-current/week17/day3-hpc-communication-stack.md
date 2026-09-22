<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：主平台是 CPU MPI rank smoke；Slurm 多 VM 與 Ray 為獨立案例，三個 worker Pods 不代表三台 node。
> **閱讀順序**：先學本文基礎，再讀[Week17 現行對照與檢核](<../../../learning-guide.md#week17>)及[對應現行入口](<../../../runbooks/automatic-worker.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week17 Day3 — HPC Communication Stack

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day5-nccl-transport-debugging](<../../../week18/day5-nccl-transport-debugging.md>)。

---

## 今日平台新增能力

今天建立 HPC / AI Cluster 的 Communication Stack 觀念與 Troubleshooting 能力。

核心技術：

- MPI
- NCCL
- TCP/IP
- RDMA
- RoCE
- InfiniBand
- GPUDirect RDMA
- RDMA NIC / Network Fabric

今天重點不是硬做不存在的 RDMA Benchmark，而是學會：

    HPC Communication 各層角色
    +
    如何判斷主機是否具備 RDMA Capability
    +
    如何定位 Communication Bottleneck

---

## 1. HPC Communication Stack

完整架構：

    AI / HPC Application
            |
            v
    PyTorch DDP / MPI Program / Ray
            |
            v
    Communication Library
            |
            +-- MPI
            |
            +-- NCCL
            |
            v
    Communication Mechanism
            |
            +-- TCP/IP
            |
            +-- RDMA
                  |
                  +-- InfiniBand
                  |
                  +-- RoCE
            |
            v
    NIC / Network Fabric

這些技術不是同一層。

MPI / NCCL：

    Communication Library

RDMA / TCP：

    Communication Mechanism / Transport

RoCE / InfiniBand：

    Network Fabric / RDMA Implementation

NIC：

    真正執行資料傳輸的 Hardware

---

## 2. MPI

MPI：

    Message Passing Interface

用途：

    General Distributed Process Communication

常見操作：

    MPI_Send
    MPI_Recv
    MPI_Bcast
    MPI_Reduce
    MPI_Allreduce

MPI 本身不是 Network Hardware。

MPI 可以使用不同底層 Communication Path，例如：

    MPI
     |
     +-- Shared Memory
     |
     +-- TCP
     |
     +-- RDMA

---

## 3. NCCL

NCCL：

    NVIDIA Collective Communications Library

用途：

    NVIDIA GPU Collective Communication

常見操作：

    AllReduce
    AllGather
    ReduceScatter
    Broadcast

典型場景：

    PyTorch DDP
        |
        v
    NCCL
        |
        v
    GPU Communication

MPI 與 NCCL 的簡化比較：

    MPI
    = General Distributed Process Communication

    NCCL
    = NVIDIA GPU Collective Communication

NCCL 同樣不是 NIC。

NCCL 會根據環境選擇底層 Communication Path，例如：

    NCCL
     |
     +-- NVLink
     +-- PCIe
     +-- Socket
     +-- RDMA

---

## 4. TCP/IP

一般 Ethernet Communication 常見路徑：

    Application
        |
        v
    Kernel
        |
        v
    TCP/IP Stack
        |
        v
    NIC
        |
        v
    Network

TCP/IP 的優點：

- 通用
- 部署容易
- Ethernet 環境普遍

缺點：

- Kernel Overhead
- Memory Copy
- CPU Involvement
- Latency 通常比 RDMA 高

---

## 5. RDMA

RDMA：

    Remote Direct Memory Access

核心概念：

    讓一台機器更直接地存取另一台機器的 Memory，
    減少 CPU 與 Kernel 介入。

簡化資料路徑：

    Node A Memory
         |
         v
    RDMA NIC
         |
         v
    Network
         |
         v
    RDMA NIC
         |
         v
    Node B Memory

常見優勢：

- Low Latency
- High Bandwidth
- Lower CPU Overhead
- Fewer Memory Copies

RDMA 是 Communication Mechanism，不是一張特定網卡名稱。

---

## 6. InfiniBand

InfiniBand 是專門為 HPC 設計的 Network Fabric。

特性：

- 原生支援 RDMA
- Low Latency
- High Bandwidth
- HPC / Supercomputer 常見
- 需要對應 NIC / Switch / Fabric

架構：

    Application
        |
        v
    MPI / NCCL
        |
        v
    RDMA
        |
        v
    InfiniBand
        |
        v
    RDMA NIC

---

## 7. RoCE

RoCE：

    RDMA over Converged Ethernet

意思：

    在 Ethernet Network 上提供 RDMA。

架構：

    Application
        |
        v
    MPI / NCCL
        |
        v
    RDMA
        |
        v
    RoCE
        |
        v
    Ethernet

RoCE 不是與 RDMA 競爭的技術。

關係：

    RDMA
     |
     +-- InfiniBand
     |
     +-- RoCE

---

## 8. RoCEv1 vs RoCEv2

RoCEv1：

    Layer 2

主要限制在同一 Layer 2 Network Domain。

RoCEv2：

    UDP / IP
    Layer 3 Routable

大型 Data Center / AI Cluster 更常看到 RoCEv2。

---

## 9. RoCE Network Tuning

RoCE 對 Network Congestion 與 Packet Loss 很敏感。

常見技術：

- PFC
- ECN
- DCQCN
- QoS

### PFC

PFC：

    Priority Flow Control

用途：

    當特定 Traffic Priority 的 Buffer 快滿時，
    暫停對應流量，降低 Packet Loss。

簡化：

    Sender
       |
       v
    Switch Buffer
       |
       v
    PFC Pause
       |
       v
    Sender Temporarily Stops

### ECN

ECN：

    Explicit Congestion Notification

用途：

    Network 開始 Congestion 時，
    在真正大量丟包前通知 Sender 降低傳輸速度。

簡化：

    Switch Congestion
          |
          v
       ECN Mark
          |
          v
    Sender Reduces Rate

---

## 10. GPUDirect RDMA

一般跨節點 GPU Communication：

    GPU Memory
        |
        v
    Host Memory
        |
        v
    CPU / Kernel
        |
        v
    NIC
        |
        v
    Network
        |
        v
    Remote Host Memory
        |
        v
    Remote GPU

GPUDirect RDMA：

    GPU Memory
        |
        v
    RDMA NIC
        |
        v
    Network
        |
        v
    Remote RDMA NIC
        |
        v
    Remote GPU Memory

主要價值：

- 減少 Host Memory Copy
- 減少 CPU Involvement
- Lower Latency
- Higher GPU-to-GPU Inter-node Throughput

大型 AI Cluster 常見組合：

    PyTorch DDP
         |
         v
    NCCL
         |
         v
    GPUDirect RDMA
         |
         v
    RoCE / InfiniBand
         |
         v
    RDMA NIC

---

## 11. RDMA Tooling

今天使用以下工具檢查 Linux RDMA Environment。

### rdma

查看 Linux RDMA subsystem：

    rdma dev
    rdma link

如果沒有任何輸出：

    Kernel RDMA Stack 可能存在，
    但沒有 RDMA Device 被偵測到。

---

### ibv_devices

用途：

    列出 libibverbs 可以看到的 RDMA Devices。

本次結果：

    device                 node GUID
    ------              ----------------

沒有任何 Device。

代表：

    libibverbs tooling 有
    RDMA NIC 沒有

---

### ibv_devinfo

用途：

    查看 RDMA Device 詳細 Capability。

常見資訊：

    Device
    Transport
    Firmware
    Port State
    Link Layer
    MTU

常見判斷：

    link_layer: Ethernet

可能代表 RoCE Environment。

    link_layer: InfiniBand

代表 InfiniBand Fabric。

---

### ibstat

用途：

    查看 InfiniBand / RDMA Port Status。

常見重點：

    State
    Physical State
    Rate

例如：

    State: Active
    Physical State: LinkUp

如果：

    State: Down

代表底層 Link 已有問題，
不應直接先怪 MPI 或 NCCL。

---

## 12. Kernel RDMA Stack

執行：

    lsmod | grep -E 'rdma|ib_core|mlx'

本次結果：

    ib_core 507904 0

代表：

    Linux Kernel 有 RDMA / InfiniBand Core Subsystem。

但有 Kernel Module：

    不代表有 RDMA Hardware。

---

## 13. PCI / NIC Hardware Check

執行：

    lspci | grep -Ei 'ethernet|network|mellanox|nvidia'

本次結果：

    00:04.0 Ethernet controller:
    Red Hat, Inc. Virtio network device

代表目前 hpc-demo 使用：

    Virtio Virtual Ethernet NIC

沒有看到：

- NVIDIA / Mellanox ConnectX
- InfiniBand NIC
- RDMA-capable NIC

---

## 14. hpc-demo RDMA Capability 結論

目前環境：

    hpc-demo

結果：

    RDMA command       有
    ib_core            有
    libibverbs tools   有
    RDMA Device        沒有
    RDMA Link          沒有
    NIC                Virtio Ethernet

因此目前：

    RDMA Software Stack
    = Available

但是：

    RDMA-capable Hardware
    = Not Available

所以目前不能實測：

- RoCE
- InfiniBand
- RDMA Bandwidth
- GPUDirect RDMA

目前這台主機適合：

- RDMA Architecture Learning
- Tooling Familiarity
- Capability Detection
- Troubleshooting Flow

---

## 15. HPC Communication Troubleshooting Flow

假設遇到：

    NCCL AllReduce 很慢

不要直接判斷：

    NCCL 有問題

正確排查順序：

    1. Hardware / NIC
            |
            v
    2. RDMA Device
            |
            v
    3. Link / Port State
            |
            v
    4. Network Performance
            |
            v
    5. NCCL Transport
            |
            v
    6. Application Behavior

---

## 16. Step 1 — NIC / Hardware

先看：

    lspci | grep -Ei 'ethernet|network|mellanox|nvidia'

確認：

- NIC 類型
- 是否有 RDMA-capable NIC
- 是否為 ConnectX / Mellanox / NVIDIA NIC

如果 Hardware 根本不支援 RDMA：

    就不需要繼續調 RoCE / InfiniBand。

---

## 17. Step 2 — RDMA Device

檢查：

    rdma dev
    rdma link
    ibv_devices

如果都是空：

    RDMA Device 不存在

此時不要浪費時間調：

    NCCL_IB_HCA
    NCCL_IB_GID_INDEX

因為底層根本沒有 RDMA Device。

---

## 18. Step 3 — Link / Port

有 RDMA Device 時再看：

    ibv_devinfo
    ibstat

確認：

    State: Active
    Physical State: LinkUp
    Rate: Expected Speed

如果 Link Down：

    問題在 NIC / Driver / Network，
    不是 Application Layer。

---

## 19. Step 4 — Network Performance

底層 Link 正常後再測：

    iperf3
    perftest
    OSU Micro-Benchmarks

主要觀察：

- Latency
- Bandwidth
- Packet Loss
- Congestion

如果 Network Performance 已經很差：

    NCCL 慢只是上層症狀。

---

## 20. Step 5 — NCCL Transport

再查看：

    NCCL_DEBUG=INFO

確認 NCCL 真正使用的 Path：

    Socket
    RDMA
    NVLink
    PCIe

如果預期使用 RDMA，
但 NCCL Log 顯示：

    NET/Socket

代表 NCCL 沒有走預期的 RDMA Path。

---

## 21. Step 6 — Application Layer

底層正常後才分析：

- PyTorch DDP
- Batch Size
- Gradient Size
- Compute / Communication Ratio
- Compute / Communication Overlap

有時 Communication 慢不是 Network Fault，

而是 Workload 本身：

    Communication-bound

---

## 22. 最終技術分層

今天最重要的一張圖：

    AI / HPC Workload
            |
            v
    PyTorch DDP / MPI / Ray
            |
            v
    MPI / NCCL
            |
            v
    TCP / RDMA
            |
            v
    RoCE / InfiniBand / Ethernet
            |
            v
    NIC / Network Fabric

GPU Cluster 典型 Path：

    PyTorch DDP
         |
         v
    NCCL
         |
         v
    GPUDirect RDMA
         |
         v
    RoCE / InfiniBand
         |
         v
    RDMA NIC
         |
         v
    Remote GPU

---

## 今日成果

完成：

- HPC Communication Stack 分層
- MPI vs NCCL
- TCP vs RDMA
- InfiniBand vs RoCE
- RoCEv1 vs RoCEv2
- PFC / ECN 基礎
- GPUDirect RDMA
- RDMA Linux Tooling
- Kernel RDMA Stack Check
- PCI / NIC Hardware Check
- RDMA Capability Detection
- HPC Communication Troubleshooting Flow

本次 hpc-demo 正式結論：

    RDMA Software Stack:
    Available

    RDMA-capable NIC:
    Not Available

    Current NIC:
    Virtio Ethernet

因此本次不宣稱任何實際 RDMA / RoCE Performance Result。

真正的 RDMA / RoCE Benchmark 將留到具備 RDMA-capable Multi-node Environment 時再驗證。

---

## Interview Review

### Q1：RDMA、RoCE、InfiniBand 三者是什麼關係？

RDMA 是 Remote Direct Memory Access 的 Communication Mechanism。

InfiniBand 是原生支援 RDMA 的 HPC Network Fabric。

RoCE 則是在 Ethernet 上實作 RDMA，因此 RoCE 與 InfiniBand 都可以提供 RDMA 能力。

### Q2：如果 NCCL AllReduce 很慢，應該如何排查？

應先從底層開始：

    NIC Hardware
    → RDMA Device
    → Link State
    → Network Performance
    → NCCL Transport
    → Application

不能一開始就假設 NCCL 本身有問題。
