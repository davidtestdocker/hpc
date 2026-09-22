# 主展示環境：部署與驗收入口

2026-09-22 現行補充：主 overlay 使用 `automatic-worker-20260922-v1`，
新增 `api-worker` Deployment，自動 dispatch／collect；手動 `/worker/*`
端點停用。現行操作與重啟驗收見 [自動 worker](automatic-worker.md)。
以下 9/21 collector 手動指令只適用當時版本。

更新：2026-09-21。本文件是現行操作入口；Week 文件保留歷史紀錄。
已完成 JobSet controller 容量修復、空 Redis 移至 PVC、Redis Pod 替換後資料保留、MPI collector image rollout 與 API lifecycle 驗收。
已在既有主叢集套用完整 overlay，三個服務 rollout 與 DB 初始化通過；Terraform 已完成主環境 import／零 drift。後續全新 CPU-only cluster 的 controllers／平台 bootstrap、驗收與銷毀也已通過；該次不涵蓋 GPU／MPI 執行，證據見下方 CPU bootstrap acceptance。

## 固定範圍

- GKE：`hpc-gpu-sg`，zone `asia-southeast1-a`。
- Namespace：`hpc-platform-dev`。
- `system-pool`：API、Redis、PostgreSQL；新 overlay 明確限制 placement。
- `gpu-pool`：既有 MPI／GPU 實驗；此專案 quota 固定為一張實體 GPU，shares 不代表多 GPU。
- 主 overlay：`kustomize/overlays/gpu-sg-platform`，不再共用舊 dev image values。
- Terraform `environments/dev` 仍是歷史 `hpc-dev`；主環境改用 [gpu-sg root module](../../terraform/environments/gpu-sg/README.md)。既有資源 import 後為零 drift；隔離 CPU-only 新環境已完成 apply、RUNNING、zero drift 與 destroy。

## 1. 先做唯讀檢查

在 repo 根目錄執行；Python 3、kubectl、Helm 與可用的 GKE 認證需先備妥：

```bash
python3 scripts/platform.py check --output /tmp/platform-preflight.json
```

工具明確指定主環境 context，不會改 current-context 或建立任何資源。
可用 `--context NAME` 指定相同架構的其他叢集。任何前置條件不符時 exit code 為 1。
報告不讀取 Secret 內容；Secret 存在不代表 keys、密碼或 SSH 連線已驗證。
GPU 檢查只代表裝置資源已被節點公布，不代表可用配額、CUDA 運算或效能驗收成功。

## 2. 新叢集 bootstrap

Terraform 建立 system／GPU pools 並取得 kubeconfig 後，以驗證模式檢查整條部署鏈：

建立 GPU rehearsal 前先同時檢查區域與專案全域 quota；exit code 1 時不要 apply：

```bash
PYTHONPATH=. .venv/bin/python -m scripts.check_gcp_quota \
  --project YOUR_PROJECT --region YOUR_REGION --gpu-count 1 --spot \
  --output /tmp/gpu-quota.json
```

本輪實測區域 Spot L4 尚有 1，但 `GPUS_ALL_REGIONS` 為 1／1，因此第二個 GPU
pool 建立失敗。Terraform 已銷毀該 rehearsal 的三個資源；證據見
[GPU bootstrap rehearsal](../evidence/gpu-bootstrap-rehearsal-20260921.json)。

唯一的一張 GPU 已由主 cluster 使用時，不應為此建立第二個 GPU cluster；改在既有
cluster 做下列單 GPU 驗收：

1. 保留既有 `gpu-pool` 的一張 L4。
2. 以不請求 GPU 的 MPI JobSet 驗證 API → Kueue → JobSet → rank collection；rank 可共置於同一 GPU node，這不等同 multi-node GPU 運算。
3. 另提交單 GPU runtime workload（request `nvidia.com/gpu: 1`），驗證 CUDA runtime 與 device visibility。
4. 如要展示分享排程，僅在 time-sharing 設定下並行提交最多四個單-share 工作，並明確標示為一張 L4 的 time-sharing，不是多 GPU scaling。

```bash
PYTHONPATH=. .venv/bin/python -m scripts.bootstrap_cluster \
  --context YOUR_NEW_GKE_CONTEXT \
  --output /tmp/cluster-bootstrap-validation.json
```

工具鎖定 JobSet `v0.12.0` 與 Kueue `v0.19.2` 的官方 release URL 及
SHA-256，接著驗證 GPU／system nodes、queue／TAS manifests 與 platform overlay。
預設不變更資源；目前已在主叢集完成這個模式的 server dry-run。

GPU quota 不足時，可在 `gpu_node_count=0` 的全新 rehearsal 使用
`--allow-cpu-only --execute` 驗證 controllers、queues、Secrets 與平台；此模式會
跳過 GPU readiness，不能當作 GPU／MPI acceptance。本輪已完成這條路徑及銷毀，
見 [CPU bootstrap acceptance](../evidence/cpu-bootstrap-acceptance-20260921.json)。

