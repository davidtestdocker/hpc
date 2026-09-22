<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day5 — 跨層 production troubleshooting

[上一課](<day4-ha-node-failure-recovery.md>) · [本週目錄](README.md) · [下一課](<day6-ai-hpc-platform-technology-selection.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

排障先找最後成功階段，再沿依賴往下；Ray pending、Slurm node 不存在、Kueue admission blockage 是不同故障。已找到根因但未恢復，應明確記為未恢復。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[docs/runbooks/ai-hpc-job-troubleshooting.md](<../runbooks/ai-hpc-job-troubleshooting.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
# AI/HPC Job Troubleshooting Runbook

## Troubleshooting Order

遇到 AI/HPC Job 無法執行、卡住或失敗時，依序確認：

    1. Queue / Admission
    2. Scheduler / Placement
    3. Node / CPU / GPU Resource
    4. Container / Process
    5. Distributed Runtime
    6. Network / NCCL
    7. Application

不要一開始就直接看 application log。

---

## 1. Kubernetes / Kueue

### Workload 尚未 Admission

檢查：

```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week20/day5-ai-hpc-production-troubleshooting.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：已驗證 worker 重啟接續；不等於 node failover、Redis 全失恢復或跨 DB 原子交易。
> **閱讀順序**：先學本文基礎，再讀[Week20 現行對照與檢核](../learning-guide.md#week20)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week20 Day5 — AI/HPC Production Troubleshooting

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [ray-cluster.yaml](../../ray-cluster.yaml)：Ray 叢集
- [ray-resource-mismatch-job.yaml](../../ray-resource-mismatch-job.yaml)：Ray 資源不匹配實驗
- [ray-worker-recovery-job.yaml](../../ray-worker-recovery-job.yaml)：Ray worker 重試實驗
- [slurm/pending-cpu-test.sbatch](../../slurm/pending-cpu-test.sbatch)

---

## 今日新增內容

今天不重複 Week17 的 Slurm 基礎操作，重點放在：

- Ray scheduler resource mismatch
- Ray task retry 與 `NODE_DIED`
- KubeRay Worker recovery
- Slurm production troubleshooting chain
- Kubernetes / Kueue / Ray / Slurm 的跨層故障定位
- 建立 production troubleshooting runbook

Runbook：

    docs/runbooks/ai-hpc-job-troubleshooting.md

---

## 1. Ray：Kubernetes Healthy 不代表 Ray Task 能執行

實測環境：

    Kubernetes Pods = Running
    Ray Cluster CPU = 3
    Ray Cluster GPU = 0

Ray Task 要求：

    CPU = 1
    GPU = 1

Ray scheduler 顯示：

    {'CPU': 1.0, 'GPU': 1.0}: 1+ pending tasks/actors

問題不是：

    Kubernetes scheduler

而是：

    Ray scheduler resource mismatch

因此 troubleshooting 時要區分：

    Kubernetes scheduler
    ↓
    負責 Ray Pod placement

    Ray scheduler
    ↓
    負責 Task / Actor placement

核心：

    Pod Running != Ray Task schedulable

---

## 2. Ray Worker Failure 與 Task Retry

測試 Task 使用：

    max_retries=2

並設定：

    NodeAffinitySchedulingStrategy(..., soft=True)

Task attempt 0 原本在某個 Ray Worker 執行。

Worker Pod 被刪除後：

    attempt_number = 0
    state = FAILED
    error_type = NODE_DIED

Ray 隨後建立：

    attempt_number = 1

並將同一個 Task 排到另一個可用 Ray node。

流程：

    Ray Worker failure
    ↓
    Ray detects NODE_DIED
    ↓
    Task attempt fails
    ↓
    retry policy allows retry
    ↓
    Ray scheduler selects another Ray node
    ↓
    new task attempt runs

這是：

    Task-level recovery

---

## 3. Ray Recovery 與 KubeRay Recovery 不同

這次故障中其實同時存在兩種 recovery。

### Ray

負責：

    Task
    Actor
    Runtime scheduling
    Retry

例如：

    Task attempt 0
    ↓
    NODE_DIED
    ↓
    Task attempt 1

---

### KubeRay

負責：

    RayCluster desired state

當 Worker Pod 被刪除：

    desired workers = 2
    actual workers = 1

KubeRay Operator 會重新建立 Worker Pod。

因此：

    Ray
    = Task-level recovery

    KubeRay
    = Cluster / Worker Pod reconciliation

兩者不要混在一起。

---

## 4. MPI / JobSet 與 Ray Recovery 差異

Week20 Day4 的 MPI / JobSet：

    Worker failure
    ↓
    Child Job failure
    ↓
    JobSet FailurePolicy
    ↓
    RestartJobSet
    ↓
    Recreate distributed workload

Ray：

    Worker failure
    ↓
    Task NODE_DIED
    ↓
    retry policy
    ↓
    Task may run on another Ray node

因此：

    MPI / JobSet
    = whole-workload recovery

    Ray
    = fine-grained task recovery

這反映兩種 distributed runtime 的 recovery model 不同。

---

## 5. Slurm Production Troubleshooting

Week17 已經完成：

    slurmctld
    slurmd
    Partition
    sbatch
    Multi-node
    MPI
    Resource scheduling

Day5 不重新建立 Slurm Cluster。

今天新增的是 production troubleshooting chain。

---

## 6. Slurm Node Troubleshooting

先看：

    sinfo

如果 Node 狀態異常，例如：

    DOWN
    DRAIN
    NOT_RESPONDING

再看：

    scontrol show node <node>

本次實測：

    compute-01
    compute-02

狀態：

    DOWN+NOT_RESPONDING

Reason：

    Not responding

後來確認：

    compute-01
    compute-02

原本是 Week17 使用 GCE 建立的 compute VM。

目前 VM 已不存在，但：

    /etc/slurm/slurm.conf

仍保留：

    NodeName=compute-01
    NodeName=compute-02

所以：

    slurmctld still knows configured nodes
    ↓
    no slurmd heartbeat
    ↓
    node becomes DOWN+NOT_RESPONDING

這不是 scheduler bug。

真正 failure domain 是：

    underlying compute infrastructure

---

## 7. Slurm Job Troubleshooting

Job 15：

    State = PENDING

`squeue` 顯示原因：

    Nodes required for job are DOWN, DRAINED
    or reserved for jobs in higher priority partitions

再使用：

    scontrol show job 15

確認：

    JobState=PENDING
    NumNodes=1
    NumCPUs=1
    ReqNodeList=(null)

這表示：

    Job 沒有綁死某個指定 Node

而是：

    需要 cpu partition 裡任一可用 Node

但目前：

    compute-01 = DOWN
    compute-02 = DOWN

所以無法執行。

---

## 8. Slurm Accounting

嘗試：

    sacct -j 15

結果：

    Slurm accounting storage is disabled

因此目前環境沒有：

    SlurmDBD / accounting storage

所以：

    sacct

不能作為這套 lab 的 troubleshooting 工具。

實務環境若有啟用 accounting，`sacct` 可用來查：

    COMPLETED
    FAILED
    CANCELLED
    TIMEOUT
    OUT_OF_MEMORY
    NODE_FAIL
    ExitCode
    Elapsed

---

## 9. Cross-Layer Troubleshooting Model

AI/HPC Job 出問題時，不要直接假設是 application 問題。

建議順序：

    Queue / Admission
    ↓
    Scheduler / Placement
    ↓
    Node / Resource
    ↓
    Container / Process
    ↓
    Distributed Runtime
    ↓
    Network / NCCL
    ↓
    Application

---

## 10. Kubernetes / Kueue

### Queue / Admission

檢查：

    Workload
    ClusterQueue
    LocalQueue
    ResourceFlavor
    TAS

常見問題：

    quota insufficient
    topology domain unavailable
    flavor mismatch

---

### Kubernetes Scheduler

常見問題：

    Insufficient cpu
    Insufficient memory
    Insufficient nvidia.com/gpu
    taint mismatch
    affinity mismatch
    nodeSelector mismatch
    SchedulingDisabled

---

## 11. Ray

Ray troubleshooting 要再多一層：

    Kubernetes scheduler
    ↓
    Ray Pod placement

    Ray scheduler
    ↓
    Task / Actor placement

因此可能出現：

    Kubernetes Healthy
    +
    Ray Pods Running
    +
    Ray Tasks Pending

---

## 12. Slurm

Slurm troubleshooting：

    Job
    ↓
    Partition
    ↓
    Node
    ↓
    slurmd
    ↓
    VM / Physical Server

常用工具：

    sinfo
    squeue
    scontrol show node
    scontrol show job

---

## 13. GPU / Distributed Runtime

如果 scheduler 都正常，但 workload 還是失敗，再往下看：

    NVIDIA Driver
    CUDA
    GPU memory
    NCCL
    MPI
    Ray
    DDP

不能一看到：

    GPU training failed

就直接判斷：

    GPU hardware broken

---

## 14. Network Layer

Distributed AI/HPC 常見：

    DNS
    MTU
    TCP
    RDMA
    RoCE
    InfiniBand
    NCCL transport

例如之前 NCCL 實測：

    NET/IB : No device found

之後 fallback：

    NET/Socket

這代表：

    NCCL 可以啟動

但沒有使用：

    RDMA / IB transport

---

## 15. Production Troubleshooting 思路

錯誤案例：

    Training Job 沒跑
    ↓
    直接看 Python traceback

較好的做法：

    Job 是否 Admission？
    ↓
    Pod 是否建立？
    ↓
    Pod 是否 Scheduled？
    ↓
    Node 是否 Healthy？
    ↓
    Runtime 是否有足夠 Resource？
    ↓
    Distributed communication 是否正常？
    ↓
    最後才看 Application

核心：

    Locate failure domain first.

---

## Day5 Outcome

完成：

    Ray resource mismatch troubleshooting
    Ray NODE_DIED task recovery
    KubeRay Worker reconciliation
    MPI / Ray recovery model comparison
    Slurm node troubleshooting
    Slurm pending reason troubleshooting
    Cross-layer AI/HPC troubleshooting model
    Production troubleshooting runbook

新增：

    docs/runbooks/ai-hpc-job-troubleshooting.md

---

## Interview Review

### Q1. Kubernetes 的 Ray Pods 都是 Running，為什麼 Ray Task 還可能 Pending？

因為 Kubernetes scheduler 只負責 Ray Pod placement，而 Ray Task / Actor 是由 Ray scheduler 再次排程。如果 Task 要求的 CPU、GPU 或其他 Ray resource 不存在，即使所有 Kubernetes Pod 都 Running，Task 仍會 Pending。

### Q2. Ray Worker Pod 掛掉後，Ray 與 KubeRay 分別做什麼？

Ray 負責 Task / Actor runtime recovery，例如偵測 `NODE_DIED` 並依 retry policy 重新執行 Task；KubeRay Operator 則負責維持 RayCluster desired state，例如 Worker Pod 數量不足時重新建立 Worker Pod。
