# JobSet / Kueue Recovery Demo

## Demo 目的

展示兩個不同 failure domains：MPI child Job failure 後的 JobSet 整組 recovery，以及 node 不可排程時的 Kueue admission blockage。本文件整理 [歷史 recovery 紀錄](../history/20260922-before-current/week20/day4-ha-node-failure-recovery.md.txt)，不執行新的 failure injection。

歷史 recovery experiment 使用固定名稱 **`mpi-real`**，對應 [JobSet example](../../k8s/gpu-scheduling/examples/jobset-mpi.yaml)。目前 [動態 MPI template](../../api/workloads/templates/jobset-mpi.yaml) 雖保留同類 hook／policy，不能據此宣稱 `mpi-<job_id>` 主 E2E 已重跑 recovery。

## Failure Injection

歷史測試在 worker container 建立 `/tmp/fail-worker`（hook trigger 為 `touch /tmp/fail-worker`）。Worker wrapper 偵測檔案後停止 sshd 並 `exit 42`，讓 child Job failure 傳到 JobSet controller。

```text
Worker hook triggered
→ worker container exit 42
→ child Job Failed
→ JobSet failure policy
```

這是 process／workload failure injection，不是真實硬體 node failure。

## JobSet Failure Policy

固定 example 與動態 template 保存的 policy：

```yaml
failurePolicy:
  maxRestarts: 1
  restartStrategy: Recreate
  rules:
    - name: restart_on_child_job_failure
      action: RestartJobSet
```

Launcher／worker child Jobs 設定 `backoffLimit: 0`，避免先由 child Job 反覆 retry。`RestartJobSet` 將故障提升為整組 distributed workload recovery，`Recreate` 重建 launcher 與 workers；`maxRestarts: 1` 是重啟上限，不代表無限自癒。

## Observed Recovery

以下是歷史文件保存的狀態與 event 摘錄：

```text
Restarts: 1
Restarts Count Towards Max: 1

first failed job: mpi-real-worker-1
applying RestartJobSet failure policy action

JobsReady
all jobs are ready
```

紀錄指出 launcher／worker Pod 名稱重新產生。Recovery 過程也曾出現暫態：

```text
JobCreationFailed
jobs.batch "mpi-real-launcher-0" already exists
```

歷史解釋是舊 Job 尚未完全刪除，後續 reconcile 最終收斂到 JobsReady。可驗證的是整組重建後 ready，不能延伸為 application checkpoint 恢復或最終 benchmark completion。

## Kueue Admission Interaction

同份歷史文件另記錄唯一 GPU node 的 cordon／uncordon 測試。這是 **scheduling／admission failure injection**，與上面的 worker exit 42 案例分開。

```text
cordon → node SchedulingDisabled
→ no topology domains at level: kubernetes.io/hostname
→ Workload 不 admission，Job 維持 Suspended，Pod 不建立

uncordon → node schedulable
→ QuotaReserved=True
→ Admitted=True
→ Job 建立 Pod
```

Cordon 時 node 仍可為 Ready，既有 Pod 繼續運行；此案例證明 Kueue TAS 能在 Pod 建立前阻止無合法 placement 的工作，不證明硬體故障後的 failover。

歷史紀錄還保存 `no TAS flavor assigned` 的整合問題：MPI request CPU，但 ClusterQueue 原先只管理 GPU。將 CPU quota 納入 flavor 後才完成 admission；此配置修正與 runtime recovery 是不同層次。

## Verified Evidence

| Evidence | 支持的結論 |
|---|---|
| [歷史 recovery 紀錄](../history/20260922-before-current/week20/day4-ha-node-failure-recovery.md.txt) | mpi-real worker failure、restarts=1、RestartJobSet、JobsReady；另有 cordon／uncordon admission 觀察 |
| [固定 JobSet example](../../k8s/gpu-scheduling/examples/jobset-mpi.yaml) | `mpi-real` 名稱、exit 42 hook、failure policy 的保存實作 |
| [動態 template](../../api/workloads/templates/jobset-mpi.yaml) | 相同 recovery 機制的設定仍存在；僅是實作 evidence，不是動態工作 recovery 的執行結果 |

## Limitation

Recovery 執行 evidence 是歷史文件摘錄，沒有在此補造 raw events、Pod UID timeline 或 recovery duration。驗證到 JobsReady，不代表 rank 重新完成計算、benchmark result 已回收或 progress 已復原。

當時只有一個實體 GPU node，沒有 multi-node failover；未測真實硬體 node failure。固定 `mpi-real` 與動態 `mpi-<job_id>` 必須分別描述，本次主 E2E 未重跑 recovery。

## 面試重點

- MPI worker failure 可能使整個 distributed execution context 失效，JobSet 以整組 Recreate 收斂。
- 暫態 AlreadyExists 要結合後續 controller events／JobsReady 判斷，不能只看單次 create error。
- Kueue admission blockage、JobSet workload recovery 與 node-level HA 是不同驗證範圍。
