<!-- readable-curriculum: 2026-09-22 -->
# Week19 Day3 — Quota 與等待

[上一課](<day2-kueue-gpu-admission.md>) · [本週目錄](README.md) · [下一課](<day4-priority-preemption-multi-tenancy.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

quota 足夠只是准入條件之一，實際 node 容量、taints、topology 還可能讓 Pod Pending。增加 queue quota 不會增加 GPU node 或雲端配額。

## 在現在的專案中

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

本課對照：[k8s/gpu-scheduling/clusterqueue.yaml](<../../k8s/gpu-scheduling/clusterqueue.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  resourceGroups:
    - coveredResources:
        - cpu
        - nvidia.com/gpu
      flavors:
        - name: l4-timesharing-tas
          # 資源設定；Pod 中是 requests／limits，Kustomize 中是待組合的檔案清單。
          resources:
            - name: cpu
              # 佇列的名義資源配額，准入時計入使用量。
              nominalQuota: "3"
            - name: nvidia.com/gpu
              nominalQuota: "4"
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week19/day3-gpu-quota-admission-queue-behavior.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行自動 worker 提交／回收 MPI；歷史 TAS placement 不等於多節點效能或當時工作成功。
> **閱讀順序**：先學本文基礎，再讀[Week19 現行對照與檢核](../learning-guide.md#week19)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week19 Day3 — GPU Quota / Admission / Queue Behavior

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/gpu-scheduling/clusterqueue.yaml](../../k8s/gpu-scheduling/clusterqueue.yaml)
- [k8s/gpu-scheduling/localqueue.yaml](../../k8s/gpu-scheduling/localqueue.yaml)
- [k8s/gpu-scheduling/resourceflavor.yaml](../../k8s/gpu-scheduling/resourceflavor.yaml)

---

## 今日完成內容

今天驗證 Kueue 在 GPU quota 不足時的真實行為：

- 單一 workload 超過 quota
- 多個 workload 累積超過 quota
- Workload Pending
- QuotaReserved=False
- 前一個 workload 完成後 quota 釋放
- 後面的 workload 自動被 admission

今天核心不是單純看 Job Pending，
而是理解：

    Kueue 怎麼根據 ClusterQueue quota
    決定 workload 能不能開始跑。

---

## 1. 目前 Queue 架構

目前：

    LocalQueue:
    gpu-local-queue

        ↓

    ClusterQueue:
    gpu-cluster-queue

        ↓

    ResourceFlavor:
    l4-timesharing

        ↓

    nvidia.com/gpu quota = 4

底層 GPU：

    1 physical NVIDIA L4
        ↓
    GKE Time-Slicing
        ↓
    4 schedulable GPU shares

---

## 2. Workload 是什麼

Kueue 真正管理的是：

    Workload

不是直接管理 Job 本身。

流程：

    Kubernetes Job
        ↓
    Kueue detects queue label
        ↓
    Kueue creates Workload
        ↓
    Workload records:
        queue
        resource request
        quota reservation
        ResourceFlavor
        admission state

所以：

    Job
    = 實際執行的 Kubernetes 工作

    Workload
    = Kueue 用來排隊與管理資源的物件

---

## 3. 單一 Workload 超過 Quota

先建立：

    kueue-gpu-overquota

要求：

    nvidia.com/gpu: 5

ClusterQueue quota：

    4

所以：

    request = 5
    quota = 4

Kueue 結果：

    QuotaReserved=False

Reason：

    Pending

Message：

    insufficient quota for nvidia.com/gpu
    current podset request (5)
    > maximum capacity (4)

因此：

    5 > 4
        ↓
    no quota reservation
        ↓
    workload Pending
        ↓
    Job 不會被 admission

---

## 4. Kueue Admission 發生在 Scheduler 前面

這個案例證明：

    Job request = 5 GPU

不會先直接進 Kubernetes Scheduler。

而是：

    Job
        ↓
    Kueue
        ↓
    quota check
        ↓
    rejected / pending

所以 Kueue 可以在 workload 真正進入 node scheduling 前，
就先擋掉不符合 quota 的工作。

---

## 5. GKE Time-Slicing 的重要限制

一開始嘗試：

    single Pod
    requests:
    nvidia.com/gpu: 3

Kueue 可以 reserve：

    3 GPU quota

但 Pod 實際建立後出現：

    UnexpectedAdmissionError

Kubelet event：

    invalid request for sharing GPU (time-sharing),
    at most 1 nvidia.com/gpu can be requested on GPU nodes

代表：

    GKE Time-Slicing
    單一 Pod / container
    最多只能 request 1 個 nvidia.com/gpu

因此錯誤模型：

    1 Pod × GPU:3

不能用來代表：

    3 GPU shares

---

## 6. 正確的 Time-Slicing Share 模型

正確做法：

    3 Pods
    ×
    每 Pod request 1 GPU
    =
    3 GPU shares

所以 Job A 改成：

    parallelism: 3
    completions: 3

每個 Pod：

    limits:
      nvidia.com/gpu: 1

這樣才符合 GKE Time-Slicing 的實際限制。

---

## 7. Job A

Job A：

    kueue-gpu-a

設定：

    parallelism: 3
    completions: 3

每個 Pod：

    nvidia.com/gpu: 1

所以總需求：

    3 Pods
    ×
    1 GPU
    =
    3 GPU shares

---

## 8. Job A Admission

Workload：

    job-kueue-gpu-a-...

結果：

    RESERVED IN:
    gpu-cluster-queue

    ADMITTED:
    True

三個 Pod：

    Running
    Running
    Running

所以：

    ClusterQueue quota = 4

    Job A usage = 3

剩餘：

    1 GPU share

---

## 9. Job B

Job B：

    kueue-gpu-b

設定：

    parallelism: 2
    completions: 2

每個 Pod：

    nvidia.com/gpu: 1

所以總需求：

    2 GPU shares

---

## 10. 累積 Quota 不足

此時：

    Job A already reserved = 3

ClusterQueue：

    quota = 4

剩餘：

    1

Job B：

    request = 2

所以：

    available = 1
    request = 2

結果：

    insufficient unused quota

Kueue event：

    couldn't assign flavors to pod set main:
    insufficient unused quota for nvidia.com/gpu
    in flavor l4-timesharing,
    1 more needed

---

## 11. Job B Pending

Workload：

    job-kueue-gpu-b-...

當時：

    RESERVED IN:
    empty

    ADMITTED:
    empty

代表：

    Job B 還沒有獲得 quota reservation

所以：

    Job A
    → admitted

    Job B
    → queued / pending

---

## 12. 重要觀念：不是只有單一 Job 超 Quota 才會 Pending

Job B 自己只要求：

    2 GPU shares

而 ClusterQueue quota：

    4

所以單獨看：

    2 <= 4

是合法的。

但 Kueue 看的是：

    currently reserved resources
    +
    new workload request

也就是：

    3 + 2 > 4

因此：

    Job B Pending

這就是 quota-aware admission。

---

## 13. Queue Saturation

當 quota 被占滿時：

    Existing Workload
        ↓
    reserves quota
        ↓
    New Workload
        ↓
    insufficient unused quota
        ↓
    stays in queue

所以 Kueue 的 queue 不是單純 FIFO 清單，
而是會根據：

    quota
    flavor
    workload request
    queue strategy

決定 admission。

---

## 14. Job A 完成

Job A 內部：

    3 Pods

每個執行：

    sleep 300

所以大約：

    5 minutes

三個 Pod 是平行執行，
不是：

    3 × 5 = 15 minutes

而是大約：

    5 minutes + scheduling startup time

---

## 15. Quota Release

Job A 完成後：

    FINISHED=True

代表：

    Job A execution complete
        ↓
    Kueue releases reservation
        ↓
    3 GPU quota returned

原本：

    used = 3
    available = 1

變成：

    used = 0
    available = 4

---

## 16. Job B 自動 Admission

Job A 完成後，
重新查看：

    kubectl get workload -n hpc-platform-dev

結果：

    job-kueue-gpu-a-...
    ADMITTED=True
    FINISHED=True

    job-kueue-gpu-b-...
    RESERVED IN=gpu-cluster-queue
    ADMITTED=True

代表：

    Job A finished
        ↓
    quota released
        ↓
    Kueue reevaluates queue
        ↓
    Job B now fits quota
        ↓
    quota reserved
        ↓
    Job B admitted automatically

---

## 17. Queue Re-Evaluation

這次真正驗證：

    workload Pending

不是永久失敗。

如果原因只是：

    temporary quota shortage

當前一個 workload 完成後，
Kueue 會重新評估 queue。

所以：

    Pending
        ↓
    quota becomes available
        ↓
    QuotaReserved
        ↓
    Admitted
        ↓
    Running

不需要人工重新 submit Job。

---

## 18. 完整實驗

ClusterQueue：

    quota = 4

Job A：

    3 Pods
    ×
    GPU:1

結果：

    usage = 3
    Admitted=True

Job B：

    2 Pods
    ×
    GPU:1

當 A 還在執行：

    available = 1
    request = 2

結果：

    Pending

A 完成：

    releases 3

接著：

    available = 4

B：

    request = 2

結果：

    Admitted=True

---

## 19. 完整 Queue Behavior

    ClusterQueue quota = 4
            ↓
    Job A requests 3
            ↓
    QuotaReserved=True
            ↓
    Admitted=True
            ↓
    Remaining quota = 1
            ↓
    Job B requests 2
            ↓
    insufficient unused quota
            ↓
    Pending
            ↓
    Job A finishes
            ↓
    quota released
            ↓
    Kueue reevaluates Job B
            ↓
    QuotaReserved=True
            ↓
    Admitted=True

---

## 20. Production Multi-Tenant 意義

如果很多 team 共用 GPU：

    Team A Job
    Team B Job
    Team C Job

Kueue 不會讓所有 workload
直接同時衝進 Kubernetes Scheduler。

而是：

    queue
        ↓
    quota
        ↓
    admission
        ↓
    scheduler

因此可以避免：

    unlimited workload submission
    GPU resource oversubscription
    uncontrolled contention

也為後續：

    team quota
    priority
    preemption
    fairness

提供基礎。

---

## 21. 今日遇到的重要錯誤

錯誤：

    UnexpectedAdmissionError

原因：

    single Pod requested:

    nvidia.com/gpu: 3

但 GKE Time-Slicing：

    at most 1 nvidia.com/gpu
    can be requested per shared GPU workload

修正：

    3 Pods
    ×
    GPU:1

而不是：

    1 Pod
    ×
    GPU:3

這是 GKE Time-Slicing resource model
很重要的限制。

---

## 今日結論

Day3 從：

    Kueue 可以 admission GPU Job

進一步驗證：

    quota shortage
    queue waiting
    quota release
    automatic admission

核心流程：

    Workload request
        ↓
    ClusterQueue quota check
        ↓
    enough?
       ├─ Yes → Admitted
       └─ No  → Pending
                  ↓
              wait for quota
                  ↓
              reevaluate
                  ↓
              Admitted

本次實際完成：

    over-quota workload Pending
    cumulative quota saturation
    correct GKE Time-Slicing multi-Pod model
    quota reservation
    pending workload
    quota release
    automatic re-admission

---

## Interview Review

**Q1：一個 workload 本身沒有超過 ClusterQueue quota，為什麼仍可能 Pending？**  
A：因為 Kueue 會計算目前已被其他 workload reserve 的資源。即使新 workload 本身 request 小於總 quota，只要剩餘 unused quota 不足，它仍會留在 queue 等待。

**Q2：GKE Time-Slicing 下要使用 3 個 GPU share，為什麼不能讓單一 Pod request `nvidia.com/gpu: 3`？**  
A：GKE Time-Slicing 限制單一共享 GPU workload 最多 request `nvidia.com/gpu: 1`。要使用 3 個 share，應建立 3 個 Pod，每個 Pod request 1 個 GPU share。
