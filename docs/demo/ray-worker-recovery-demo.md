# Ray Worker Recovery Demo

## Demo 目的

透過兩個既有案例展示 Kubernetes、Ray scheduler 與 KubeRay controller 的責任邊界：resource mismatch，以及 worker 消失後的 task retry。本文件整理 historical evidence，供面試時依設定、症狀與結果展示；本輪未重跑實驗，也未接入主 MPI E2E。

## Failure Scenario

環境設定見 [RayCluster](../../ray-cluster.yaml)：Ray 2.47.1、namespace `ray-system`、cluster `hpc-ray`，CPU worker group 的 desired replicas 為 2。

| 案例 | Trigger | 對應實作 |
|---|---|---|
| Resource mismatch | CPU Ray cluster 上提交要求 `num_gpus=1` 的 task | [mismatch RayJob](../../ray-resource-mismatch-job.yaml) |
| Worker recovery | 長時間 task 執行中，刪除承載它的 Ray worker Pod，造成 Ray node disappearance | [recovery RayJob](../../ray-worker-recovery-job.yaml) |

這是兩個分開的案例；GPU pending task 不是後面 recovery 測試的 long_task。

## Observed Symptoms

[歷史排障紀錄](../week20/day5-ai-hpc-production-troubleshooting.md) 與 [runbook](../runbooks/ai-hpc-job-troubleshooting.md) 保存以下觀察。Resource mismatch 時 Kubernetes Pods 為 Running，但 Ray resources 為 CPU=3、GPU=0；task 要求 CPU=1、GPU=1：

```text
{'CPU': 1.0, 'GPU': 1.0}: 1+ pending tasks/actors
```

Worker recovery 案例的 task state 摘錄：

```text
attempt_number: 0
state: RUNNING

attempt_number: 0
state: FAILED
error_type: NODE_DIED

attempt_number: 1
state: RUNNING
```

歷史紀錄明確指出 attempt 1 已在另一個 Ray node／Ray Pod 啟動，KubeRay 也建立替代 worker Pod。

## Root Cause / Failure Domain

Resource mismatch 位於 Ray scheduler：Kubernetes Pod Running 只代表容器已啟動，不能證明 Ray resource 能滿足 task。當 Ray GPU=0，要求 `num_gpus=1` 的 task 沒有合法資源可用。

Recovery 案例則是執行 task 的 Ray node 隨 worker Pod 消失，Ray 偵測到 `NODE_DIED`。這裡的 Ray node 是 runtime 成員，不代表 Kubernetes 實體 node 發生硬體故障。

面試時可用歷史調查工具 `ray status`、`ray.cluster_resources()`、`ray.available_resources()` 說明如何區分 Pod placement 與 task scheduling；本文件沒有執行這些指令。

## Recovery Mechanism

Recovery manifest 設定 `@ray.remote(max_retries=2)`，並使用 `NodeAffinitySchedulingStrategy(node_id=target["NodeID"], soft=True)`。初次執行偏好選定 worker；該 Ray node 消失後，retry policy 允許重試，soft affinity 允許在其他可用 Ray node 排程。

```text
Worker Pod 消失
  ├─ Ray：attempt 0 NODE_DIED → retry → 另一 Ray node 的 attempt 1 RUNNING
  └─ KubeRay：worker 數量低於 desired replicas → 建立替代 worker Pod
```

這兩個 recovery loop 分別處理 task execution 與 cluster desired state。紀錄不足以判定兩者精確時序，也不表示 task 必須等新 worker 建好才開始 retry。

## Verified Evidence

| Evidence | 可確認的內容 |
|---|---|
| [Recovery RayJob](../../ray-worker-recovery-job.yaml) | `max_retries=2`、soft affinity、TARGET_NODE_ID／TARGET_IP／TASK_HOST 輸出設計 |
| [歷史排障紀錄](../week20/day5-ai-hpc-production-troubleshooting.md) | Resource mismatch、NODE_DIED、另一 Ray node 的 retry、KubeRay 補 worker |
| [Runbook](../runbooks/ai-hpc-job-troubleshooting.md) | attempt 0 FAILED → attempt 1 RUNNING 的 state 摘錄 |

## Limitation

保存的 recovery evidence 到 attempt 1 RUNNING，沒有足夠結果可宣稱 task 最終 SUCCEEDED。Manifest 中有 `RESULT=` 輸出程式碼，不等於 repo 已保存該次完成輸出。

本案例未驗證 GPU Ray workload 成功、exactly-once 或 actor state recovery。跨 Ray node retry 的證據是歷史文件敘述與 state 摘錄，沒有在此補造完整 task ID／node ID 對照 raw dump。

## 面試重點

- 先比較 task resource demand 與 Ray available resources，Pod Running 不能排除 runtime scheduling 問題。
- Ray task retry 與 KubeRay worker reconciliation 是兩個不同責任的 recovery loop。
- 已驗證 retry 在另一 Ray node 啟動；最終完成與 state durability 需要額外證據。
