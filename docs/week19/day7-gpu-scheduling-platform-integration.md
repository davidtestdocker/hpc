# Week19 Day7 — GPU Scheduling Platform Integration

## 本週整合目標

Week19 最後整合成一條完整 GPU scheduling pipeline：

    GPU Workload
        ↓
    PriorityClass
        ↓
    LocalQueue
        ↓
    ClusterQueue
        ↓
    ResourceFlavor
        ↓
    GPU Quota / Admission
        ↓
    Priority / Preemption
        ↓
    JobSet All-or-Nothing
        ↓
    Topology-Aware Scheduling
        ↓
    Kubernetes Scheduler
        ↓
    GPU Node

---

## 1. GPU Time-Sharing

底層：

    1 × NVIDIA L4

GKE Time-Sharing：

    maxSharedClientsPerGpu = 4

Kubernetes 因此看到：

    nvidia.com/gpu = 4

但實際仍然是：

    1 physical GPU
    → 4 schedulable shares

重點：

    GPU share ≠ 4 張實體 GPU

而且單一 Pod 最多 request：

    nvidia.com/gpu: 1

多 share workload 要用：

    multiple Pods × GPU:1

---

## 2. Kueue 的角色

Kueue 不取代 Kubernetes scheduler。

Kueue主要回答：

    「這個 workload 現在能不能進場？」

負責：

    Queue
    Quota
    Admission
    Priority
    Preemption
    ResourceFlavor
    Topology-aware admission

Kubernetes scheduler回答：

    「Pod 最後放在哪個 Node？」

所以：

    Kueue
    → admission layer

    kube-scheduler
    → placement layer

---

## 3. LocalQueue / ClusterQueue / ResourceFlavor

LocalQueue：

    namespace 內 workload 的提交入口

目前：

    gpu-local-queue
        ↓
    gpu-cluster-queue

ClusterQueue：

    cluster-level GPU quota

目前：

    nvidia.com/gpu quota = 4

ResourceFlavor：

    描述「是哪一類資源」

目前：

    l4-timesharing-tas

代表：

    NVIDIA L4
    + GKE Time-Sharing
    + GPU Topology

簡單記：

    LocalQueue
    = 從哪裡排隊

    ClusterQueue
    = 有多少 quota

    ResourceFlavor
    = 要哪一類硬體

---

## 4. GPU Quota / Admission

Kueue 會先算整個 workload 的 resource request。

例如：

    Job A
    3 Pods × GPU:1
    = GPU request 3

ClusterQueue：

    quota = 4

則可以：

    QuotaReserved=True
    Admitted=True

如果另一個 workload 需要：

    2 GPU

但只剩：

    1 quota

則：

    Admitted=False
    Pending

等前一個 workload 完成釋放 quota 後：

    Kueue reevaluate
    ↓
    QuotaReserved
    ↓
    Admitted

---

## 5. Priority / Preemption

建立：

    gpu-low  = 100
    gpu-high = 1000

ClusterQueue：

    withinClusterQueue: LowerPriority

實際驗證：

    Low
    priority 100
    使用 4 / 4 GPU quota

    High
    priority 1000
    需要 2 GPU

結果：

    High quota 不足
    ↓
    Kueue 選 Low 當 victim
    ↓
    Low 被 Preempted / Evicted
    ↓
    Low Admitted=False
    ↓
    High QuotaReserved=True
    ↓
    High Admitted=True

關鍵：

    PriorityClass
    = 誰比較重要

    Preemption Policy
    = 高 priority 是否能把低 priority 擠掉

兩者不是同一件事。

---

## 6. JobSet / Gang Admission

JobSet：

    把多個相關 Kubernetes Jobs
    描述成同一個 distributed workload

例如：

    JobSet
    ├─ launcher
    └─ workers × 3

Kueue 將整個 JobSet 建成：

    1 Workload

因此可以做到：

    All-or-Nothing Admission

實際驗證：

    ClusterQueue quota = 4
    blocker 使用 2
    JobSet 需要 3

當下只有：

    available = 2

結果：

    launcher = Suspended
    workers = Suspended
    Pods = 0

不是：

    先跑 2 個
    剩下再等

釋放 blocker 後：

    整個 JobSet Admitted
    ↓
    launcher + workers 一起啟動

---

## 7. MPI Launcher / Worker

真實 MPI 架構：

    launcher
    └─ mpirun
        ├─ SSH → worker-0
        ├─ SSH → worker-1
        └─ SSH → worker-2

Worker：

    sshd
    ↓
    接收 launcher 啟動 process
    ↓
    執行 MPI rank

實際驗證：

    RANK=0 HOST=mpi-real-worker-0-0
    RANK=1 HOST=mpi-real-worker-1-0
    RANK=2 HOST=mpi-real-worker-2-0

證明：

    launcher
    → 真正執行 mpirun
    → SSH 到 workers
    → 在不同 worker Pods 啟動 MPI processes

---

## 8. SSH / sshd

SSH client：

    ssh
    = 主動連出去

SSH server：

    sshd
    = 接受別人連入

本次：

    launcher
    → ssh client

    workers
    → sshd

SSH 只是：

    MPI process launch mechanism

