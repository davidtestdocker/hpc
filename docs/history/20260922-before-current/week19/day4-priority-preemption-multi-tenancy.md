<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](<../../../learning-guide.md#week19>)及[對應現行入口](<../../../runbooks/automatic-worker.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day4 — Priority / Preemption / Multi-Tenancy

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/gpu-scheduling/clusterqueue.yaml](<../../../../k8s/gpu-scheduling/clusterqueue.yaml>)
- [k8s/gpu-scheduling/localqueue.yaml](<../../../../k8s/gpu-scheduling/localqueue.yaml>)
- [k8s/gpu-scheduling/priorityclasses.yaml](<../../../../k8s/gpu-scheduling/priorityclasses.yaml>)
- [k8s/gpu-scheduling/resourceflavor.yaml](<../../../../k8s/gpu-scheduling/resourceflavor.yaml>)

---

## 今日完成內容

今天把 Kueue 的 GPU quota 進一步提升成：

- workload priority
- Kueue preemption
- low-priority workload eviction
- high-priority workload admission
- multi-tenant GPU resource competition

核心目標：

    GPU quota 已滿
    ↓
    更高優先級 workload 進來
    ↓
    Kueue 是否能讓低優先級 workload 讓出資源？

---

## 1. PriorityClass 是什麼

Kubernetes 的 PriorityClass 用來表示：

    workload priority

數字越大：

    priority 越高

目前 cluster 原本已有：

    gmp-critical
    system-cluster-critical
    system-node-critical

這些主要是系統 / GKE 元件使用，
不是一般 GPU workload 使用。

因此另外建立：

    gpu-low
    gpu-high

---

## 2. 自訂 GPU PriorityClass

建立：

    gpu-low

設定：

    value: 100

建立：

    gpu-high

設定：

    value: 1000

結果：

    gpu-low  = 100
    gpu-high = 1000

所以：

    gpu-high
    >
    gpu-low

---

## 3. Priority 不等於 Preemption

只有 PriorityClass：

    不代表高 priority workload
    一定可以把低 priority workload 擠掉

Kueue 原本 ClusterQueue：

    Within Cluster Queue: Never

代表：

    Low workload 先占 quota
        ↓
    High workload 進來
        ↓
    quota 不足
        ↓
    High 只能等待

因此還要開啟 Kueue preemption。

---

## 4. Enable Kueue Preemption

修改：

    gpu-cluster-queue

設定：

    preemption:
      withinClusterQueue: LowerPriority

驗證：

    Within Cluster Queue: LowerPriority

意思：

    同一個 ClusterQueue 裡

    higher-priority workload
    可以 preempt
    lower-priority workload

---

## 5. 測試架構

ClusterQueue：

    gpu-cluster-queue

GPU quota：

    4

ResourceFlavor：

    l4-timesharing

底層：

    1 physical NVIDIA L4
        ↓
    GKE Time-Slicing
        ↓
    4 schedulable GPU shares

---

## 6. Low Priority Job

建立：

    kueue-low

PriorityClass：

    gpu-low

Priority：

    100

設定：

    parallelism: 4
    completions: 4

每個 Pod：

    nvidia.com/gpu: 1

所以總需求：

    4 Pods
    ×
    1 GPU
    =
    4 GPU shares

剛好吃滿：

    4 / 4 quota

---

## 7. Low Workload Admission

Workload：

    job-kueue-low-3483f

結果：

    RESERVED IN:
    gpu-cluster-queue

    ADMITTED:
    True

Pod：

    4 Pods Running

因此：

    ClusterQueue quota = 4
    Low workload usage = 4

剩餘：

    0

---

## 8. High Priority Job

接著建立：

    kueue-high

PriorityClass：

    gpu-high

Priority：

    1000

設定：

    parallelism: 2
    completions: 2

每個 Pod：

    nvidia.com/gpu: 1

總需求：

    2 GPU shares

但當下：

    remaining quota = 0

所以必須：

    wait
    或
    preempt

---

## 9. Preemption Decision

Kueue event：

    PreemptedWorkload

並明確指出：

    preemptor effective priority: 1000
    preemptee effective priority: 100

代表：

    High priority workload
    =
    priority 1000

成功選中：

    Low priority workload
    =
    priority 100

作為 preemption victim。

---

## 10. Preemption 過程

High workload 一開始看到：

    insufficient unused quota

並出現：

    Pending the preemption of 1 workload(s)

這不是失敗。

而是 preemption 的暫態：

    High workload enters queue
        ↓
    quota insufficient
        ↓
    Kueue selects low workload
        ↓
    waits for low workload eviction
        ↓
    quota released
        ↓
    High reserves quota
        ↓
    High admitted

---

## 11. Low Workload 被 Evict

Low workload event：

    EvictedDueToPreempted

以及：

    Preempted

Message：

    Preempted to accommodate a workload

而且：

    preemptor effective priority: 1000
    preemptee effective priority: 100

這證明：

    Low workload
    被 High workload 擠掉

---

## 12. Low Workload 最終狀態

查看 Workload：

    job-kueue-low-3483f

結果：

    RESERVED IN:
    empty

    ADMITTED:
    False

