<!-- readable-curriculum: 2026-09-22 -->
# Week17 Day2 — MPI 效能測試

[上一課](<day1-mpi-fundamentals.md>) · [本週目錄](README.md) · [下一課](<day3-hpc-communication-stack.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史單機OSU摘要。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

8567.71 MB/s按十進位約8.568 GB/s，原8.36混用1024與GB標記。所有rank同host且oversubscribe，不代表Ethernet／RDMA；OMB未保存在repo。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<day2-mpi-performance-benchmark.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
8567.71
```

hpc-demo OMB7.5.2：1B latency.43us、256KB bandwidth8567.71MB/s，只有文內摘要非完整raw。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：主平台是 CPU MPI rank smoke；Slurm 多 VM 與 Ray 為獨立案例，三個 worker Pods 不代表三台 node。
> **閱讀順序**：先學本文基礎，再讀[Week17 現行對照與檢核](../learning-guide.md#week17)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week17 Day2 — MPI Performance Benchmarking

## 對應檔案

OSU micro-benchmarks 的原始碼與執行檔由外部安裝，未保存在此儲存庫；實驗指令與結果保留於本文。

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day1-mpi-fundamentals](day1-mpi-fundamentals.md)。

---

## 今日平台新增能力

今天從「會使用 MPI」進一步進入：

    MPI Performance Analysis

使用業界標準工具：

    OSU Micro-Benchmarks (OMB)

完成以下 benchmark：

- Point-to-Point Latency
- Point-to-Point Bandwidth
- Collective AllReduce Latency
- Collective Broadcast Latency
- Message Size 對 Communication Performance 的影響分析
- Single-node Benchmark Limitation 分析

---

## 1. OSU Micro-Benchmarks

OSU Micro-Benchmarks 是 HPC 常用的 MPI Communication Benchmark Suite。

本次使用：

    OMB 7.5.2

主要工具：

    osu_latency
    osu_bw
    osu_allreduce
    osu_bcast

安裝位置：

    /opt/osu/libexec/osu-micro-benchmarks/

---

## 2. Point-to-Point Latency

執行：

    mpirun \
      --allow-run-as-root \
      --oversubscribe \
      -np 2 \
      /opt/osu/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_latency

用途：

    Rank 0 <-> Rank 1

測量兩個 MPI Process 之間的 Communication Latency。

Latency：

    一次 Communication 需要花多少時間

單位：

    us
    microsecond

本次部分結果：

    Size        Avg Latency(us)

    1 B              0.43
    1 KB             1.01
    4 KB             3.99
    64 KB           12.29
    256 KB          43.75
    1 MB           167.19
    4 MB          1061.43

觀察：

小 Message：

    Latency / software overhead

影響較明顯。

大 Message：

    Data movement / bandwidth

影響逐漸增加。

---

## 3. Point-to-Point Bandwidth

執行：

    mpirun \
      --allow-run-as-root \
      --oversubscribe \
      -np 2 \
      /opt/osu/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw

Bandwidth：

    一秒鐘可以傳輸多少資料

單位：

    MB/s
    GB/s

本次部分結果：

    Size        Bandwidth (MB/s)

    1 B               7.30
    512 B          1494.55
    2 KB           4519.78
    64 KB          6839.06
    128 KB         7794.73
    256 KB         8567.71
    512 KB         8169.95
    1 MB           7013.88
    4 MB           5042.19

本次峰值約：

    8567 MB/s

約等於：

    8.36 GB/s

觀察：

小 Message：

固定 Communication Overhead 比例很高，因此 Bandwidth 低。

Message Size 增加後：

固定成本比例下降，Bandwidth 上升。

當 Message 太大：

可能開始受到：

- Memory Copy
- Cache Pressure
- CPU Memory Bandwidth
- Buffer Management

等因素影響，因此 Bandwidth 不一定持續增加。

---

## 4. Latency vs Bandwidth

Latency：

    一次 Communication 要多久

Bandwidth：

    一秒可以搬多少資料

簡化 Communication Model：

    Communication Time
    =
    Latency
    +
    Data Size / Bandwidth

因此：

小 Message：

    Latency Dominated

大 Message：

    Bandwidth Dominated

這是 HPC Network Performance Analysis 的核心概念之一。

---

## 5. MPI AllReduce Benchmark

執行：

    mpirun \
      --allow-run-as-root \
      --oversubscribe \
      -np 4 \
      /opt/osu/libexec/osu-micro-benchmarks/mpi/collective/osu_allreduce

AllReduce：

    所有 Rank 提供資料
            |
            v
        Reduction
            |
            v
    所有 Rank 得到結果

本次部分結果：

    Size        Avg Latency(us)

    4 B              5.47
    1 KB            10.07
    4 KB            23.51
    64 KB          103.03
    256 KB         323.88
    512 KB         466.23
    1 MB          1066.40

AllReduce 比單純 Point-to-Point Communication 更重。

因為除了資料傳輸之外，還包含：

- Reduction Operation
- Multi-Rank Synchronization
- Collective Data Movement

---

## 6. MPI Broadcast Benchmark

執行：

    mpirun \
      --allow-run-as-root \
      --oversubscribe \
      -np 4 \
      /opt/osu/libexec/osu-micro-benchmarks/mpi/collective/osu_bcast

Broadcast：

    Root Rank
        |
        +--> Rank 1
        +--> Rank 2
        +--> Rank 3

本次部分結果：

    Size        Avg Latency(us)

    4 B              1.51
    1 KB             3.67
    4 KB            12.90
    64 KB           33.89
    256 KB         128.92
    512 KB         246.82
    1 MB           802.56

---

## 7. Bcast vs AllReduce

相同 Message Size 比較：

    Size        Bcast(us)     AllReduce(us)

    4 B             1.51            5.47
    1 KB            3.67           10.07
    4 KB           12.90           23.51
    64 KB          33.89          103.03
    256 KB        128.92          323.88
    1 MB          802.56         1066.40

Bcast：

    一個 Rank
        |
        v
    所有 Rank

AllReduce：

    所有 Rank
        |
        v
    Reduction
        |
        v
    所有 Rank

因此 AllReduce 通常需要更多 Communication 與 Synchronization。

---

## 8. MPI AllReduce 與 NCCL 的關係

MPI：

    MPI_Allreduce

主要負責一般 Distributed Process Communication。

NCCL：

    ncclAllReduce

專門針對 NVIDIA GPU Collective Communication 最佳化。

概念：

    MPI AllReduce

        CPU / Process

            ↓

    NCCL AllReduce

        GPU Communication

            ↓

    PyTorch DDP

        Gradient Synchronization

Distributed Training 中：

    Forward
       |
       v
    Backward
       |
       v
    Gradient AllReduce
       |
       v
    Model Update

如果 AllReduce Communication 很慢：

    GPU 等待
        |
        v
    Training Throughput 下降

---

## 9. Single-node Benchmark Limitation

本次所有 MPI Rank 都在同一台：

    hpc-demo

例如：

    Rank 0
    Rank 1
    Rank 2
    Rank 3

都位於同一 Host。

因此本次測量主要反映：

- Open MPI Runtime
- Shared Memory Communication
- Memory Copy
- CPU Scheduling
- Local Memory Performance

不能直接解讀為：

    真正 Multi-node Ethernet Latency

也不能直接解讀為：

    RDMA / RoCE Network Performance

本次結果的正確定位是：

    Single-node MPI Communication Baseline

真正 Multi-node HPC Cluster 還需要：

    Node A
      |
    Network
      |
    Node B

後續才能分析：

- TCP
- Ethernet
- RDMA
- RoCE
- InfiniBand
- GPUDirect RDMA

---

## 今日成果

完成：

- OSU Micro-Benchmarks 安裝
- osu_latency
- osu_bw
- osu_allreduce
- osu_bcast
- Latency vs Bandwidth
- Message Size Performance Analysis
- Collective Communication Performance Analysis
- MPI AllReduce 與 NCCL / PyTorch DDP 關聯
- Single-node Benchmark Limitation Analysis

今天平台已從：

    MPI API Learning

提升到：

    MPI Communication Performance Analysis

---

## Interview Review

### Q1：Latency 與 Bandwidth 有什麼差別？

Latency 代表一次 Communication 需要花多少時間，通常對小 Message 特別重要。

Bandwidth 代表單位時間可以傳輸多少資料，對大型 Message 或大量 Data Movement 特別重要。

### Q2：為什麼 MPI AllReduce 通常比 Broadcast 成本高？

Broadcast 主要是由一個 Root Rank 將資料傳給其他 Rank。

AllReduce 則需要所有 Rank 共同參與 Reduction、Synchronization 與資料交換，最後再讓所有 Rank 都取得結果，因此 Communication 成本通常更高。
