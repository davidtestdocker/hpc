<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](<../../../learning-guide.md#week19>)及[對應現行入口](<../../../runbooks/automatic-worker.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day1 — GPU Sharing Models：Dedicated / Time-Slicing / MPS / MIG

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

下方 Kueue 設定可對照 GPU 配額與資源風味；GKE time-sharing 開關本身不由這些檔案設定。

- [k8s/gpu-scheduling/clusterqueue.yaml](<../../../../k8s/gpu-scheduling/clusterqueue.yaml>)
- [k8s/gpu-scheduling/localqueue.yaml](<../../../../k8s/gpu-scheduling/localqueue.yaml>)
- [k8s/gpu-scheduling/resourceflavor.yaml](<../../../../k8s/gpu-scheduling/resourceflavor.yaml>)

---

## 今日完成內容

今天建立 GPU sharing 的基礎模型，理解：

- Dedicated GPU
- Time-Slicing
- MPS
- MIG
- GKE GPU sharing
- GPU scheduler resource representation
- Time-Slicing 實際驗證

目標是回答：

    當 GPU 很少
    但 workload 很多時
    平台要怎麼讓多個 workload 共用 GPU？

---

## 1. Dedicated GPU

Dedicated GPU：

    Pod A
    → 整張 GPU

其他 Pod 不能同時拿同一張 GPU。

優點：

    isolation 高
    performance 穩定
    latency 可預測

缺點：

    小 workload 也會占整張 GPU
    utilization 可能偏低
    容易浪費資源

適合：

    large training
    benchmark
    latency-sensitive workload
    performance testing

---

## 2. Time-Slicing

Time-Slicing：

    Pod A
    Pod B
    Pod C
       ↓
    same physical GPU

多個 workload 共用同一張實體 GPU。

核心：

    sharing by time

不是：

    hardware partition

也不是：

    每個 Pod 固定拿 25%

Time-Slicing 主要提高：

    GPU utilization
    scheduling density

但 workload 之間仍可能競爭：

    compute
    memory
    bandwidth

---

## 3. MPS

MPS：

    Multi-Process Service

概念：

    CUDA Process A
    CUDA Process B
    CUDA Process C
          ↓
       MPS Server
          ↓
       same GPU

MPS 讓多個 CUDA process
更有效率地 concurrent 使用 GPU。

跟 Time-Slicing 差異：

    Time-Slicing
    → 主要是時間共享

    MPS
    → 多 process 更有效率地 concurrent 執行

適合：

    small CUDA workloads
    HPC multi-process workload
    low-utilization GPU jobs

---

## 4. MIG

MIG：

    Multi-Instance GPU

MIG 是真正的 hardware partition。

例如：

    1 GPU
    ↓
    MIG instance 0
    MIG instance 1
    MIG instance 2

每個 instance 可以獲得部分：

    compute
    GPU memory
    cache
    bandwidth resource

因此 isolation 比 Time-Slicing / MPS 強。

適合：

    multi-tenant production
    stable QoS
    inference serving
    workload isolation

---

## 5. 四種模式比較

    Dedicated
    → 一個 workload 獨占 GPU

    Time-Slicing
    → 多 workload 時間共享 GPU

    MPS
    → 多 CUDA process concurrent sharing

    MIG
    → hardware partition

簡化：

    Dedicated = 獨占
    Time-Slicing = 輪流共享
    MPS = 多 process 並行共享
    MIG = 硬體切片

---

## 6. MIG Capability Check

GPU：

    NVIDIA L4

執行：

    nvidia-smi -q | grep -A3 'MIG Mode'

結果：

    MIG Mode
        Current : N/A
        Pending : N/A

代表：

    NVIDIA L4 不支援 MIG

注意：

    Disabled
    → GPU 支援 MIG，只是沒開

    N/A
    → GPU 不具備 MIG capability

因此目前實驗環境：

    Dedicated
    → available

    Time-Slicing
    → available

    MPS
    → available for further study

    MIG
    → unavailable on L4

---

## 7. GKE NVIDIA Device Plugin

目前 GKE GPU node：

    nvidia-gpu-device-plugin-small-cos

代表：

    NVIDIA device plugin
    由 GKE 管理

不是自行部署 NVIDIA Helm chart。

因此 GPU sharing 應從：

    GKE node pool configuration

設定，而不是直接修改：

    kube-system DaemonSet

---

## 8. Dedicated Mode Baseline

原始 node pool：

    acceleratorCount: 1
    acceleratorType: nvidia-l4

沒有：

    gpuSharingConfig

Kubernetes：

    nvidia.com/gpu = 1

代表：

    1 physical NVIDIA L4
    ↓
    1 schedulable GPU resource

所以一般情況：

    Pod A request GPU:1
    → Running

    Pod B request GPU:1
    → Pending

---

## 9. GPU Quota Issue

第一次更新 GPU node pool：

    gpu-sharing-strategy=time-sharing
    max-shared-clients-per-gpu=4

失敗：

    QUOTA_EXCEEDED
    GPUS_ALL_REGIONS
    Limit: 1

原因：

    GKE node pool update
    預設會嘗試建立新的 surge node

流程：

    old GPU node
    +
    temporary new GPU node

短時間需要：

    2 GPUs

但目前 quota：

    1 GPU globally

所以更新失敗。

---

## 10. Node Pool Upgrade Strategy

改成：

    maxSurge = 0
    maxUnavailable = 1

指令：

    gcloud container node-pools update gpu-pool \
      --cluster=hpc-gpu-sg \
      --zone=asia-southeast1-a \
      --max-surge-upgrade=0 \
      --max-unavailable-upgrade=1

意思：

    不建立額外 surge GPU node
    ↓
    先停止舊 node
    ↓
    用原本 GPU quota 重建

缺點：

    GPU workload 會暫時中斷

但適合目前：

    single-node lab
    GPU quota = 1

---

## 11. Enable GKE Time-Slicing

設定：

    gcloud container node-pools update gpu-pool \
      --cluster=hpc-gpu-sg \
      --zone=asia-southeast1-a \
      --accelerator=type=nvidia-l4,count=1,gpu-sharing-strategy=time-sharing,max-shared-clients-per-gpu=4,gpu-driver-version=default

更新成功。

---

## 12. Time-Slicing Configuration

Node pool：

    acceleratorCount: 1
    acceleratorType: nvidia-l4

新增：

    gpuSharingConfig:
      gpuSharingStrategy: TIME_SHARING
      maxSharedClientsPerGpu: 4

代表：

    1 physical L4
    ↓
    maximum 4 shared clients

---

## 13. GKE Node Labels

Node 出現：

    cloud.google.com/gke-gpu-sharing-strategy=time-sharing

以及：

    cloud.google.com/gke-max-shared-clients-per-gpu=4

這些 label 可以用來：

    nodeSelector
    scheduler targeting
    workload placement

---

## 14. Kubernetes Allocatable GPU

Dedicated mode：

    nvidia.com/gpu = 1

啟用 Time-Slicing 後：

    nvidia.com/gpu = 4

實際輸出：

    NAME                                    GPU
    gke-hpc-gpu-sg-gpu-pool-...            4

重要：

    GPU = 4

不代表：

    4 physical GPUs

實際仍然只有：

    1 × NVIDIA L4

這個 4 是：

    4 schedulable sharing slots

---

## 15. Time-Slicing Workload Test

建立兩個 Pod：

    gpu-share-a
    gpu-share-b

兩個 Pod 都要求：

    resources:
      limits:
        nvidia.com/gpu: 1

並指定：

    cloud.google.com/gke-gpu-sharing-strategy: time-sharing

---

## 16. Actual Result

結果：

    gpu-share-a
    → Running

    gpu-share-b
    → Running

兩者都位於：

    same GPU node

因此：

    1 physical NVIDIA L4
        ↓
    Time-Slicing
        ↓
    gpu-share-a
    gpu-share-b
        ↓
    both Running

證明：

    GKE Time-Slicing 生效

---

## 17. Time-Slicing 不代表平均切分

設定：

    maxSharedClientsPerGpu = 4

不是：

    each Pod gets 25%

也不是：

    4 independent GPUs

實際：

    same physical GPU
    shared compute
    shared memory
    shared bandwidth

因此 workload 之間可能產生：

    contention
    latency variation
    throughput interference

---

## 18. Scheduling Perspective

Dedicated：

    Physical GPU = 1
    Kubernetes allocatable = 1

Time-Slicing：

    Physical GPU = 1
    Kubernetes allocatable = 4

所以 scheduler 可以接受：

    Pod A GPU:1
    Pod B GPU:1
    Pod C GPU:1
    Pod D GPU:1

但底層仍然：

    same NVIDIA L4

這是：

    scheduler-level sharing

不是：

    physical GPU multiplication

---

## 19. Production Use Cases

### Dedicated

適合：

    training
    benchmark
    performance-critical jobs

### Time-Slicing

適合：

    development
    notebook
    lightweight inference
    small experiments

### MPS

適合：

    many CUDA processes
    HPC workloads
    concurrent small GPU jobs

### MIG

適合：

    production multi-tenancy
    stronger isolation
    stable QoS

但目前 L4 不支援 MIG。

---

## 20. 今日架構

    Kubernetes Scheduler
           ↓
    nvidia.com/gpu = 4
           ↓
    GKE Time-Slicing
           ↓
    1 Physical NVIDIA L4
       ├─ gpu-share-a
       ├─ gpu-share-b
       ├─ possible share-c
       └─ possible share-d

---

## 今日結論

Day1 從：

    1 GPU
    → 1 workload

提升成：

    1 GPU
    → multiple schedulable GPU workloads

實際完成：

    Dedicated baseline
    MIG capability verification
    GPU sharing configuration
    GKE node pool update
    GPU quota troubleshooting
    Time-Slicing enablement
    Kubernetes allocatable verification
    two simultaneous GPU Pods

最重要的概念：

    Time-Slicing
    !=
    multiple physical GPUs

而是：

    multiple workloads
    sharing one physical GPU

---

## Interview Review

**Q1：Time-Slicing 開成 `maxSharedClientsPerGpu=4`，是不是代表一張 GPU 被切成四張，每個 Pod 固定拿 25%？**  
A：不是。它只是讓 scheduler 提供 4 個可排程 sharing slots，底層仍是同一張實體 GPU，compute、memory 與 bandwidth 都可能互相競爭。

**Q2：Dedicated GPU、Time-Slicing、MPS、MIG 最大差異是什麼？**  
A：Dedicated 是整張 GPU 獨占；Time-Slicing 是多 workload 時間共享；MPS 是多 CUDA process 更有效率地 concurrent sharing；MIG 則是硬體層真正切分 GPU instance。
