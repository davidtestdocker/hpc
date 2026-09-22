# Slurm Failure Troubleshooting Demo

## Demo 目的

以既有 CPU multi-node MPI 成功紀錄為 baseline，展示如何從 job PENDING 追到 node heartbeat 與底層 GCE infrastructure。這是獨立 Slurm supporting case，使用 historical evidence，未重跑或重建環境。

## Normal Multi-node MPI Evidence

[Multi-node 實驗紀錄](../history/20260922-before-current/week17/day4-slurm-multinode-hpc-cluster.md.txt) 記載 `hpc-demo` 作為 controller／login host，`compute-01`、`compute-02` 作為 CPU compute nodes。[MPI sbatch](../../mpi-multinode.slurm) 配置 2 nodes、每 node 2 tasks，並以 `mpirun --host compute-01:2,compute-02:2 -np 4 /tmp/mpi_hello` 啟動 [MPI 程式](../../mpi_hello.c)。

保存的成功輸出：

```text
JOB_ID=14
NODELIST=compute-[01-02]
NTASKS=4

Hello from rank 0 out of 4 processes
Hello from rank 1 out of 4 processes
Hello from rank 3 out of 4 processes
Hello from rank 2 out of 4 processes
```

此案例驗證 Slurm allocation 與 Open MPI 跨 CPU nodes 啟動。當時 `srun --mpi=pmi2` 遇到 Open MPI 未編譯 Slurm PMI support，因此採 Slurm 分配資源、mpirun 啟動 ranks 的方式。

## Failure Scenario

後續 [排障紀錄](../history/20260922-before-current/week20/day5-ai-hpc-production-troubleshooting.md.txt) 中，controller 仍保留 compute-01／02 設定，但兩台 GCE VM 已不存在。這是與 Job 14 成功執行不同時間點的故障案例。[Pending CPU script](../../slurm/pending-cpu-test.sbatch) 保存 cpu partition 的小型工作請求。

## Symptoms

歷史 node／job 狀態摘錄：

```text
State=DOWN+NOT_RESPONDING
Reason=Not responding

JobState=PENDING
NumNodes=1
NumCPUs=1
ReqNodeList=(null)
```

Job 15 的 pending reason：

```text
Nodes required for job are DOWN, DRAINED
or reserved for jobs in higher priority partitions
```

## Investigation Chain

以下是歷史調查的指令與判斷順序，不是本輪執行結果；完整判讀見 [runbook](../runbooks/ai-hpc-job-troubleshooting.md)。

| 調查入口 | 觀察與下一步 |
|---|---|
| `sinfo` | 先定位 partition 中不可用的 compute nodes |
| `scontrol show node compute-01`／`compute-02` | 確認 DOWN+NOT_RESPONDING 與 heartbeat 問題，往 slurmd／network／VM 層檢查 |
| `squeue` | 讀取 NODELIST(REASON)，辨別 PENDING 的具體原因 |
| `scontrol show job 15` | `ReqNodeList=(null)`，未綁死特定 node；仍無可用 CPU node 可分配 |
| GCE inventory 與 `slurm.conf` 比對 | 歷史紀錄確認 VM 已不存在，但 NodeName 設定仍保留 |
| `sacct -j 15` | 回傳 accounting storage disabled，無法補齊歷史 accounting 查詢 |

## Root Cause

Failure domain 位於 underlying compute infrastructure 與殘留配置：controller 仍認得兩個 configured nodes，但 VM 已移除，沒有 slurmd heartbeat；因此 nodes 變成 DOWN+NOT_RESPONDING，cpu partition 無可用 node，工作持續 PENDING。

這份證據支持「找到根因」，不支持「修復並成功重跑」。不要將這次 PENDING 解讀成 MPI application crash。

## Limitation

Accounting 的實際訊息為：

```text
Slurm accounting storage is disabled
```

因此 `sacct` 無法在該環境提供完整歷史查詢。沒有 Slurm recovery 成功證據；正常 multi-node MPI 是歷史 CPU workload，不是 GPU Slurm。

當時未建立 shared filesystem，透過 `/tmp` 工作目錄與檔案準備處理執行需求。OSU multi-node benchmark 因編譯問題未完成，不能宣稱已有 multi-node latency／bandwidth 結果。VM 不存在的結論來自歷史文件，本頁沒有補造 GCE inventory raw output。

## 面試重點

- PENDING 是症狀；結合 pending reason、node state 與 infrastructure inventory 才能定位根因。
- Slurm resource allocation 與 MPI rank launch 分工不同，PMI 相容性也屬實際整合邊界。
- 沒有 accounting 時依靠 controller 即時狀態與保存紀錄；根因確認不等於 recovery 驗證。
