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
