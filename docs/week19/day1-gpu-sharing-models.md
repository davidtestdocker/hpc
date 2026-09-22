<!-- readable-curriculum: 2026-09-22 -->
# Week19 Day1 — GPU sharing models

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-kueue-gpu-admission.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

time-sharing 讓多工作輪流用同一 GPU，沒有同等於硬體分割的記憶體／效能隔離。排程顯示四個可分配 share，不代表有四倍計算能力。

## 在現在的專案中

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

本課對照：[terraform/environments/gpu-sg/main.tf](<../../terraform/environments/gpu-sg/main.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
      gpu_sharing_config {
        gpu_sharing_strategy       = "TIME_SHARING"
        max_shared_clients_per_gpu = 4
      }
    }

    # GKE 會在同時存在 CPU pool 時自動加入 nvidia.com/gpu=present:NoSchedule，
    # 並透過 effective_taints 回報；重複宣告 taint 會造成無效的匯入後 drift。

    shielded_instance_config {
      enable_integrity_monitoring = true
    }
  }
}
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week19/day1-gpu-sharing-models.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](../learning-guide.md#week19)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day1 — GPU Sharing Models：Dedicated / Time-Slicing / MPS / MIG

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

下方 Kueue 設定可對照 GPU 配額與資源風味；GKE time-sharing 開關本身不由這些檔案設定。

- [k8s/gpu-scheduling/clusterqueue.yaml](../../k8s/gpu-scheduling/clusterqueue.yaml)
- [k8s/gpu-scheduling/localqueue.yaml](../../k8s/gpu-scheduling/localqueue.yaml)
- [k8s/gpu-scheduling/resourceflavor.yaml](../../k8s/gpu-scheduling/resourceflavor.yaml)

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
