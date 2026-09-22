# HPC AI Performance Engineering Platform - Demo Script

2026-09-22：主環境已改為自動 worker，現行展示以
[自動 worker runbook](../runbooks/automatic-worker.md) 為準；只需提交與查詢。
[驗收證據](../evidence/automatic-worker-20260922.json) 包含 worker 重啟接續。
下列手動流程保留為舊版展示。

## Demo 目標

展示平台如何從 API Request 開始，在手動呼叫 worker HTTP handler 後將 MPI Workload 提交到 Kubernetes，經過 Kueue Admission 後執行 Distributed MPI。

前置條件見 [主 E2E demo](end-to-end-mpi-jobset-demo.md)。以下是展示時的檢查步驟與預期狀態，不代表目前 cluster 已重新驗證；workload 使用 CPU，三個 worker Pods 不等於三台實體 nodes。

---

## 1. 確認平台服務

```bash
kubectl get pods -n hpc-platform-dev -o wide
```

確認：

```text
api        Running
redis      Running
postgres   Running
```

平台控制服務應位於 `system-pool`。

---

## 2. 提交 MPI Benchmark

```bash
curl -X POST \
  http://127.0.0.1:8000/benchmark \
  -H 'Content-Type: application/json' \
  -d '{"benchmark":"mpi"}'
```

說明：

```text
FastAPI
→ 建立 Job
→ PostgreSQL 保存 Job metadata
→ Redis Queue 排隊
```

記下回傳的 `job_id`。

---

## 3. Worker Dispatch

```bash
curl -X POST \
  http://127.0.0.1:8000/worker/process-next
```

說明：

```text
Worker
→ 從 Redis 取得 Job
→ Worker handler 判斷 benchmark=mpi
→ Dispatcher
→ Renderer 產生 JobSet Manifest
→ Kubernetes Python Client
→ Kubernetes API
```

預期：

```text
status=submitted
jobset_name=mpi-<job_id>
```

---

## 4. 查看 JobSet / Kueue

```bash
kubectl get jobset -n hpc-platform-dev
```

確認新 JobSet：

```text
SUSPENDED=false
```

說明：

```text
JobSet
→ LocalQueue
→ ClusterQueue
→ ResourceFlavor
→ Topology-Aware Scheduling
→ Kueue Admission
```

---

## 5. 查看 Distributed Workload

```bash
kubectl get jobs,pods -n hpc-platform-dev
```

確認：

```text
MPI Launcher   Running
Worker 0       Running
Worker 1       Running
Worker 2       Running
```

---

## 6. 查看 Node Placement

```bash
kubectl get pods -n hpc-platform-dev -o wide
```

確認 MPI Pods 被排到：

```text
gpu-pool
```

平台服務則位於：

```text
system-pool
```

說明 CPU platform service layer 與 distributed workload layer 的 Node Pool 分工；system-pool 不是 GKE managed control plane。現有 overlay 未以 nodeSelector 鎖定 system-pool，應以實際 placement 為準。

---

## 7. 驗證 MPI Execution

找到 Launcher Pod：

```bash
kubectl get pods -n hpc-platform-dev | grep launcher
```

查看 Log：

```bash
kubectl logs -n hpc-platform-dev <launcher-pod>
```

預期：

```text
RANK=0 HOST=...worker-0...
RANK=1 HOST=...worker-1...
RANK=2 HOST=...worker-2...
```

這證明：

```text
JobSet 建立成功
→ MPI Worker DNS / SSH 成功
→ mpirun 成功
→ Distributed MPI Rank 實際執行
```

---

# Demo 主線

```text
Client
→ FastAPI
→ PostgreSQL
→ Redis Queue
→ Worker
→ Dispatcher
→ Kubernetes API
→ JobSet
→ Kueue
→ MPI Launcher / Workers
→ Distributed Execution
```
