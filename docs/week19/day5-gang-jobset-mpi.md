<!-- readable-curriculum: 2026-09-22 -->
# Week19 Day5 — JobSet 與 MPI 群組

[上一課](<day4-priority-preemption-multi-tenancy.md>) · [本週目錄](README.md) · [下一課](<day6-topology-aware-gpu-scheduling.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

launcher 和 workers 分別是 replicatedJobs，JobSet 管理整組狀態。群組生命週期不等於所有 Pod 在同一瞬間開始，也不等於任意失敗都可無成本重跑。

## 在現在的專案中

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

本課對照：[api/workloads/templates/jobset-mpi.yaml](<../../api/workloads/templates/jobset-mpi.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
    targetReplicatedJobs:
      - launcher

  # 工作失敗時由控制器採用的處理策略。
  failurePolicy:
    # JobSet 層級允許的重新啟動次數上限。
    maxRestarts: 1
    restartStrategy: Recreate
    # 規則清單；RBAC 中定義 API 存取權限，Ingress 中定義路由。
    rules:
      - name: restart_on_child_job_failure
        action: RestartJobSet

  network:
    enableDNSHostnames: true

  # JobSet 管理的子 Job 群組，例如 launcher 與 worker。
  replicatedJobs:
    - name: launcher
      # 期望副本數；設定為 0 表示不維持執行中的副本。
      replicas: 1
      # 子物件模板；控制器以此內容建立 Pod 或相關工作資源。
      template:
        spec:
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week19/day5-gang-jobset-mpi.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](../learning-guide.md#week19)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day5 — Gang Scheduling / JobSet / MPI Launcher-Worker

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/gpu-scheduling/clusterqueue.yaml](../../k8s/gpu-scheduling/clusterqueue.yaml)
- [k8s/gpu-scheduling/examples/jobset-mpi.yaml](../../k8s/gpu-scheduling/examples/jobset-mpi.yaml)：固定名稱的 MPI JobSet 實驗
- [k8s/gpu-scheduling/localqueue.yaml](../../k8s/gpu-scheduling/localqueue.yaml)
- [k8s/gpu-scheduling/resourceflavor.yaml](../../k8s/gpu-scheduling/resourceflavor.yaml)

---

## 今日目標

把 distributed workload 做成：

    JobSet
    + Kueue
    + MPI launcher
    + MPI workers

並驗證：

    資源不足
    → 整組不 admission

    資源足夠
    → 整組一起啟動

---

## 1. Gang Scheduling / All-or-Nothing

Distributed workload 可能需要：

    launcher
    worker-0
    worker-1
    worker-2

不能只啟動其中一部分。

正確行為：

    資源不足
    → 全部等待

    資源足夠
    → 整組放行

---

## 2. JobSet

JobSet 用來描述：

    一組彼此相關的 Kubernetes Jobs

本次結構：

    JobSet
    ├─ launcher
    └─ workers × 3

Kueue 會把整個 JobSet 建成：

    1 個 Workload

而不是每個 child Job 各自 admission。

---

## 3. All-or-Nothing 驗證

ClusterQueue GPU quota：

    4

先用 gpu-blocker 使用：

    2 GPU

剩餘：

    2 GPU

distributed-gang 需要：

    3 GPU

結果：

    Workload 未 Admission

    launcher    Suspended
    worker-0    Suspended
    worker-1    Suspended
    worker-2    Suspended

    Pods = 0

證明：

    JobSet 不會 partial start

---

## 4. Quota 釋放後

刪除 gpu-blocker 後：

    available GPU = 4

JobSet 立即：

    QuotaReserved=True
    Admitted=True

Child Jobs：

    launcher    Running
    worker-0    Running
    worker-1    Running
    worker-2    Running

證明：

    resource available
    → whole JobSet admitted

---

## 5. Launcher vs Worker

Launcher：

    負責啟動 distributed processes

本次使用：

    mpirun

Worker：

    真正承載 MPI process

例如：

    worker-0 → rank 0
    worker-1 → rank 1
    worker-2 → rank 2

---

## 6. SSH / sshd

Launcher 需要：

    ssh client

Worker 需要：

    sshd

作用：

    launcher
    → SSH 到 worker
    → 在 worker 上啟動 MPI process

SSH 只是 process launch 機制。

真正 MPI 執行後：

    rank 0
    ↔
    rank 1
    ↔
    rank 2

MPI processes 直接互相通信。

---

## 7. MPI Runtime Image

使用：

    mpioperator/mpi-pi:openmpi

驗證已有：

    mpirun
    ssh
    sshd

因此不用額外 build MPI image。

---

## 8. SSH Key

建立 Kubernetes Secret：

    mpi-ssh-key

用途：

    launcher private key
    → SSH client authentication

    authorized_keys
    → worker 允許 launcher 登入

    host key
    → worker sshd server identity

---

## 9. InitContainer

Secret volume 是 read-only。

因此使用：

    initContainer
    ↓
    copy SSH keys 到 emptyDir
    ↓
    chown / chmod
    ↓
    main container 使用 non-root UID 1000

這樣：

    initContainer
    → filesystem initialization

    main container
    → non-root runtime

---

## 10. 真正 MPI Launcher 驗證

Launcher 執行：

    mpirun -np 3

然後透過 SSH：

    worker-0
    worker-1
    worker-2

實際結果：

    RANK=0 HOST=mpi-real-worker-0-0
    RANK=1 HOST=mpi-real-worker-1-0
    RANK=2 HOST=mpi-real-worker-2-0

證明：

    launcher
    → mpirun
    → SSH workers
    → 啟動 MPI ranks
    → ranks 分別執行於不同 worker Pods

---

## 11. 完整架構

    JobSet
    ↓
    Kueue
    ↓
    all-or-nothing admission
    ↓
    launcher + workers
    ↓
    launcher: mpirun
    ↓
    SSH / sshd
    ↓
    worker MPI ranks
    ↓
    distributed communication

---

## 12. Kueue / JobSet / Volcano

Kueue：

    queue
    quota
    admission
    priority
    preemption

JobSet：

    描述一組相關 Jobs

Kubernetes scheduler：

    決定 Pod 放哪個 Node

Volcano：

    更深入 scheduler 層
    支援 batch / gang scheduling / placement

簡化：

    Kueue
    → workload 能不能進場

    Volcano
    → workload 的 Pods 怎麼實際排程

---

## 13. LeaderWorkerSet

JobSet：

    適合 batch / finite distributed jobs

例如：

    MPI
    training
    launcher + workers

LeaderWorkerSet：

    偏向 leader-worker topology
    與長時間 distributed serving

例如：

    distributed inference
    LLM serving

---

## 今日結論

完成：

    JobSet installation
    Kueue + JobSet integration
    all-or-nothing admission
    resource shortage waiting
    quota release admission
    real MPI launcher
    worker sshd
    multi-Pod MPI ranks

最終成功：

    RANK 0 → worker-0
    RANK 1 → worker-1
    RANK 2 → worker-2

---

## Interview Review

**Q1：Kueue + JobSet 如何避免 distributed workload partial start？**  
A：Kueue 把整個 JobSet 視為一個 Workload 做 admission，只有整組資源需求都能滿足時才解除 suspend，否則所有 child Jobs 一起等待。

**Q2：MPI launcher 與 worker 的差別？**  
A：Launcher 使用 mpirun 啟動 distributed processes；worker 承載真正的 MPI ranks。SSH/sshd 可以作為 launcher 在其他 worker 啟動 process 的機制。
