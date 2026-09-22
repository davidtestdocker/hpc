<!-- readable-curriculum: 2026-09-22 -->
# Week19 Day6 — Topology-aware placement

[上一課](<day5-gang-jobset-mpi.md>) · [本週目錄](README.md) · [下一課](<day7-gpu-scheduling-platform-integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Topology 描述層級，ResourceFlavor 和 PodSet 要求參與准入／placement。歷史只驗證單 GPU node 的 placement，未完成跨 node 選擇和對照性能。

## 在現在的專案中

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

本課對照：[k8s/gpu-scheduling/topology.yaml](<../../k8s/gpu-scheduling/topology.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  levels:
    - nodeLabel: topology.kubernetes.io/region
    - nodeLabel: topology.kubernetes.io/zone
    - nodeLabel: kubernetes.io/hostname
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week19/day6-topology-aware-gpu-scheduling.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](../learning-guide.md#week19)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day6 — Topology-Aware GPU Scheduling

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/gpu-scheduling/clusterqueue.yaml](../../k8s/gpu-scheduling/clusterqueue.yaml)
- [k8s/gpu-scheduling/localqueue.yaml](../../k8s/gpu-scheduling/localqueue.yaml)
- [k8s/gpu-scheduling/resourceflavor.yaml](../../k8s/gpu-scheduling/resourceflavor.yaml)
- [k8s/gpu-scheduling/topology.yaml](../../k8s/gpu-scheduling/topology.yaml)

---

## 今日完成

完成 Kueue Topology-Aware Scheduling（TAS）：

- 建立真實 GKE topology
- 建立帶 topology 的 GPU ResourceFlavor
- ClusterQueue 改用 TAS flavor
- workload 指定 hostname-level topology
- 驗證 Kueue topologyAssignment
- 驗證兩個 GPU Pods 被排到同一 hostname domain

---

## 1. Topology / Topology Domain

Topology：

    描述 cluster 中資源的位置階層

本次：

    region
    ↓
    zone
    ↓
    hostname

真實 GKE node：

    region:
    asia-southeast1

    zone:
    asia-southeast1-a

    hostname:
    gke-hpc-gpu-sg-gpu-pool-9ad99345-j95p

Topology Domain：

    某一 topology level 的實際分組值

例如：

    level = zone
    domain = asia-southeast1-a

    level = hostname
    domain = gke-hpc-gpu-sg-gpu-pool-9ad99345-j95p

---

## 2. 為什麼 GPU Scheduling 需要 Topology

Distributed GPU workload 不應只看：

    哪裡還有 GPU

還要考慮：

    GPU / Node 彼此距離

通常：

    same node
    → communication cost 較低

    same rack / zone
    → 次之

    cross-zone
    → latency / network cost 更高

因此 topology-aware scheduling 可以降低：

    MPI / NCCL communication cost

---

## 3. 建立 Kueue Topology

建立：

    gke-gpu-topology

內容：

    topology.kubernetes.io/region
    topology.kubernetes.io/zone
    kubernetes.io/hostname

代表：

    region
    ↓
    zone
    ↓
    node

---

## 4. ResourceFlavor

ResourceFlavor 可以理解成：

    Kueue 的資源種類描述

原本：

    l4-timesharing

表示：

    NVIDIA L4
    + GKE Time-Sharing

新增：

    l4-timesharing-tas

除了：

    NVIDIA L4
    + Time-Sharing

另外加入：

    topologyName: gke-gpu-topology

所以現在：

    ResourceFlavor
    ↓
    L4 Time-Sharing GPU
    ↓
    Topology-Aware

---

## 5. ClusterQueue 改用 TAS Flavor

ClusterQueue：

    gpu-cluster-queue

原本：

    flavor:
    l4-timesharing

修改成：

    flavor:
    l4-timesharing-tas

GPU quota 維持：

    nvidia.com/gpu = 4

驗證：

    Active=True

---

## 6. TAS Workload

建立：

    gpu-tas-test

設定：

    parallelism: 2
    completions: 2

每 Pod：

    nvidia.com/gpu: 1

並加入：

    kueue.x-k8s.io/podset-required-topology:
    kubernetes.io/hostname

意思：

    這個 PodSet 的 2 個 Pods
    必須被放在同一個 hostname topology domain

---

## 7. Kueue Topology Request

Workload 產生：

    topologyRequest:
      required: kubernetes.io/hostname

證明 annotation 已被 Kueue 轉換成：

    hostname-level topology requirement

---

## 8. Topology Assignment

Kueue admission 結果：

    flavor:
    l4-timesharing-tas

    resourceUsage:
    nvidia.com/gpu: 2

並產生：

    topologyAssignment

Level：

    kubernetes.io/hostname

Domain：

    gke-hpc-gpu-sg-gpu-pool-9ad99345-j95p

Pod count：

    2

代表：

    Kueue 在 admission 階段
    已指定兩個 Pods 必須使用同一 hostname domain

---

## 9. 實際 Pod Placement

實際結果：

    gpu-tas-test-6rbzc
    → gke-hpc-gpu-sg-gpu-pool-9ad99345-j95p

    gpu-tas-test-gl29b
    → gke-hpc-gpu-sg-gpu-pool-9ad99345-j95p

因此：

    topology request
    ↓
    Kueue topologyAssignment
    ↓
    Kubernetes scheduler placement
    ↓
    same hostname domain

整條流程成立。

---

## 10. 完整架構

    GPU Workload
        ↓
    Kueue Workload
        ↓
    ResourceFlavor
    l4-timesharing-tas
        ↓
    Topology
    region
      ↓
    zone
      ↓
    hostname
        ↓
    required topology:
    hostname
        ↓
    topologyAssignment
        ↓
    same-node placement

---

## 11. Day5 vs Day6

Day5：

    Gang / All-or-Nothing Admission

回答：

    「整組 workload 能不能一起進場？」

Day6：

    Topology-Aware Scheduling

回答：

    「進場後這組資源應該放在哪個 topology domain？」

兩者解決不同問題。

---

## 12. 驗證限制

目前 cluster 只有：

    1 個實體 GPU node
    1 × NVIDIA L4
    GKE Time-Sharing

因此本次真實驗證：

    Topology API
    ✓

    ResourceFlavor topology binding
    ✓

    hostname topology requirement
    ✓

    topologyAssignment
    ✓

    same-hostname Pod placement
    ✓

尚未真實驗證：

    multi-node topology selection
    cross-zone placement
    rack-aware placement
    multi-node GPU communication performance

另外兩個測試 Pod 最後觀察時仍為：

    ContainerCreating

但 node placement 已完成，因此不影響本次 TAS placement 驗證；container runtime 問題未進一步排查。

---

## Interview Review

**Q1：Topology-Aware Scheduling 解決什麼問題？**  
A：讓 scheduler 不只看資源是否存在，也考慮 node / zone 等位置關係，讓 distributed workload 優先使用彼此接近的資源，降低 MPI/NCCL communication cost。

**Q2：Kueue 的 topologyAssignment 代表什麼？**  
A：代表 Kueue 在 admission 階段已替 PodSet 選定符合要求的 topology domain，例如指定 2 個 GPU Pods 必須位於同一個 hostname domain。
