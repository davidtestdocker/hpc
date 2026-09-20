# End-to-End MPI JobSet Demo

## Demo 目的

這個 Demo 用來驗證 HPC AI Performance Engineering Platform 的完整工作提交流程。

使用者先透過 FastAPI 提交 MPI benchmark，工作會進入 Redis Queue，接著由 Worker 取出工作，再透過 Dispatcher 呼叫 Kubernetes API 建立 JobSet。

JobSet workload 由 Kueue 進行 queue／resource admission，Pod placement 由 Kubernetes Scheduler 完成，最後啟動 MPI Launcher 與 3 個 Worker，並透過 `mpirun` 實際啟動 3 個 MPI Rank。

以下成功結果是保存的歷史 evidence，不代表目前 cluster 即時狀態。Template request CPU，三個 worker Pods 不等於三台實體 nodes，也不代表 GPU benchmark；主線目前驗證到 rank execution，尚無 completion／result 回收閉環。

---

## 架構流程

```text
Client
  │
  │ POST /benchmark
  ▼
FastAPI
  │
  ▼
Redis Job Queue
  │
  │ /worker/process-next
  ▼
Workload Dispatcher
  │
  ▼
Kubernetes API
  │
  ▼
JobSet
  │
  ▼
Kueue Admission
  │
  ▼
MPI Launcher
  │
  ├── Worker 0
  ├── Worker 1
  └── Worker 2
```

---

## Demo prerequisite

以下指令從 repo 根目錄執行。先確認 kubectl context 指向目標 cluster（本次成功環境為 `hpc-gpu-sg`），且 `hpc-platform-dev` namespace、JobSet／Kueue controllers、`gpu-local-queue` 與其 ClusterQueue／ResourceFlavor／Topology 已建立。API image 需要可從 Artifact Registry 拉取；目前 dev tag 為 `jobset-dispatch-v4`。

平台 overlay 包含 API、Redis、PostgreSQL，以及 API 使用的 ServiceAccount／Role／RoleBinding；不會建立上述 controllers、queues 或 MPI SSH Secret。它使用本地 Helm charts 與跨目錄檔案引用，因此需要 Helm CLI，以及以下 render flags：

```bash
kubectl kustomize kustomize/overlays/gpu-sg-platform \
  --enable-helm --load-restrictor LoadRestrictionsNone \
  > /tmp/gpu-sg-platform-final.yaml
```

此指令只 render，不會部署。`LoadRestrictionsNone` 用於讀取此 repo 內的 chart、values 與共用 RBAC manifest；應先檢視可信任的 repo 內容。執行後續步驟前，平台服務需已部署並可用。

### MPI SSH Secret

JobSet template 需要 namespace 內的 `mpi-ssh-key`，包含 `id_ed25519`、`id_rsa`、`authorized_keys`。Launcher 使用 Ed25519 key，worker template 另外掛載 RSA key；公鑰均加入 `authorized_keys`。若已有可用的 Secret，沿用即可，不要覆寫進行中 workload 的 key。

新環境可使用以下 Bash 指令建立 demo 專用 key。Private keys 僅短暫存於 repo 外的受限暫存目錄，再直接送入 Kubernetes Secret；不要輸出或保存含 private key 的 Secret YAML 到 repo。

```bash
(
  set -eu
  umask 077
  mpi_key_dir=$(mktemp -d /tmp/hpc-mpi-ssh.XXXXXX)
  trap 'rm -rf -- "$mpi_key_dir"' EXIT

  ssh-keygen -q -t ed25519 -N '' -C mpi-demo-launcher \
    -f "$mpi_key_dir/id_ed25519"
  ssh-keygen -q -t rsa -b 3072 -N '' -C mpi-demo-worker \
    -f "$mpi_key_dir/id_rsa"
  cat "$mpi_key_dir/id_ed25519.pub" "$mpi_key_dir/id_rsa.pub" \
    > "$mpi_key_dir/authorized_keys"

  kubectl create secret generic mpi-ssh-key -n hpc-platform-dev \
    --from-file=id_ed25519="$mpi_key_dir/id_ed25519" \
    --from-file=id_rsa="$mpi_key_dir/id_rsa" \
    --from-file=authorized_keys="$mpi_key_dir/authorized_keys"
)
```

