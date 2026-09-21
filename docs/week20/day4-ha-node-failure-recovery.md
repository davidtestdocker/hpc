# Week20 Day4 — HA / Node Failure / Distributed Job Recovery

> 2026-09-21 新實測見 [平台修復與驗收](../demo/platform-recovery-20260921.md)：controller／Redis 恢復成功、新 MPI JobSet Completed；舊 MPI TAS placement 恢復被 reclaimablePods webhook 擋住。本文以下保留原始實驗，不把新工作成功當成舊工作恢復。

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/gpu-scheduling/examples/jobset-mpi.yaml](../../k8s/gpu-scheduling/examples/jobset-mpi.yaml)：固定名稱的 MPI JobSet 實驗
- [k8s/recovery/gpu-node-failure-test.yaml](../../k8s/recovery/gpu-node-failure-test.yaml)

---

## 今天平台增加了什麼

今天把平台補上實際的故障與恢復驗證：

- GPU Node 無法接受新 workload 時的 Kueue / TAS 行為
- GKE Node Auto Repair 與真正 HA 的差異
- MPI distributed job 的 worker failure
- JobSet `failurePolicy`
- Distributed workload 整組 restart / recovery

---

## 1. HA / Self-Healing / Failover

### HA

High Availability 的重點不是「永遠不壞」，而是：

    component failure
    ↓
    failure detection
    ↓
    recovery / failover
    ↓
    service restored

### Self-Healing

Controller 發現實際狀態與 desired state 不一致，自動重新收斂。

### Failover

原本的執行位置失效後，把 workload 移到其他可用資源。

目前平台只有：

    GPU Node = 1

所以沒有真正的 worker-node failover。

---

## 2. cordon

`cordon`：

    kubectl cordon <node>

代表：

    Node 還是 Ready
    ↓
    SchedulingDisabled
    ↓
    現有 Pod 繼續跑
    ↓
    新 Pod 不允許排入

它常用於：

- Node maintenance
- OS / kernel upgrade
- Hardware maintenance
- Node 下線前準備

它不等於真正的 Node failure。

---

## 3. Kueue TAS 與不可排程 Node

將唯一 GPU Node cordon 後，提交 GPU workload。

Kueue Event：

    couldn't assign flavors to pod set main:
    no topology domains at level: kubernetes.io/hostname

原因：

    唯一 GPU Node
    ↓
    cordon
    ↓
    Node 無法接受新 Pod
    ↓
    TAS 找不到可用 hostname placement
    ↓
    Workload 不 Admission
    ↓
    Job 維持 Suspended
    ↓
    Pod 不會建立

恢復 Node：

    kubectl uncordon "$NODE"

之後 Kueue 自動重新評估：

    Node schedulable
    ↓
    TAS 找到可用 Node
    ↓
    QuotaReserved=True
    ↓
    Admitted=True
    ↓
    Job 建立 Pod

重點：

> Kueue TAS 可以在 Pod 建立以前就發現沒有合法的 topology placement。

---

## 4. GKE Auto Repair

目前 GPU node pool：

    initialNodeCount: 1
    autoRepair: true
    autoUpgrade: true

`Auto Repair=true`：

    Node failure
    ↓
    GKE 嘗試修復 / 重建 Node

但：

    Auto Repair != HA

因為目前只有一台 GPU Node。

如果它真的掛掉：

    GPU Node failure
    ↓
    沒有第二台 GPU Node
    ↓
    workload 中斷
    ↓
    等 GKE repair / recreate
    ↓
    Node 回來後才能恢復

真正 node-level HA 需要：

    GPU Node A
    GPU Node B
    GPU Node C

    A failure
    ↓
    workload reschedule / failover
    ↓
    B / C 接手

---

## 5. 修正 Kueue Resource Model

原本 ClusterQueue 只管理：

    nvidia.com/gpu

但 MPI launcher / workers 是 CPU workload，因此 Kueue TAS 無法替它們分配 ResourceFlavor：

    failed to assign flavors to pod set launcher:
    no TAS flavor assigned