新叢集實際執行前，在 repo 外建立權限受限的 PostgreSQL env file；格式可參考
`k8s/bootstrap/postgres.env.example`，工具會拒絕空值與 `CHANGE_ME`：

```bash
PYTHONPATH=. .venv/bin/python -m scripts.bootstrap_cluster \
  --context YOUR_NEW_GKE_CONTEXT \
  --execute \
  --postgres-env-file /secure/path/postgres.env \
  --output /tmp/cluster-bootstrap.json
```

執行模式安裝釘版 controllers、等待 rollout、建立 namespace、套用 system-pool
placement 與 Kueue 資源、從外部 env 建立 PostgreSQL Secret，並在暫存目錄生成
MPI keys 後直接建立 Secret，最後部署完整平台。既有 Secrets 會保留；報告不包含
密碼、private key 或 Secret YAML。此流程不管理 Terraform state、Artifact Registry
image build 或 DNS／Ingress。

小型單 system-node 叢集在修改 Kueue placement 時無法容納 RollingUpdate 的兩個
500m controller Pods，因此 bootstrap patch 使用 `Recreate`；服務會短暫中斷，
但不會因 surge request 卡在 Pending。正式 HA 環境應增加 system capacity 並重新
評估 rolling strategy。

## 3. 離線渲染與檢視

```bash
python3 scripts/platform.py render --output /tmp/hpc-platform.yaml
helm lint helm/api helm/redis helm/postgres
```

主 overlay 目前產生 13 個資源；沒有內嵌 PostgreSQL Secret，也不建立 Ingress。
API 使用 `mpi-collector-20260921-v1` image；原有 dev CI 不會自動更新這個獨立 values 檔。
後續 image build 仍需明確更新 `api-values.yaml`，不能把本機程式變更視為已部署。

## 4. 部署前必須處理的狀態

1. 確認 system-pool 容量能容納 controllers、平台與 rollout 額外 Pod。
2. 既有環境沿用 `postgres-secret`；新環境先以 repo 外的受限 env file 建立同名 Secret，包含 `POSTGRES_USER`／`POSTGRES_PASSWORD`，與資料庫初始化設定一致。不要將密碼寫入 repo 或渲染檔。
3. JobSet／Kueue controllers、queue、flavor、topology 與 MPI SSH Secret 不在平台 overlay 內；SSH Secret 的建立方式見 [MPI demo](../demo/end-to-end-mpi-jobset-demo.md)。
4. **Redis 遷移**：舊 Deployment 的 AOF 沒有持久 volume。新設定使用 `redis-pvc` 與 `Recreate`，會中斷 Redis。2026-09-21 已在來源所有 DB 均為空的條件下遷移，並完成 Pod 替換驗收。非空環境仍需獨立備份／還原方案，不可直接套用空磁碟。
5. PostgreSQL PVC 保持既有名稱；不刪除 PVC、不以重建代替 migration。

## 5. 狀態妥當後部署與驗收

新增部署入口（需要 requirements.txt 的 PyYAML），先檢查前置條件及 server dry-run：

```bash
PYTHONPATH=. .venv/bin/python -m scripts.deploy_platform \
  --context gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg \
  --output /tmp/platform-deployment.json
```

加入 `--execute` 才會套用 overlay，依序等待 Redis／PostgreSQL／API rollout，
最後執行 DB `create_all`。工具要求明確 context，不建立 controllers、queues 或
Secrets；這是平台部署階段，還不是從空白叢集完成全部 bootstrap。
既有 Redis 必須直接掛載 `redis-pvc` 至 `/data`，否則拒絕部署並要求先完成遷移。
執行中失敗會保留資源與 PVC，JSON 報告記錄最後成功步驟，不做自動資料回滾。
server dry-run 只驗證 API 接受設定，不能證明 Pod 容量、image pull 或 workload 成功。

以下保留對應手動步驟。完整 overlay 尚未在新 cluster 部署，已實際套用的部分見頁首：

```bash
PLATFORM_CONTEXT=gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg
kubectl --context "$PLATFORM_CONTEXT" apply --dry-run=server -f /tmp/hpc-platform.yaml
kubectl --context "$PLATFORM_CONTEXT" apply -f /tmp/hpc-platform.yaml
kubectl --context "$PLATFORM_CONTEXT" -n hpc-platform-dev rollout status deployment/redis --timeout=180s
kubectl --context "$PLATFORM_CONTEXT" -n hpc-platform-dev rollout status statefulset/postgres --timeout=180s
kubectl --context "$PLATFORM_CONTEXT" -n hpc-platform-dev rollout status deployment/api --timeout=180s
kubectl --context "$PLATFORM_CONTEXT" -n hpc-platform-dev exec deployment/api -- python -m api.database.init_db
python3 scripts/platform.py check --output /tmp/platform-after.json
```

