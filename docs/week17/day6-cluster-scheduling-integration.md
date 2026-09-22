<!-- readable-curriculum: 2026-09-22 -->
# Week17 Day6 — 排程層整合

[上一課](<day5-ray-kuberay-distributed-computing.md>) · [本週目錄](README.md) · [下一週](../week18/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

API 接受、Kueue admitted、Pod scheduled、MPI started、工作 completed 是一串不同狀態。每一層都能卡住，必須依症狀定位而不是看到 Pending 就認為缺 GPU。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    elif state == 'submitted' and job['benchmark'] == 'mpi':
        # submitted 只代表已提交；collector 回傳 None 表示尚未取得終態。
        update = main.collect_mpi_jobset(job['result']['jobset_name'])
        if update is None:
            return
        guard()
        main.persist_job_status(job_id, update['status'])
        job.update(update)
        job['finished_at'] = datetime.now(timezone.utc).isoformat()
        guard()
        redis.set(key, json.dumps(job))
    else:
        raise ValueError(f'Unsupported job state: {state}')
    # pipeline 預設使用 MULTI/EXEC，把 queue 清理與 done 標記放在同一 Redis 交易。
    # 此交易不涵蓋上方 PostgreSQL；DB-first 失敗時保留可在下一輪重試的狀態。
    guard()
    with redis.pipeline() as pipe:
        pipe.lrem('job_queue', 0, job_id)
        pipe.lrem('processing_queue', 0, job_id)
        if job['status'] == 'failed':
            pipe.lrem('dead_letter_queue', 0, job_id)
            pipe.rpush('dead_letter_queue', job_id)
        if job['status'] in {'completed', 'failed'}:
            pipe.set(f'worker:done:{job_id}', '1')
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week17/day6-cluster-scheduling-integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：主平台是 CPU MPI rank smoke；Slurm 多 VM 與 Ray 為獨立案例，三個 worker Pods 不代表三台 node。
> **閱讀順序**：先學本文基礎，再讀[Week17 現行對照與檢核](../learning-guide.md#week17)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week17 Day6 — Cluster Scheduling Comparison & Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/pytorch-runtime/templates/ddp-test-job.yaml](../../helm/pytorch-runtime/templates/ddp-test-job.yaml)
- [mpi-multinode.slurm](../../mpi-multinode.slurm)
- [ray-cluster.yaml](../../ray-cluster.yaml)：Ray 叢集
- [ray-job.yaml](../../ray-job.yaml)：Ray task 範例

---

## 今日完成

把 Week17 已實作的 Slurm、Kubernetes、Ray 三種 scheduler 整合成同一套 scheduling model，並實際驗證不同層級的 resource contention 與 Pending 行為。

今日完成：

- 對照 Slurm / Kubernetes / Ray 的排程單位
- 釐清 Node、Pod、Task / Actor 三層資源模型
- 驗證 Kubernetes Pod Pending
- 驗證 Ray Task Unschedulable
- 驗證 Ray Task Pending / Resource Contention
- 對照 Slurm `PD (Resources)`
- 建立完整 HPC / Distributed Scheduling 分層模型

---

## 1. 三種 Scheduler 的定位

### Slurm

主要負責：

- HPC batch scheduling
- Job allocation
- Compute Node resource management
- Queue / Partition / Reservation
- CPU / GPU / Memory allocation

主要排程：

    Job / Task
        ↓
    Compute Node

---

### Kubernetes

主要負責：

- Container orchestration
- Pod scheduling
- Service workload
- Node resource allocation

主要排程：

    Pod
      ↓
    Kubernetes Node

---

### Ray

主要負責：

- Application-level distributed execution
- Python Task scheduling
- Actor scheduling
- Dynamic workload execution
- Distributed resource management

主要排程：

    Task / Actor
         ↓
    Ray Node

---

## 2. Kubernetes + Ray 架構

目前平台：

    GKE hpc-dev
    │
    ├── primary-pool Node
    │   ├── Ray Head Pod
    │   └── Ray Worker Pod
    │
    └── observability-pool Node
        └── Ray Worker Pod

Ray runtime：

    RayCluster hpc-ray
    ├── Head
    ├── Worker 1
    └── Worker 2

兩層 Scheduler：

    Kubernetes Scheduler
        ↓
    決定 Ray Pod 放在哪個 Kubernetes Node

    Ray Scheduler
        ↓
    決定 Task / Actor 使用哪個 Ray Node resource

---

## 3. Kubernetes Resource Contention

Ray Worker 曾出現：

    Pending

Event：

    FailedScheduling
    0/1 nodes are available:
    1 Insufficient cpu

原因：

Kubernetes Scheduler 根據 Pod `requests` 判斷可否放入某個 Node。

Ray Worker request：

    cpu: 500m
    memory: 1Gi

當唯一 Node 沒有足夠剩餘 allocatable CPU 時：

    Worker Pod
        ↓
    Kubernetes Scheduler
        ↓
    No suitable Node
        ↓
    Pending

開啟 observability-pool：

    gcloud container clusters resize hpc-dev \
      --node-pool=observability-pool \
      --num-nodes=1 \
      --zone=asia-east1-a

第二台 Node 出現後：

    Pending Worker
        ↓
    Scheduler 找到可用 Node
        ↓
    Running

---

## 4. Ray Cluster Resource Model

Ray 狀態：

    Active Ray Nodes: 3

    Total:
    CPU: 3
    Memory: 6 GiB
    Object Store: ~1.51 GiB

實際分布：

    Ray Head     = 1 CPU
    Ray Worker A = 1 CPU
    Ray Worker B = 1 CPU

總共：

    3 CPU

重要：

    Cluster total CPU = 3

不代表：

    單一 Task 可以要求 3 CPU

Ray Task 必須由單一 Ray Node 滿足其 resource request。

---

## 5. Ray Unschedulable Request

測試：

    @ray.remote(num_cpus=2)
    def hold(task_id):
        ...

目前每個 Ray Node 都只有：

    1 CPU

因此：

    Task requires 2 CPU
           ↓
    Ray checks all nodes
           ↓
    No single node has 2 CPU
           ↓
    Unschedulable

實際訊息：

    No available node types can fulfill resource request {'CPU': 2.0}

雖然整個 Cluster：

    1 + 1 + 1 = 3 CPU

但不能把一個 Task 拆成：

    Node A 0.7 CPU
    Node B 0.7 CPU
    Node C 0.6 CPU

一個普通 Ray Task 仍會在單一 Ray Node 上執行。

---

## 6. Ray Resource Contention

第二個測試：

    @ray.remote(num_cpus=1)
    def hold(task_id):
        ...

一次提交 4 個 Task。

Cluster：

    3 CPU

每個 Task：

    1 CPU

因此同時最多：

    3 Tasks

實際狀態：

    Total Usage:
    3.0/3.0 CPU

    Total Demands:
    {'CPU': 1.0}: 1+ pending tasks/actors

代表：

    Task 0 → Running
    Task 1 → Running
    Task 2 → Running

    Task 3 → Pending

原因不是 Task 規格非法，而是：

    所有可用 Ray CPU 已被占用

當前面 Task 完成：

    CPU released
        ↓
    Pending Task scheduled
        ↓
    Running

---

## 7. Unschedulable vs Pending

### Unschedulable

例如：

    Task requires 2 CPU

但：

    Node A = 1 CPU
    Node B = 1 CPU
    Node C = 1 CPU

結果：

    No suitable Ray Node exists

即使等待也不會自然解決，除非增加或改變 node resources。

---

### Resource Pending

例如：

    Task requires 1 CPU

每個 Node 都可以滿足，但當下全部 CPU 已被使用。

結果：

    Pending

等其他 Task 完成後即可被排程。

---

## 8. Slurm Resource Contention

Week17 Day4 已驗證：

    Job A → Running
    Job B → PD (Resources)

代表：

    Slurm Scheduler
        ↓
    Job resource request
        ↓
    Compute resources currently occupied
        ↓
    Job Pending

當資源釋放：

    Pending Job
        ↓
    Allocated
        ↓
    Running

這與 Ray resource contention 概念相近，但發生在不同 scheduling layer。

---

## 9. 三種 Pending 對照

### Slurm

    Job
      ↓
    Slurm Scheduler
      ↓
    Compute Node resource unavailable
      ↓
    PD (Resources)

---

### Kubernetes

    Pod
      ↓
    Kubernetes Scheduler
      ↓
    No Node currently satisfies Pod requests
      ↓
    Pending

---

### Ray

    Task / Actor
        ↓
    Ray Scheduler
        ↓
    Ray resource unavailable
        ↓
    Pending

---

## 10. Scheduler 正式對照

| 項目 | Slurm | Kubernetes | Ray |
|---|---|---|---|
| 主要排程單位 | Job / Task | Pod | Task / Actor |
| 主要資源對象 | Compute Node | Kubernetes Node | Ray Node |
| CPU / GPU Resource | 有 | 有 | 有 |
| Batch Queue | 強 | 可透過 Job / Kueue 等 | Runtime task queue |
| Service Orchestration | 非主要用途 | 強 | 非主要用途 |
| MPI / HPC | 強 | 可執行 | 可整合 |
| Dynamic Python Task | 非主要模型 | 無 application-level task model | 強 |
| Stateful Actor | 無 Ray Actor 模型 | 無 | 有 |
| Pod Scheduling | 無 | 有 | 無 |

---

## 11. Slurm + Distributed Runtime

典型 HPC 架構：

    User
      ↓
    sbatch
      ↓
    Slurm Scheduler
      ↓
    Allocate Compute Nodes
      ↓
    MPI / NCCL / Ray
      ↓
    Distributed Processes / Tasks

例如：

    Slurm
      ↓
    allocate 4 nodes
      ↓
    launch Ray cluster
      ↓
    Ray schedules hundreds of tasks

Slurm 與 Ray 不一定互斥。

---

## 12. Kubernetes + Ray

目前平台實際架構：

    User / RayJob
          ↓
    Kubernetes API
          ↓
    KubeRay Operator
          ↓
    RayCluster Pods
          ↓
    Kubernetes Scheduler
          ↓
    Kubernetes Nodes
          ↓
    Ray Runtime
          ↓
    Tasks / Actors

因此：

    Kubernetes
    = 管 Ray 執行環境

    Ray
    = 管 distributed application execution

---

## 13. HPC / Distributed Scheduling 分層模型

最終模型：

    User / CI / API
          ↓
    Workload Submission
          ↓
    +-----------------------------+
    | Cluster Scheduler           |
    | Slurm / Kubernetes          |
    +-----------------------------+
          ↓
    Compute / Pod Allocation
          ↓
    +-----------------------------+
    | Distributed Runtime         |
    | Ray / MPI / NCCL            |
    +-----------------------------+
          ↓
    Tasks / Actors / Processes
          ↓
    CPU / GPU / Network

不同工具負責不同層級，不能只因為都會「排程」就視為同一種 scheduler。

---

## 驗證結果

Kubernetes：

    Nodes: 2

Ray：

    Active Ray Nodes: 3
    CPU: 3
    Memory: 6 GiB

Ray Unschedulable：

    Task requires 2 CPU
    No single Ray Node has 2 CPU

    Result:
    No available node types can fulfill resource request

Ray Resource Contention：

    4 Tasks
    1 CPU each

    Total Usage:
    3.0/3.0 CPU

    Total Demands:
    {'CPU': 1.0}: 1+ pending tasks/actors

成功驗證：

    Kubernetes Pod scheduling
    Ray Task scheduling
    Resource contention
    Unschedulable resource request
    Scheduler layering

---

## 限制

目前環境：

- 2 個 Kubernetes Nodes
- 3 個 Ray Nodes
- 每個 Ray Node 1 CPU
- 未啟用大型 Ray autoscaling
- 未實作 Kubernetes Kueue / Volcano
- 未整合 Slurm 與 Ray 成同一個實體 cluster
- 未測試 GPU scheduler contention
- 未測試 gang scheduling

Day6 主要驗證 scheduling architecture 與 resource behavior，而不是大規模 production scheduler performance。

---

## Interview Review

### Q1：Kubernetes Pod Pending 和 Ray Task Pending 有什麼差別？

Kubernetes Pod Pending 是 Pod 找不到可滿足 requests 的 Kubernetes Node；Ray Task Pending 是 RayCluster 已存在且 Pod 已 Running，但 Task 當下拿不到所需 Ray resource。

### Q2：為什麼 Ray Cluster 總共有 3 CPU，但 `num_cpus=2` 的 Task 仍可能無法排程？

因為單一 Task 必須由單一 Ray Node 滿足 resource request。若 3 個 Ray Nodes 各只有 1 CPU，即使 cluster total 為 3 CPU，也沒有任何單一 node 能提供 2 CPU。
