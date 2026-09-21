# Week17 Day5 — Ray / KubeRay Distributed Computing

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [ray-cluster.yaml](../../ray-cluster.yaml)：Ray 叢集
- [ray-job.yaml](../../ray-job.yaml)：Ray task 範例

---

## 今日完成

在既有 GKE `hpc-dev` 上建立正式 KubeRay / Ray distributed computing capability：

- 安裝 KubeRay Operator
- 建立 `RayCluster`
- 建立 Ray Head + 2 Ray Workers
- 驗證 Ray Cluster resources
- 執行 Ray distributed Tasks
- 實作 Ray Actor
- 使用 `RayJob` 正式提交 distributed workload
- 驗證跨 Kubernetes Node 的 Ray Cluster topology

---

## 1. KubeRay Operator

使用 Helm 安裝：

    helm repo add kuberay https://ray-project.github.io/kuberay-helm/
    helm repo update

    kubectl create namespace kuberay-system

    helm install kuberay-operator \
      kuberay/kuberay-operator \
      --namespace kuberay-system

驗證：

    kubectl get pods -n kuberay-system
    kubectl get crd | grep ray

建立的主要 CRD：

    rayclusters.ray.io
    rayjobs.ray.io
    rayservices.ray.io
    raycronjobs.ray.io

Operator 控制流程：

    RayCluster CR
         ↓
    KubeRay Operator
         ↓
    Ray Head / Worker Pods

Helm 本身不直接執行 Ray workload，而是安裝 Kubernetes resources，其中 KubeRay Operator 由 Deployment → ReplicaSet → Pod 管理。

---

## 2. RayCluster

建立：

    kind: RayCluster
    name: hpc-ray
    namespace: ray-system

RayCluster topology：

    GKE hpc-dev
    │
    ├── primary-pool Node
    │   ├── Ray Head Pod
    │   └── Ray Worker Pod
    │
    └── observability-pool Node
        └── Ray Worker Pod

RayCluster：

    hpc-ray
    ├── Head
    ├── Worker 1
    └── Worker 2

Kubernetes 與 Ray 是兩層 scheduler：

    Kubernetes Scheduler
        ↓
    決定 Ray Pod 放在哪個 K8s Node

    Ray Scheduler
        ↓
    決定 Python Task / Actor 使用哪個 Ray node resource

---

## 3. Kubernetes CPU Scheduling

第二個 Worker 最初 Pending：

    FailedScheduling
    0/1 nodes are available:
    1 Insufficient cpu

原因不是 CPU 被平均切分，而是 Kubernetes 根據 Pod CPU requests 做 scheduling。

開回既有 observability-pool：

    gcloud container clusters resize hpc-dev \
      --node-pool=observability-pool \
      --num-nodes=1 \
      --zone=asia-east1-a

之後第二個 Ray Worker 成功排到 observability-pool。

---

## 4. Ray Cluster Resources

在 Head 執行：

    ray status

結果：

    Active Ray nodes: 3
    CPU: 3.0
    Memory: 6.00 GiB
    Object Store Memory: 1.51 GiB

Python 驗證：

    ray.cluster_resources()
    ray.available_resources()

Ray Cluster 認得：

    node:10.68.0.23
    node:10.68.0.24
    node:10.68.1.2

並使用：

    node:__internal_head__

標識 Ray Head。

### Object Store

Ray 使用 distributed object store 儲存 Task / Actor 之間需要共享的物件。

概念：

    Task A
       ↓
    Ray Object Store
       ↓
    Task B

---

## 5. Ray Task

核心寫法：

    @ray.remote(num_cpus=1)
    def work(task_id):
        ...

提交：

    future = work.remote(1)

取得結果：

    result = ray.get(future)

一次提交多個：

    futures = [work.remote(i) for i in range(6)]
    results = ray.get(futures)

`num_cpus=1` 表示每個 Task 執行期間需要 1 個 Ray CPU resource。

目前 Cluster 有 3 CPU，因此最多可以同時容納 3 個這類 Task。

但 Ray 不保證平均分散 Task。

短 Task 可能全部被同一個 Ray Worker 快速依序執行：

    Task 0 → Worker A
    Task 1 → Worker A
    Task 2 → Worker A
    ...

較長 Task 佔住 CPU 時，Ray 才會利用其他可用 node resources。

因此：

    Ray scheduler = resource-aware scheduling

不是：

    round-robin / 強制平均分配

---

## 6. Ray Actor

Task：

    function
    ↓
    執行一次
    ↓
    完成

