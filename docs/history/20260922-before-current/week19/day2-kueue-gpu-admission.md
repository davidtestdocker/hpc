<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](<../../../learning-guide.md#week19>)及[對應現行入口](<../../../runbooks/automatic-worker.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day2 — Kueue GPU Admission：ResourceFlavor / ClusterQueue / LocalQueue

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/gpu-scheduling/clusterqueue.yaml](<../../../../k8s/gpu-scheduling/clusterqueue.yaml>)
- [k8s/gpu-scheduling/localqueue.yaml](<../../../../k8s/gpu-scheduling/localqueue.yaml>)
- [k8s/gpu-scheduling/resourceflavor.yaml](<../../../../k8s/gpu-scheduling/resourceflavor.yaml>)

---

## 今日完成內容

今天正式把 GPU workload 從：

    直接交給 Kubernetes Scheduler

改成：

    先進 Kueue
    ↓
    檢查 quota
    ↓
    通過 admission
    ↓
    再交給 Kubernetes Scheduler

本次完成：

- 安裝 Kueue
- 建立 ResourceFlavor
- 建立 ClusterQueue
- 建立 LocalQueue
- 建立 GPU Job
- 驗證 Workload 自動建立
- 驗證 GPU quota reservation
- 驗證 admission
- 驗證 Job 正式執行

---

## 1. Kueue 是什麼

Kueue 不是 GPU 專用工具。

它本質上是：

    Kubernetes workload queueing
    quota management
    admission control

可以管理：

    CPU
    Memory
    GPU
    TPU
    Extended Resources

Kueue 的核心角色：

    決定 workload 現在有沒有資格開始跑

而 Kubernetes Scheduler：

    決定 workload 實際排到哪個 node

所以：

    Kueue
    = admission / queue

    Kubernetes Scheduler
    = placement

---

## 2. 一般 Kubernetes Scheduling

沒有 Kueue 時：

    User submits Job
        ↓
    Kubernetes Scheduler
        ↓
    有資源
    → Running

    沒資源
    → Pending

這種模式沒有額外的：

    queue
    team quota
    admission
    fairness

---

## 3. 加入 Kueue 後

流程變成：

    User submits Job
        ↓
    LocalQueue
        ↓
    ClusterQueue
        ↓
    ResourceFlavor
        ↓
    Quota check
        ↓
    Admission
        ↓
    Kubernetes Scheduler
        ↓
    GPU Node

---

## 4. Kueue Installation

確認原本 cluster：

    kubectl get crd | grep kueue
    kubectl get pods -A | grep kueue

結果：

    no existing Kueue

因此安裝 Kueue。

安裝後 controller 一開始：

    Pending

原因：

    0/1 nodes are available:
    node had untolerated taint

GPU node：

    nvidia.com/gpu=present:NoSchedule

Kueue controller 沒有對應 toleration，
所以排不上唯一 node。

移除 node taint 後：

    kueue-controller-manager
    → Running

驗證：

    kubectl wait deploy/kueue-controller-manager \
      -n kueue-system \
      --for=condition=available \
      --timeout=2m

結果：

    condition met

---

## 5. Kueue 三個核心物件

今天主要建立：

    ResourceFlavor
    ClusterQueue
    LocalQueue

關係：

    Workload
        ↓
    LocalQueue
        ↓
    ClusterQueue
        ↓
    ResourceFlavor

---

## 6. ResourceFlavor

ResourceFlavor 用來描述：

    這是哪一類資源

目前環境：

    NVIDIA L4
    GKE Time-Slicing

因此建立：

    l4-timesharing

設定：

    nodeLabels:
      cloud.google.com/gke-accelerator: nvidia-l4
      cloud.google.com/gke-gpu-sharing-strategy: time-sharing

意思：

    使用這個 flavor 的 workload
    應該排到：

    NVIDIA L4
    +
    Time-Sharing GPU node

---

## 7. ResourceFlavor API Version

最初使用：

    kueue.x-k8s.io/v1beta1

Kueue warning：

    This version is deprecated.
    Use v1beta2 instead.

實際儲存：

    API Version:
    kueue.x-k8s.io/v1beta2