真正 MPI 啟動後：

    rank ↔ rank

workers 直接進行 distributed communication，
不是所有資料都經過 launcher。

---

## 9. Secret + InitContainer

SSH private key 不放進 Git。

使用：

    Kubernetes Secret

Secret volume：

    read-only

所以採用：

    Secret
        ↓
    initContainer
        ↓
    copy key → emptyDir
        ↓
    chown / chmod
        ↓
    main container non-root

這讓：

    initialization
    → root

    runtime
    → UID 1000

比直接讓 main container 用 root 更合理。

---

## 10. Topology-Aware Scheduling

Topology：

    cluster 資源的位置階層

目前：

    region
    ↓
    zone
    ↓
    hostname

Topology Domain：

    某一層的實際位置

例如：

    zone:
    asia-southeast1-a

    hostname:
    gke-hpc-gpu-sg-gpu-pool-...

ResourceFlavor：

    l4-timesharing-tas
        ↓
    topologyName:
    gke-gpu-topology

---

## 11. TAS Workload

Workload 指定：

    kueue.x-k8s.io/podset-required-topology:
    kubernetes.io/hostname

意思：

    整個 PodSet
    必須位於同一 hostname domain

實際 Kueue Workload：

    topologyRequest:
      required: kubernetes.io/hostname

並產生：

    topologyAssignment

結果：

    domainCount = 1
    podCount = 2

選定：

    gke-hpc-gpu-sg-gpu-pool-...

實際兩個 Pods 也被 scheduler 指派到：

    same hostname

---

## 12. Gang Scheduling vs Topology Scheduling

兩者不要混在一起。

Gang / All-or-Nothing：

    「整組資源夠不夠？」

Topology-Aware：

    「整組資源應該放在哪裡？」

所以流程：

    Workload request
        ↓
    quota / admission
        ↓
    all-or-nothing
        ↓
    topology assignment
        ↓
    actual scheduling

---

## 13. Kueue + JobSet vs Volcano

目前平台：

    JobSet
        ↓
    Kueue
        ↓
    default kube-scheduler

JobSet：

    描述 distributed Jobs

Kueue：

    quota / queue / admission / preemption

kube-scheduler：

    actual Pod placement

Volcano：

    更深入 scheduler layer

典型能力：

    batch scheduling
    gang scheduling
    PodGroup
    queue
    fair-share
    scheduler-level placement

簡化記：

    Kueue
    → workload 能不能進場

    Volcano
    → 更直接控制 Pods 怎麼排

---

## 14. LeaderWorkerSet vs JobSet

JobSet：

    偏 batch / finite workload

適合：

    MPI
    distributed training
    launcher + workers

LeaderWorkerSet：

    偏 leader-worker topology
    與長時間運行 workload

適合：

    distributed inference
    LLM serving

---

## 15. Week19 最終平台

    NVIDIA L4
        ↓
    GKE Time-Sharing ×4
        ↓
    GPU Workload
        ↓
    PriorityClass
        ↓
    LocalQueue
        ↓
    ClusterQueue
        ↓
    ResourceFlavor
    L4 + Time-Sharing + TAS
        ↓
    GPU Quota
        ↓
    Admission
        ↓
    Priority / Preemption
        ↓
    JobSet
        ↓
    All-or-Nothing Admission
        ↓
    Topology Assignment
        ↓
    Kubernetes Scheduler
        ↓
    GPU Node

Distributed workload 可再接：

    launcher
    ↓
    mpirun
    ↓
    workers
    ↓
    MPI / NCCL communication

---

## 16. Repo 整合

GPU scheduling declarative config：

    k8s/gpu-scheduling/
    ├─ priorityclasses.yaml
    ├─ topology.yaml
    ├─ resourceflavor.yaml
    ├─ clusterqueue.yaml
    ├─ localqueue.yaml
    └─ examples/
       └─ jobset-mpi.yaml

核心 YAML 已做：

    kubectl --dry-run=server

驗證。

---

## 17. 驗證限制

目前：

    1 physical GPU node
    1 × NVIDIA L4
    Time-Sharing ×4

因此已真實驗證：

    GPU sharing
    Queue / quota
    Priority / preemption
    JobSet all-or-nothing
    MPI launcher-worker
    hostname-level TAS

尚未真實驗證：

    multi-node GPU placement
    rack-aware placement
    cross-zone TAS
    multi-node NCCL/RDMA performance

因此不能把目前結果宣稱為：

    real multi-node GPU topology benchmark

---

## Interview Review

**Q1：一個 distributed GPU workload 從提交到執行，Kueue、JobSet、ResourceFlavor、scheduler 各自負責什麼？**  
A：JobSet 描述多個相關 Jobs；Kueue負責 queue、quota、admission、priority 與 preemption；ResourceFlavor 描述 GPU 類型與 topology；最後 Kubernetes scheduler 負責實際 Pod-to-Node placement。

**Q2：Gang scheduling 與 Topology-Aware Scheduling 差在哪？**  
A：Gang scheduling解決「整組 workload 是否能一起進場」，避免 partial start；Topology-Aware Scheduling解決「整組資源應放在哪個 topology domain」，降低 distributed communication cost。