### PostgreSQL 初始化與 API 存取

PostgreSQL ready 後，在已注入 DB connection 環境變數的 API container 執行初始化，再提交第一個 benchmark：

```bash
kubectl exec -n hpc-platform-dev deployment/api -- \
  python -m api.database.init_db
```

目前使用 `Base.metadata.create_all(bind=engine)` 建立缺少的 table；它不會替既有 table 執行 schema migration。Future Improvement：有 schema 演進需求時導入 Alembic，這個 demo 先保留現有初始化方式。

另開 terminal 保持 port-forward，後續 curl 才能使用本機 8000 port：

```bash
kubectl port-forward -n hpc-platform-dev service/api-service 8000:8000
```

---

## 1. 提交 MPI Benchmark

先透過 FastAPI 建立 benchmark job：

```bash
curl -X POST \
  http://127.0.0.1:8000/benchmark \
  -H 'Content-Type: application/json' \
  -d '{"benchmark":"mpi"}'
```

以下保留成功執行當時的原始回應；目前 API 的 `next_step` 已改為 `Check job status at GET /jobs/<job_id>`，其他歷史 evidence 不變。`GET /jobs` 也可列出工作；MPI 狀態目前在 dispatch 後為 `submitted`，尚未同步 JobSet 的最終完成狀態。

```json
{
  "message": "benchmark request received",
  "job_id": "52eedc2a-f6b1-4c97-9c11-529223ed6899",
  "benchmark": "mpi",
  "status": "accepted",
  "next_step": "job status API will be added next"
}
```

此時代表：

```text
FastAPI 已收到 Request
→ Job 已建立
→ Job 已寫入 PostgreSQL
→ Job 已加入 Redis Queue
```

---

## 2. Worker 取出工作

呼叫 Worker：

```bash
curl -X POST \
  http://127.0.0.1:8000/worker/process-next
```

實際回應：

```json
{
  "job_id": "52eedc2a-f6b1-4c97-9c11-529223ed6899",
  "benchmark": "mpi",
  "simulate_failure": false,
  "status": "submitted",
  "result": {
    "message": "MPI JobSet submitted",
    "jobset_name": "mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899"
  },
  "retry_count": 0
}
```

流程：

```text
Redis Queue
→ Worker 取得 Job
→ benchmark == mpi
→ Dispatcher
→ Renderer 產生 JobSet Manifest
→ Kubernetes Python Client
→ Kubernetes API Server
→ 建立 JobSet
```

---

## 3. 驗證 JobSet

查詢 JobSet：

```bash
kubectl get jobset -n hpc-platform-dev
```

建立出的 JobSet：

```text
mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899
```

關鍵狀態：

```text
SUSPENDED=false
```

代表 JobSet 已經不再被 Kueue 暫停，可以開始執行。

---

## 4. Kueue Admission

JobSet 建立後會進入 Kueue。

流程：

```text
JobSet
→ LocalQueue
→ ClusterQueue
→ ResourceFlavor
→ Topology-Aware Scheduling
→ Node Placement
```

此 Demo 使用：

```text
LocalQueue:
gpu-local-queue

ClusterQueue:
gpu-cluster-queue

Topology:
gke-gpu-topology
```

當 Kueue 確認資源與拓樸條件可以滿足 Workload 後，才會正式 Admission。

---

## 5. 驗證 Launcher 與 Worker

查詢 Job 與 Pod：

```bash
kubectl get jobs,pods \
  -n hpc-platform-dev | \
  grep 'mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899'
```

實際結果：

