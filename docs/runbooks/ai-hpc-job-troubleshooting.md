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

    kubectl get workload -A
    kubectl describe workload <name> -n <namespace>

重點：

    QuotaReserved
    Admitted
    Events

可能原因：

    ClusterQueue quota 不足
    ResourceFlavor 不符合
    TAS 找不到 topology domain

如果 Job 還是 suspended 且 Pod 尚未建立：

    問題仍在 Kueue admission layer

---

### Workload 已 Admission，但 Pod Pending

檢查：

    kubectl describe pod <pod> -n <namespace>

重點：

    FailedScheduling

常見原因：

    Insufficient cpu
    Insufficient memory
    Insufficient nvidia.com/gpu
    untolerated taint
    nodeSelector / affinity mismatch
    Node SchedulingDisabled

此時問題位於：

    Kubernetes scheduler / placement layer

---

## 2. Ray Resource Troubleshooting

Kubernetes Pod 全部 Running，不代表 Ray Task 一定能執行。

檢查：

    ray status

以及：

    ray.cluster_resources()
    ray.available_resources()

實測案例：

Ray Cluster：

    CPU = 3
    GPU = 0

Ray Task：

    CPU = 1
    GPU = 1

Ray scheduler 顯示：

    {'CPU': 1.0, 'GPU': 1.0}: 1+ pending tasks/actors

結論：

    Kubernetes layer = Healthy
    Ray cluster Pods = Running
    Ray scheduler = Resource mismatch

因此：

    Pod Running != Ray Task schedulable

---

## 3. Ray Worker Failure Recovery

實測 long_task：

    attempt_number: 0
    state: RUNNING

Task 原本執行於：

    Ray Worker Pod A

刪除 Worker Pod A 後：

    attempt_number: 0
    state: FAILED
    error_type: NODE_DIED

Task 設定：

    max_retries=2

並使用 soft node affinity：

    soft=True

Ray 自動重新排程：

    attempt_number: 1
    state: RUNNING

Task 改到另一個 Ray node / Ray Pod 執行。

Recovery flow：

    Worker Pod failure
    ↓
    Ray detects NODE_DIED
    ↓
    Task attempt 0 FAILED
    ↓
    max_retries permits retry
    ↓
    Ray scheduler selects another available Ray node
    ↓
    Task attempt 1 RUNNING

另外：

    KubeRay Operator
    ↓
    發現 RayCluster Worker 數量不足
    ↓
    自動建立新的 Worker Pod

這是兩套不同的 recovery：

    Ray
    = Task-level recovery

    KubeRay
    = Ray Worker Pod / cluster desired-state recovery

---

## 4. MPI / JobSet vs Ray Recovery

MPI / JobSet：

    Worker failure
    ↓
    Distributed MPI world may become invalid
    ↓
    Child Job failure
    ↓
    RestartJobSet
    ↓
    Recreate whole distributed workload

Ray：

    Worker failure
    ↓
    Individual Task fails
    ↓
    Retry policy
    ↓
    Task may run on another Ray node

重點：

    MPI / JobSet
    = whole-workload recovery

    Ray
    = fine-grained task / actor recovery

---

## 5. Slurm Troubleshooting

### Cluster / Node Layer

檢查：

    sinfo

如果看到：

    down
    drain

再查：

    scontrol show node <node>

實測案例：

    State=DOWN+NOT_RESPONDING
    Reason=Not responding

排障方向：

    slurmd process
    network
    VM / physical server
    Slurm node configuration

---

### Job Layer

檢查：

    squeue

不要只看：

    PD / PENDING

要看：

    NODELIST(REASON)

實測案例：

    Nodes required for job are DOWN, DRAINED
    or reserved for jobs in higher priority partitions

再深入：

    scontrol show job <job-id>

可以確認：

    JobState
    Reason
    Partition
    NumNodes
    NumCPUs
    ReqNodeList

---

## 6. Cross-Platform Failure Domains

同樣是「Job 沒跑」，故障層可能完全不同。

    AI/HPC Job Problem
    │
    ├── Kueue
    │   └── Admission / Quota / Flavor / TAS
    │
    ├── Kubernetes Scheduler
    │   └── CPU / Memory / GPU / Taint / Affinity
    │
    ├── Kubernetes Node
    │   └── Ready / NotReady / cordon / runtime
    │
    ├── Ray Scheduler
    │   └── Task / Actor resource mismatch
    │
    ├── Slurm Scheduler
    │   └── Partition / Pending Reason / Node state
    │
    ├── GPU Runtime
    │   └── NVIDIA device / CUDA / memory
    │
    ├── Distributed Runtime
    │   └── Ray / MPI / DDP / NCCL
    │
    ├── Network
    │   └── DNS / MTU / TCP / RDMA / NCCL transport
    │
    └── Application
        └── Training / inference / code logic

核心原則：

> 先定位 failure domain，再使用該層工具，不要看到 Job 卡住就直接查 application logs。