代表：

    quota reservation 已被拿掉

    workload 不再被 admission

---

## 13. Low Pods 被清除

執行：

    kubectl get pods \
      -n hpc-platform-dev \
      -l job-name=kueue-low

結果：

    No resources found

代表：

    Low workload 被 preempt 後
    原本的 4 個 Pod 已被停止 / 移除

---

## 14. High Workload Admission

High workload：

    job-kueue-high-5a28a

結果：

    RESERVED IN:
    gpu-cluster-queue

    ADMITTED:
    True

這代表：

    Low 釋放 quota
        ↓
    High reserve 2 GPU shares
        ↓
    High admitted

---

## 15. High Pods 實際執行

查看：

    kubectl get pods \
      -n hpc-platform-dev \
      -l job-name=kueue-high

結果：

    kueue-high-4bjfh
    Running

    kueue-high-kgn44
    Running

因此：

    High workload
    2 Pods × GPU:1
    → Running

---

## 16. 完整 Preemption Flow

    ClusterQueue quota = 4
            ↓
    Low Priority Job
    priority = 100
            ↓
    requests 4 GPU shares
            ↓
    Admitted=True
            ↓
    quota full
            ↓
    High Priority Job
    priority = 1000
            ↓
    requests 2 GPU shares
            ↓
    no unused quota
            ↓
    Kueue selects Low as victim
            ↓
    EvictedDueToPreempted
            ↓
    Low Admitted=False
            ↓
    Low Pods removed
            ↓
    quota released
            ↓
    High QuotaReserved=True
            ↓
    High Admitted=True
            ↓
    High Pods Running

---

## 17. Kubernetes Priority vs Kueue Preemption

PriorityClass：

    表示誰比較重要

例如：

    gpu-low = 100
    gpu-high = 1000

但是否真的進行 queue-level preemption：

    由 Kueue ClusterQueue preemption policy 決定

所以：

    Priority
    !=
    Preemption

正確關係：

    Priority
        ↓
    Kueue compares workloads
        ↓
    Preemption Policy
        ↓
    decide whether victim can be evicted

---

## 18. WithinClusterQueue Preemption

目前設定：

    withinClusterQueue: LowerPriority

代表：

    同一個 ClusterQueue 裡

只有：

    lower-priority workload

可以被：

    higher-priority workload

preempt。

這可以避免：

    同 priority workload
    隨意互相搶資源

---

## 19. Multi-Tenant 意義

真實 AI cluster 可能有：

    Production Training
    Research Training
    Notebook
    Test Job
    Batch Inference

可以設計：

    Production
    → high priority

    Research
    → medium priority

    Dev / Test
    → low priority

當 GPU shortage：

    high priority workload
        ↓
    reclaim scarce GPU resources
        ↓
    lower priority workloads wait

---

## 20. Priority 設計原則

Priority 不應亂設。

如果所有 workload 都設：

    highest priority

那 priority system 就失去意義。

Production 通常會依：

    business criticality
    SLA
    workload type
    deadline
    environment

設計不同級別。

例如：

    prod-critical
    prod
    batch
    dev

---

## 21. Preemption 的代價

Preemption 不是免費的。

被 preempt workload 可能：

    terminate running Pods
    lose current progress
    require restart
    wait for quota again

所以 training workload 應搭配：

    checkpoint
    restart capability
    fault tolerance

避免：

    preemption
    =
    entire training lost

---

## 22. GPU Platform 架構演進

Week19 Day1：

    GPU Time-Slicing

Day2：

    Queue + Admission

Day3：

    Quota + Queue Waiting

Day4：

    Priority + Preemption

目前架構：

    GPU Workloads
        ↓
    PriorityClass
        ↓
    LocalQueue
        ↓
    ClusterQueue
        ↓
    GPU Quota
        ↓
    Preemption Policy
        ↓
    Admission
        ↓
    Kubernetes Scheduler
        ↓
    GKE Time-Slicing GPU

---

## 今日結論

Day4 完成真正的 GPU priority / preemption 測試。

實際驗證：

    Low priority = 100
    High priority = 1000

    ClusterQueue quota = 4

    Low:
    4 GPU shares
    → Admitted
    → Running

    High:
    2 GPU shares
    → quota unavailable
    → preempts Low

最後：

    Low:
    Admitted=False
    Pods removed

    High:
    Admitted=True
    2 Pods Running

證明：

    Kueue 可以根據 workload priority
    對 GPU quota 做真正的 preemption。

---

## Interview Review

**Q1：Kubernetes PriorityClass 設成高 priority，是否代表 workload 一定會 preempt 其他 workload？**  
A：不一定。PriorityClass 只表示 workload 的相對優先級；Kueue 是否允許 queue-level preemption，還要看 ClusterQueue 的 preemption policy，例如 `withinClusterQueue: LowerPriority`。

**Q2：GPU training workload 被 preempt 最大的風險是什麼？**  
A：正在執行的 Pod 可能被停止，如果 workload 沒有 checkpoint / restart 機制，就可能失去已完成的 training progress，因此 production distributed training 通常需要搭配 checkpoint 與 fault tolerance。