驗收需另外確認 PVC Bound、Pod placement、API／DB 連線、MPI rank 輸出，及 Redis 重啟後測試資料保留。
`rollout status` 不等於資料完整性或 benchmark 成功；`create_all` 也不是 schema migration。

## 2026-09-21 實際阻礙

完整 overlay 後續已透過部署工具驗收，見
[部署步驟](../evidence/platform-deployment-20260921.json) 與
[Service／資料保存檢查](../evidence/platform-deployment-health-20260921.json)。
差異僅為 API／PostgreSQL 新增 system-pool nodeSelector；套用後 overlay diff 為空。
Redis 與 PostgreSQL PVC 仍 Bound，既有 MPI job 在兩個資料庫均保留 completed。
以下保留先前盤點找到的問題及修復歷程。

唯讀盤點：兩個 node Ready；API／Redis／PostgreSQL 可用；Kueue controller 可用。
JobSet controller Pending，scheduler 回報 `Insufficient cpu` 與另一節點的 untolerated taint。
system node allocatable CPU 為 1930m，既有 requests 共 1638m，餘額 292m；JobSet controller 要求 500m，因此無法排入。
這是 requests 容量不足的證據，不是 CPU 即時利用率過高的證據。

### 本輪修復與限制

system node 即時用量樣本為 198m（約 10%），Kueue 用量 19m。以小型 demo 的配置將自管 JobSet controller CPU request 從 500m 調為 100m，不增加 CPU limit，也不修改 GKE 系統元件或擴增 VM。controller 已 Running；修復後一個用量樣本為 4m／18Mi。
這是 demo 的初始配置，單次低負載樣本不能當作正式容量規劃；需在工作增多時重新量測。

```bash
kubectl --context "$PLATFORM_CONTEXT" -n jobset-system patch deployment jobset-controller-manager \
  --type=strategic --patch-file k8s/controllers/jobset-demo-resources-patch.yaml
kubectl --context "$PLATFORM_CONTEXT" -n jobset-system rollout status deployment/jobset-controller-manager --timeout=120s
```

request 決定排程預留量，並非 CPU 使用上限，見 [Kubernetes 資源管理](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)。
需要回復原值時可用 `kubectl set resources deployment/jobset-controller-manager -n jobset-system --containers=manager --requests=cpu=500m`，但必須先提供足夠容量，否則會再次 Pending。

### 空 Redis 遷移工具

```bash
.venv/bin/python -m scripts.migrate_redis_empty --output /tmp/redis-migration.json
.venv/bin/python -m scripts.migrate_redis_empty --execute --output /tmp/redis-migration.json
```

第一行只渲染 Redis 的 Deployment／PVC；第二行實際維護。工具需要 PyYAML（requirements.txt 已包含）。
它拒絕任何 DB 有資料、既有同名 PVC、或已掛載持久磁碟的部署，不支援覆蓋或重複遷移。
流程為 server dry-run → 停 API → 暫停 source writes → 再次確認全部 DB 為空 → 套用 PVC／Deployment → 寫測試 key → graceful restart → 驗證 key → 移除測試 key → 恢復 API。
不是非空資料搬移、斷電耐久性、備份還原或 HA 驗證。失敗時保留 PVC，嘗試恢復可連線的服務，並在報告標示是否需人工恢復。

API 設為零副本後，minReplicas 大於零的 HPA 暫停調整，見 [HPA maintenance mode](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)。
來源使用 [CLIENT PAUSE WRITE](https://redis.io/docs/latest/commands/client-pause/) 短暫阻止新的寫入；不是全域交易鎖，工具僅適用此單 Redis demo。

驗收結果：[遷移報告](../evidence/redis-persistence-migration-20260921.json)、[修復後前置檢查](../evidence/platform-preflight-after-20260921.json)。API `/health/redis` 已實測回傳 healthy／connected。

### MPI completion collector

9/21 版本的 `POST /worker/process-next` 需手動從 Redis queue 取出一筆工作並提交
JobSet。JobSet 終止後呼叫：

```bash
curl -X POST http://API_ENDPOINT/worker/collect-mpi
curl http://API_ENDPOINT/jobs/JOB_ID
```

Collector 只掃描 `benchmark=mpi` 且 `status=submitted` 的工作。非終態留在
pending；Completed／Failed 才讀取 launcher log、擷取 ranks、更新 Redis，並
同步 PostgreSQL status。ServiceAccount 可 list Pods／get pod logs，但不可
delete Pods。

2026-09-21 已實測一筆 job 由 accepted → submitted → completed，回收 ranks
0／1／2，Redis/API 與 PostgreSQL 都是 completed。詳見
[lifecycle evidence](../evidence/mpi-api-lifecycle-20260921.json)。當時尚無背景 daemon。
9/22 已由 [自動 worker](automatic-worker.md) 補上 polling 與重啟接續；watch、
跨 Redis／PostgreSQL 原子交易與外部 artifact storage 仍未完成。