因此後續改用：

    apiVersion: kueue.x-k8s.io/v1beta2

---

## 8. ClusterQueue

建立：

    gpu-cluster-queue

用途：

    cluster-wide GPU quota pool

目前 GKE：

    1 physical NVIDIA L4
        ↓
    Time-Slicing
        ↓
    4 schedulable GPU shares

所以設定：

    nominalQuota: 4

資源：

    nvidia.com/gpu

Flavor：

    l4-timesharing

---

## 9. ClusterQueue Configuration

核心設定：

    resourceGroups:
      - coveredResources:
          - nvidia.com/gpu
        flavors:
          - name: l4-timesharing
            resources:
              - name: nvidia.com/gpu
                nominalQuota: 4

意思：

    gpu-cluster-queue
        ↓
    管理 nvidia.com/gpu
        ↓
    使用 l4-timesharing
        ↓
    quota = 4

---

## 10. ClusterQueue Status

驗證：

    kubectl describe clusterqueue gpu-cluster-queue

結果：

    Active:
    True

Message：

    Can admit new workloads

Quota：

    nvidia.com/gpu
    Nominal Quota: 4

當下：

    Admitted Workloads: 0
    Pending Workloads: 0
    GPU Usage: 0

代表 ClusterQueue 正常可用。

---

## 11. LocalQueue

建立：

    gpu-local-queue

Namespace：

    hpc-platform-dev

連到：

    gpu-cluster-queue

設定：

    spec:
      clusterQueue: gpu-cluster-queue

---

## 12. LocalQueue 的角色

LocalQueue 是：

    namespace 裡 workload 使用的 queue entrance

目前：

    hpc-platform-dev
        ↓
    gpu-local-queue
        ↓
    gpu-cluster-queue

所以使用者不需要直接操作 ClusterQueue。

---

## 13. LocalQueue Status

驗證：

    kubectl describe localqueue gpu-local-queue \
      -n hpc-platform-dev

結果：

    Active:
    True

Message：

    Can submit new workloads to localQueue

Cluster Queue：

    gpu-cluster-queue

GPU usage：

    0

所以 LocalQueue 已正常連接 ClusterQueue。

---

## 14. 完整 Queue Architecture

目前：

    hpc-platform-dev Job
        ↓
    LocalQueue
    gpu-local-queue
        ↓
    ClusterQueue
    gpu-cluster-queue
        ↓
    ResourceFlavor
    l4-timesharing
        ↓
    GPU quota = 4
        ↓
    GKE Time-Slicing L4

---

## 15. 建立 Kueue GPU Job

建立：

    kueue-gpu-test

Job label：

    kueue.x-k8s.io/queue-name: gpu-local-queue

代表：

    這個 Job
    要提交到 gpu-local-queue

---

## 16. suspend: true

Job：

    suspend: true

意思：

    Job 一開始先不要直接執行

流程：

    Job created
        ↓
    suspended
        ↓
    Kueue checks quota
        ↓
    admitted
        ↓
    Kueue unsuspends Job
        ↓
    Kubernetes starts Pod

這就是 admission control。

---

## 17. GPU Resource Request

Job：

    resources:
      limits:
        nvidia.com/gpu: 1

所以 workload 需要：

    1 GPU share

Kueue 必須先確認：

    gpu-cluster-queue

是否還有至少：

    1 GPU quota

---

## 18. Kueue Workload

建立 Job 後，
Kueue 自動建立：

    Workload

名稱：

    job-kueue-gpu-test-2fa5e

Workload 是 Kueue 用來追蹤：

    resource request
    queue
    quota reservation
    admission
    execution state

的核心物件。

---

## 19. Queue Reservation

Workload：

    QUEUE:
    gpu-local-queue

    RESERVED IN:
    gpu-cluster-queue

代表：

    Job 從 LocalQueue 進入
    ClusterQueue 成功替它保留 quota

---

## 20. ResourceFlavor Assignment

Workload Status：

    Flavors:
      nvidia.com/gpu:
      l4-timesharing

代表 Kueue 幫這個 workload 選擇：

    l4-timesharing