Actor：

    remote object
    ↓
    可以保存 state
    ↓
    可以反覆呼叫 methods

範例：

    @ray.remote(num_cpus=1)
    class Counter:
        def __init__(self):
            self.value = 0

        def increment(self):
            self.value += 1
            return self.value

建立：

    counter = Counter.remote()

呼叫：

    ray.get(counter.increment.remote())

同一 Actor 的 state 可以持續：

    0 → 1 → 2 → 3 → 4 → 5

普通 Actor 並非永久存在，預設生命週期會受到 owner / driver 影響。

若要跨 driver 存活，可使用 detached actor：

    Counter.options(
        name="counter",
        lifetime="detached"
    ).remote()

---

## 7. RayJob

手動：

    kubectl exec
    ↓
    python script

可以測試，但不是正式 workload submission 方式。

KubeRay 提供：

    RayJob

使用既有：

    RayCluster hpc-ray

提交 distributed workload。

流程：

    ray-job.yaml
        ↓
    Kubernetes API
        ↓
    KubeRay RayJob Controller
        ↓
    Kubernetes Submitter Job
        ↓
    Ray Jobs API
        ↓
    hpc-ray
        ↓
    Ray Tasks

RayJob 狀態：

    JOB STATUS: SUCCEEDED
    DEPLOYMENT STATUS: Complete
    RAY CLUSTER NAME: hpc-ray

RayJob 建立：

    hpc-ray-job-r58wf

此 Pod 是 Submitter Pod，不是 Ray Worker。

Ray Tasks 並不會各自變成 Kubernetes Pod。

架構：

    Kubernetes
    ├── Ray Head Pod
    ├── Ray Worker Pod
    ├── Ray Worker Pod
    └── RayJob Submitter Pod

    Ray Runtime
    ├── Task 0
    ├── Task 1
    ├── Task 2
    ├── Task 3
    ├── Task 4
    └── Task 5

---

## 8. RayCluster 與 RayJob

RayCluster：

    長期存在的 distributed compute cluster

RayJob：

    提交到 RayCluster 的一次性 workload

可以理解為：

    RayCluster = Compute Platform
    RayJob     = Workload

---

## 9. Ray 與 Slurm 的定位

Slurm：

    Cluster / Node resource allocation
    Batch Job scheduling
    Queue / Partition / Reservation
    HPC workload management

Ray：

    Application-level distributed runtime
    Dynamic Task scheduling
    Actor
    Object Store
    Python distributed execution

兩者不是完全互斥。

典型概念：

    Infrastructure Scheduler
        ↓
    分配 machines/resources
        ↓
    Ray Runtime
        ↓
    動態執行 Tasks / Actors

在 Kubernetes 環境：

    Kubernetes
        ↓
    Ray Head / Worker Pods
        ↓
    Ray Runtime
        ↓
    Tasks / Actors

---

## 驗證結果

KubeRay Operator：

    Running

RayCluster：

    hpc-ray
    Head: 1
    Workers: 2
    Ready Workers: 2

Ray resources：

    CPU: 3
    Memory: 6 GiB
    Object Store: ~1.51 GiB

Ray Task：

    成功執行 distributed tasks

Ray Actor：

    成功保存並更新 Actor state

RayJob：

    JOB STATUS: SUCCEEDED
    DEPLOYMENT STATUS: Complete

因此已完成：

    Kubernetes
        ↓
    KubeRay Operator
        ↓
    RayCluster
        ↓
    RayJob
        ↓
    Distributed Tasks / Actors

---

## 限制

目前 RayCluster 雖跨兩台 Kubernetes Nodes，但資源規模仍屬小型 CPU lab。

尚未驗證：

- 大規模 Ray autoscaling
- GPU Ray Workers
- Placement Groups
- Ray Data / Ray Train
- Node failure / Actor recovery
- 大型 distributed object transfer performance

本日驗證重點為 KubeRay control plane、Ray runtime、Task/Actor programming model 與 RayJob workload submission。

---

## Interview Review

### Q1：Kubernetes Scheduler 和 Ray Scheduler 有什麼差別？

Kubernetes Scheduler 負責把 Ray Head / Worker Pods 放到 Kubernetes Nodes；Ray Scheduler 則在 RayCluster 內根據 Ray resources 分配 Tasks / Actors。

### Q2：Ray Task 和 Actor 的主要差異？

Task 是一次性的 remote function；Actor 是可保存 state 並被反覆呼叫的 remote object，普通 Actor 預設不代表永久存在。