修正：

    ClusterQueue
    └── l4-timesharing-tas
        ├── cpu quota = 3
        └── nvidia.com/gpu quota = 4

Node allocatable：

    CPU    = 3920m
    GPU    = 4 shares

保留部分 CPU 給 system controller，因此 batch CPU quota 設為 3 CPU。

MPI：

    launcher = 250m CPU
    worker × 3 = 750m CPU

總需求：

    1 CPU

修正後：

    MPI request CPU
    ↓
    Kueue ResourceFlavor
    ↓
    TAS placement
    ↓
    Workload Admitted=True

---

## 6. JobSet Failure Policy

在既有：

    k8s/gpu-scheduling/examples/jobset-mpi.yaml

加入：

    failurePolicy:
      maxRestarts: 1
      restartStrategy: Recreate
      rules:
        - name: restart_on_child_job_failure
          action: RestartJobSet

另外 launcher / worker：

    backoffLimit: 0

意思：

    Child Job failure
    ↓
    不先反覆 retry
    ↓
    failure 傳給 JobSet controller
    ↓
    RestartJobSet
    ↓
    Recreate 整組 distributed workload

---

## 7. MPI Failure Injection

MPI 架構：

    launcher
    ↓ SSH
    worker
    ↓
    prted
    ↓
    MPI rank

為了可重複驗證 worker failure，在 worker process 加入 fault-injection hook：

    /tmp/fail-worker

測試時：

    touch /tmp/fail-worker

worker wrapper 偵測後：

    exit 42

因此：

    worker container Failed
    ↓
    worker Job Failed
    ↓
    JobSet failurePolicy
    ↓
    RestartJobSet
    ↓
    Recreate launcher + workers

---

## 8. 實際 Recovery 結果

JobSet：

    Restarts: 1
    Restarts Count Towards Max: 1

Event：

    first failed job: mpi-real-worker-1

    applying RestartJobSet failure policy action

證明：

    mpi-real-worker-1 failure
    ↓
    JobSet controller 偵測 child Job failure
    ↓
    RestartJobSet
    ↓
    整組 MPI workload 重建

新 launcher / worker Pod 名稱也全部重新產生。

最後：

    JobsReady
    all jobs are ready

代表 recovery 成功。

---

## 9. Reconciliation

Recovery 過程曾出現：

    JobCreationFailed
    jobs.batch "mpi-real-launcher-0" already exists

原因是：

    controller 開始重建
    ↓
    舊 Job 尚未完全刪除
    ↓
    第一次 create 遇到 AlreadyExists
    ↓
    controller 再次 reconcile
    ↓
    最終成功建立
    ↓
    JobsReady

重點：

> Kubernetes controller 不保證每一次操作立即成功，重點是透過 reconciliation 最終收斂到 desired state。

---

## 10. Day4 最終架構理解

    GPU Node unavailable
    │
    ├── cordon
    │     ↓
    │   Kueue TAS 阻止 admission
    │
    └── real Node failure
          ↓
        GKE Auto Repair
          ↓
        目前沒有第二台 GPU Node
          ↓
        無真正 node failover


    MPI Worker Failure
    ↓
    Child Job Failed
    ↓
    JobSet failurePolicy
    ↓
    RestartJobSet
    ↓
    Recreate distributed workload
    ↓
    JobsReady

---

## Interview Review

### Q1：GKE Auto Repair 等於 High Availability 嗎？

不是。Auto Repair 是 Node 發生問題後自動修復或重建；HA 還需要 redundancy。只有一台 GPU Node 時，Node failure 期間沒有其他 Node 可以承接 workload，因此仍會產生 downtime。

### Q2：為什麼 distributed MPI workload 的 worker 掛掉後可能需要整組 restart？

因為 MPI ranks 屬於同一個 distributed execution context，其中一個 rank / worker failure 可能使整個 MPI world 狀態失效。JobSet 可以透過 `failurePolicy: RestartJobSet` 將 child Job failure 提升成整組 workload recovery，而不是只補一個 worker。