這個 ResourceFlavor。

---

## 21. Resource Usage

Workload：

    Resource Usage:
      nvidia.com/gpu: 1

代表：

    此 workload
    reservation = 1 GPU share

ClusterQueue quota：

    4

所以：

    total quota = 4
    current reservation = 1

理論剩餘：

    3 GPU shares

---

## 22. QuotaReserved

Workload Condition：

    Type:
    QuotaReserved

    Status:
    True

Message：

    Quota reserved in ClusterQueue gpu-cluster-queue

代表：

    Kueue 已成功替 workload 保留資源。

Event：

    QuotaReserved

wait time：

    1s

---

## 23. Admitted

接著：

    Type:
    Admitted

    Status:
    True

Message：

    The workload is admitted

代表：

    workload 通過 Kueue admission

現在才有資格執行。

---

## 24. PodsReady

最後：

    Type:
    PodsReady

    Status:
    True

Message：

    All pods reached readiness and the workload is running

代表：

    admission
    ↓
    Job unsuspended
    ↓
    Pod scheduled
    ↓
    workload running

---

## 25. Job Result

Job：

    kueue-gpu-test

狀態：

    Running

所以完整流程成功：

    Job submitted
        ↓
    LocalQueue
        ↓
    Workload created
        ↓
    ClusterQueue quota reserved
        ↓
    ResourceFlavor assigned
        ↓
    Admitted=True
        ↓
    Job starts
        ↓
    Running

---

## 26. 與 Time-Slicing 的整合

Week19 Day1：

    1 physical L4
        ↓
    GKE Time-Slicing
        ↓
    4 schedulable GPU shares

Week19 Day2：

    4 GPU shares
        ↓
    Kueue ClusterQueue
        ↓
    quota = 4
        ↓
    workload admission

所以現在平台變成：

    Physical GPU
        ↓
    GPU Sharing
        ↓
    Scheduler Resource
        ↓
    Kueue Quota
        ↓
    Workload Admission

---

## 27. Kueue 與 Kubernetes Scheduler 的差別

Kueue：

    現在輪不輪得到你跑？

Kubernetes Scheduler：

    你要跑在哪台 node？

所以：

    Kueue
    !=
    Kubernetes Scheduler

而是：

    Kueue Admission
        ↓
    Kubernetes Scheduling

---

## 28. Multi-Tenant 意義

如果沒有 Kueue：

    Team A
    → submit many Jobs
    → directly compete for GPU

加入 Kueue 後：

    Team A
    Team B
       ↓
    Queues
       ↓
    Quota
       ↓
    Admission
       ↓
    GPU

後續可以加入：

    team quota
    priority
    preemption
    cohort
    borrowing

這些就是後面 Day3 / Day4 的重點。

---

## 今日結論

Day2 把：

    GPU sharing

進一步提升成：

    GPU queue + quota + admission

目前完整架構：

    User submits GPU Job
        ↓
    LocalQueue
    gpu-local-queue
        ↓
    ClusterQueue
    gpu-cluster-queue
        ↓
    ResourceFlavor
    l4-timesharing
        ↓
    GPU quota = 4
        ↓
    Admission
        ↓
    Kubernetes Scheduler
        ↓
    GKE Time-Slicing L4

本次真實驗證：

    ClusterQueue Active=True
    LocalQueue Active=True
    Workload automatically created
    QuotaReserved=True
    Admitted=True
    PodsReady=True
    ResourceFlavor=l4-timesharing
    GPU usage=1
    Job=Running

---

## Interview Review

**Q1：Kueue 跟 Kubernetes Scheduler 最大差別是什麼？**  
A：Kueue 負責 workload queue、quota 與 admission，決定 workload 現在是否有資格開始跑；Kubernetes Scheduler 則負責 workload 通過 admission 後實際放到哪個 node。

**Q2：ResourceFlavor、ClusterQueue、LocalQueue 分別是什麼？**  
A：ResourceFlavor 描述資源類型，例如 L4 Time-Slicing；ClusterQueue 管理 cluster-wide quota；LocalQueue 則是 namespace 內使用者提交 workload 的 queue 入口。
