<!-- readable-curriculum: 2026-09-22 -->
# Week17 Day1 — MPI rank 與 launcher

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-mpi-performance-benchmark.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史MPI collective輸出。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

MPI是標準，OpenMPI是實作；MPI→NCCL→DDP只是概念關聯，不是必經呼叫鏈。send_recv至少需2rank，現在code未防呆；MPI output順序不保證固定。

## 程式／設定與來源

本次核對：[mpi_hello.c](<../../mpi_hello.c>)、[mpi_allreduce.c](<../../mpi_allreduce.c>)、[mpi_reduce.c](<../../mpi_reduce.c>)、[mpi_broadcast.c](<../../mpi_broadcast.c>)、[mpi_send_recv.c](<../../mpi_send_recv.c>)

## 已有結果與解讀

來源：[記錄／示例原文](<day1-mpi-fundamentals.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Total sum = 100
```

4rank求和100是本課舊示例成果，並非主API的3rank hello工作負載。

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

# Week17 Day1 — MPI Fundamentals

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [mpi_allreduce.c](../../mpi_allreduce.c)
- [mpi_broadcast.c](../../mpi_broadcast.c)
- [mpi_hello.c](../../mpi_hello.c)
- [mpi_reduce.c](../../mpi_reduce.c)
- [mpi_send_recv.c](../../mpi_send_recv.c)

---

## 今日平台新增能力

今天正式進入 HPC Distributed Computing，建立 MPI 基礎能力：

- MPI Process / Rank
- MPI Communicator
- Point-to-Point Communication
- Collective Communication
- Broadcast / Reduce / AllReduce
- OpenMPI 基本操作

---

## 1. HPC 與 MPI

HPC（High Performance Computing）透過多個 CPU / GPU / Node 協同運算大型工作。

MPI（Message Passing Interface）是 HPC 常用的 Process Communication 標準。

基本模型：

    mpirun
      |
      +-- Rank 0
      +-- Rank 1
      +-- Rank 2
      +-- Rank 3

每個 Rank 都是一個獨立 Process。

---

## 2. OpenMPI Environment

版本確認：

    mpirun --version

目前環境：

    Open MPI 4.1.2

因目前使用 root 執行 Lab，需要：

    --allow-run-as-root

目前 CPU slot 不足以直接啟動 4 個 Process，因此 Lab 使用：

    --oversubscribe

例如：

    mpirun \
      --allow-run-as-root \
      --oversubscribe \
      -np 4 \
      ./mpi_hello

其中：

    -np 4

代表啟動 4 個 MPI Process：

    Rank 0
    Rank 1
    Rank 2
    Rank 3

---

## 3. MPI Process / Rank

重要 API：

    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

取得目前 Communicator 內的 Process 數量。

例如：

    -np 4

則：

    world_size = 4

取得目前 Process 的 Rank：

    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

可能得到：

    Rank 0
    Rank 1
    Rank 2
    Rank 3

Rank 是 MPI Process 的識別 ID。

---

## 4. MPI_Bcast

Broadcast：

一個 Rank 將資料傳給所有 Rank。

範例：

    Rank 0: data = 100

Broadcast 後：

    Rank 0 = 100
    Rank 1 = 100
    Rank 2 = 100
    Rank 3 = 100

核心 API：

    MPI_Bcast(
        &data,
        1,
        MPI_INT,
        0,
        MPI_COMM_WORLD
    );

參數：

- `&data`：資料位置
- `1`：資料數量
- `MPI_INT`：資料型態
- `0`：Root Rank
- `MPI_COMM_WORLD`：參與 Communication 的 Process 群組

實測結果：

    Rank 0 created data = 100
    Rank 0 received data = 100
    Rank 1 received data = 100
    Rank 2 received data = 100
    Rank 3 received data = 100

---

## 5. MPI_Reduce

Reduce：

多個 Rank 的資料進行聚合，結果只交給指定 Root。

範例：

    Rank 0 = 10
    Rank 1 = 20
    Rank 2 = 30
    Rank 3 = 40

使用：

    MPI_SUM

結果：

    10 + 20 + 30 + 40 = 100

只有 Root Rank 得到：

    Rank 0 = 100

核心 API：

    MPI_Reduce(
        &value,
        &total,
        1,
        MPI_INT,
        MPI_SUM,
        0,
        MPI_COMM_WORLD
    );

實測：

    Total sum = 100

---

## 6. MPI_Allreduce

AllReduce：

所有 Rank 的資料先進行聚合，再將結果提供給所有 Rank。

可以理解為：

    Reduce + Broadcast

範例：

    Rank 0 = 10
    Rank 1 = 20
    Rank 2 = 30
    Rank 3 = 40

SUM 後：

    100

最後：

    Rank 0 = 100
    Rank 1 = 100
    Rank 2 = 100
    Rank 3 = 100

核心 API：

    MPI_Allreduce(
        &local_value,
        &global_sum,
        1,
        MPI_INT,
        MPI_SUM,
        MPI_COMM_WORLD
    );

與 `MPI_Reduce` 不同：

`MPI_Allreduce` 不需要 Root，因為所有 Rank 都會取得結果。

實測：

    Rank 3: local_value = 40, global_sum = 100
    Rank 0: local_value = 10, global_sum = 100
    Rank 1: local_value = 20, global_sum = 100
    Rank 2: local_value = 30, global_sum = 100

---

## 7. Point-to-Point Communication

MPI 除了 Collective Communication，也支援指定 Rank 之間直接通信。

主要 API：

    MPI_Send()
    MPI_Recv()

本次測試：

    Rank 0
      |
      | data = 123
      v
    Rank 1

實測：

    Rank 0 sent data = 123 to Rank 1
    Rank 1 received data = 123 from Rank 0

Point-to-Point：

    Rank A <-> Rank B

Collective Communication：

    多個 Rank 一起參與 Communication

---

## 8. Communication 類型整理

### Point-to-Point

    MPI_Send
    MPI_Recv

用途：

指定 Process 之間直接交換資料。

### Collective

    MPI_Bcast
    MPI_Reduce
    MPI_Allreduce

用途：

多個 Process 共同參與 Communication。

---

## 9. MPI 與 AI Distributed Training

今天最重要的連結：

    MPI_Allreduce
          |
          v
    NCCL AllReduce
          |
          v
    PyTorch DDP
    Gradient Synchronization

MPI：

    CPU / General Process Communication

NCCL：

    NVIDIA GPU Collective Communication

PyTorch DDP：

每個 Worker 計算自己的 Gradient，之後透過 AllReduce 進行 Gradient Synchronization，使所有 Worker 的 Model 保持一致。

---

## 今日成果

完成：

- OpenMPI Runtime 驗證
- MPI Process / Rank
- MPI_COMM_WORLD
- MPI_Bcast
- MPI_Reduce
- MPI_Allreduce
- MPI_Send / MPI_Recv
- Point-to-Point vs Collective Communication
- MPI AllReduce 與 NCCL / PyTorch DDP 的概念連結

Day1 主要目的是建立 HPC Distributed Communication 基礎。

Day2 將使用標準 HPC Benchmark 工具開始進行 MPI Performance Analysis，包括：

- Latency
- Bandwidth
- Message Size
- Collective Performance

---

## Interview Review

### Q1：MPI_Reduce 與 MPI_Allreduce 有什麼差別？

MPI_Reduce 會將所有 Rank 的資料進行聚合，但結果只交給指定 Root Rank。

MPI_Allreduce 則會將聚合結果提供給所有 Rank，因此常用於 Distributed Training 的 Gradient Synchronization。

### Q2：Point-to-Point 與 Collective Communication 有什麼差別？

Point-to-Point 是指定兩個 Rank 直接通信，例如 MPI_Send / MPI_Recv。

Collective Communication 則需要一組 Rank 共同參與，例如 MPI_Bcast、MPI_Reduce、MPI_Allreduce。
