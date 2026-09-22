<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day4 — 恢復與 HA 邊界

[上一課](<day3-networkpolicy-tenant-isolation.md>) · [本週目錄](README.md) · [下一課](<day5-ai-hpc-production-troubleshooting.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

worker 停止期間 JobSet 可繼續跑，恢復後收回終態；Redis Pod replacement 證明 PVC 上的測試 key 保留。這兩項都不代表整台 node 消失後有另一台接手。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[docs/demo/platform-recovery-20260921.md](<../demo/platform-recovery-20260921.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
# 2026-09-21 平台修復與驗收

本輪是現有 GKE `hpc-gpu-sg` 的維護實測，非從零重建或 production HA 認證。

## 1. Controller 排程容量

JobSet v0.12.0 controller Pending；system node allocatable 1930m，既有 requests 1638m，剩餘 292m 小於 controller request 500m。
即時 CPU 用量樣本為 198m。套用 [demo patch](../../k8s/controllers/jobset-demo-resources-patch.yaml)，將 request 調為 100m、綁定 system-pool，保留原記憶體配置與未設 CPU limit 的行為。
controller 恢復 1/1 Running，之後用量樣本為 4m／18Mi。[修復前](../evidence/platform-preflight-20260921.json)／[修復後](../evidence/platform-preflight-after-20260921.json) 保存前置檢查結果。

這些是低負載 demo 樣本，沒有證明大規模 workload 下 100m 足夠。沒有改 GKE 系統元件 requests，也沒有新增 VM。

## 2. Redis 持久化與恢復

舊 Redis 雖開啟 AOF，卻沒有掛載 volume。實測所有 DB 為空後，工具停止 API、暫停 source writes、再次驗空、建立 PVC 並部署 Redis。
寫入測試 key 後執行 graceful Pod replacement，確認 key 仍存在，再移除測試 key 並恢復 API。

[JSON 紀錄](../evidence/redis-persistence-migration-20260921.json) 顯示：

- 維護開始：09:24:20 UTC。
- 新 Redis ready、PVC Bound：09:24:41 UTC。
- Pod 替換後 test key 保留：09:24:55 UTC。
- API 恢復完成：09:25:12 UTC。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week20/day4-ha-node-failure-recovery.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：已驗證 worker 重啟接續；不等於 node failover、Redis 全失恢復或跨 DB 原子交易。
> **閱讀順序**：先學本文基礎，再讀[Week20 現行對照與檢核](../learning-guide.md#week20)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

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
