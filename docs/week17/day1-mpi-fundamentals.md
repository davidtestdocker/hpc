<!-- readable-curriculum: 2026-09-22 -->
# Week17 Day1 — MPI rank 與 launcher

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-mpi-performance-benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

MPI_Comm_rank 取得本程序編號，MPI_Comm_size 取得群組大小。hostname 讓你知道程序所在 host，但容器 hostname 不必然等於實體 node 名稱。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[mpi_hello.c](<../../mpi_hello.c>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```c
    MPI_Init(&argc, &argv);


    int world_size;
    int world_rank;


    /*
     * 取得 MPI communicator 裡總共有多少 process
     *
     * MPI_COMM_WORLD:
     * 代表目前所有 MPI process 的集合。
     *
     * 例如：
     * mpirun -np 4
     *
     * world_size = 4
     *
     * 代表目前有：
     * Rank 0
     * Rank 1
     * Rank 2
     * Rank 3
     */
```

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week17/day1-mpi-fundamentals.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