```text
launcher    Running
worker-0    Running
worker-1    Running
worker-2    Running
```

JobSet 成功建立：

```text
1 個 MPI Launcher
3 個 MPI Worker
```

---

## 6. 驗證 Node Placement

```bash
kubectl get pods \
  -n hpc-platform-dev \
  -o wide | \
  grep 'mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899'
```

Launcher 與 Worker 都被排到：

```text
gpu-pool
```

GPU Node 有以下 Taint：

```text
nvidia.com/gpu=present:NoSchedule
```

因此 MPI JobSet 的 Pod Template 必須加入：

```yaml
tolerations:
  - key: nvidia.com/gpu
    operator: Equal
    value: present
    effect: NoSchedule
```

否則 Scheduler / Kueue 會排除 GPU Node。

---

## 7. 驗證 MPI 實際執行

查看 Launcher Log：

```bash
kubectl logs \
  -n hpc-platform-dev \
  mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899-launcher-0-0-flsfn
```

實際輸出：

```text
RANK=0 HOST=mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899-worker-0-0
RANK=2 HOST=mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899-worker-2-0
RANK=1 HOST=mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899-worker-1-0
```

這代表：

```text
Launcher
→ 成功透過 SSH 連線到 3 個 Worker
→ mpirun 成功啟動
→ 3 個 MPI Rank 成功執行
```

因此不是只有 Pod Running，而是真正完成 MPI Distributed Execution。

---

# End-to-End 結果

完整流程：

```text
POST /benchmark
        ↓
FastAPI
        ↓
PostgreSQL
        ↓
Redis Queue
        ↓
Worker
        ↓
Workload Dispatcher
        ↓
Kubernetes API
        ↓
JobSet
        ↓
Kueue Admission
        ↓
MPI Launcher + 3 Workers
        ↓
mpirun
        ↓
RANK 0 / RANK 1 / RANK 2
```

結果：

```text
End-to-End MPI workload submission and distributed execution
驗證成功
```

---

# Troubleshooting Case

整合過程中曾遇到 JobSet 一直維持：

```text
SUSPENDED=true
```

Kueue 顯示：

```text
topology "gke-gpu-topology" doesn't allow to fit any of 1 pod(s)

excluded:
taint "nvidia.com/gpu=present:NoSchedule"
```

## Root Cause

GPU Node 有：

```text
nvidia.com/gpu=present:NoSchedule
```

但 MPI Launcher / Worker Pod 沒有對應的 Toleration。

因此：

```text
JobSet
→ Kueue Topology Placement
→ GPU Node 因 Taint 被排除
→ 無可用 Node
→ Workload Pending
```

## Resolution

在 Launcher 與 Worker Pod Spec 加入：

```yaml
tolerations:
  - key: nvidia.com/gpu
    operator: Equal
    value: present
    effect: NoSchedule
```

修正後：

```text
Kueue Admission 成功
→ JobSet SUSPENDED=false
→ Launcher / Worker 建立
→ MPI 成功執行
```

---

# Platform Components

本 Demo 涉及：

- FastAPI
- Redis
- PostgreSQL
- Kubernetes / GKE
- Kubernetes Python Client
- Kubernetes ServiceAccount
- Kubernetes RBAC
- JobSet
- Kueue
- LocalQueue
- ClusterQueue
- ResourceFlavor
- Topology-Aware Scheduling
- Taint / Toleration
- MPI / OpenMPI
- GPU Node Pool

---

# Demo 重點

這個 Demo 驗證的不是單一 Kubernetes YAML，而是一條完整的平台工作流：

```text
API Layer
→ Queue Layer
→ Dispatch Layer
→ Scheduler Layer
→ Distributed Compute Layer
```

平台從 API Request 建立工作後，需手動呼叫 worker HTTP handler，才會將 MPI Job 提交到 Kubernetes，經過 Kueue Admission 後執行 Distributed MPI Workload。
