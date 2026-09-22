<!-- readable-curriculum: 2026-09-22 -->
# Week19 Day4 — Priority 與 preemption

[上一課](<day3-gpu-quota-admission-queue-behavior.md>) · [本週目錄](README.md) · [下一課](<day5-gang-jobset-mpi.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

priority 是排序信號，preemption 依配置回收低優先工作的配額。被 evict 不代表資料已安全保存，也不是完整 tenant 隔離；要看工作是否可重跑及成本。

## 在現在的專案中

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

本課對照：[k8s/gpu-scheduling/priorityclasses.yaml](<../../k8s/gpu-scheduling/priorityclasses.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
kind: PriorityClass
# 資源識別資訊；name 與 namespace 決定命名空間內的身分。
metadata:
  name: gpu-low
value: 100
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "Low priority GPU workloads"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: gpu-high
value: 1000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "High priority GPU workloads"
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week19/day4-priority-preemption-multi-tenancy.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](../learning-guide.md#week19)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day4 — Priority / Preemption / Multi-Tenancy

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/gpu-scheduling/clusterqueue.yaml](../../k8s/gpu-scheduling/clusterqueue.yaml)
- [k8s/gpu-scheduling/localqueue.yaml](../../k8s/gpu-scheduling/localqueue.yaml)
- [k8s/gpu-scheduling/priorityclasses.yaml](../../k8s/gpu-scheduling/priorityclasses.yaml)
- [k8s/gpu-scheduling/resourceflavor.yaml](../../k8s/gpu-scheduling/resourceflavor.yaml)

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
