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

記錄的 API 維護區間約 52 秒，不是外部連續探測得到的精確停機 SLA。API `/health/redis` 後續實測 healthy／connected。
此案例驗證空資料庫遷移與正常重啟後持久化，未驗證非空資料搬移、硬斷電或跨節點 HA。

## 3. 舊 MPI 工作：有定位，未修復

原 JobSet `mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899` 的四個 Pending Pods 被 TAS 指定到已不存在的 hostname `gke-hpc-gpu-sg-gpu-pool-9ad99345-3dzb`。
目前 GPU node 是 `gke-hpc-gpu-sg-gpu-pool-9ad99345-jz5j`。

工具確認沒有 Running Pods 後嘗試停用／重新啟用 Workload，但舊 admission 未能清除。[結果](../evidence/mpi-placement-recovery-20260921.json) 為 `reactivated=true`、`placement_recovered=false`。
Kueue v0.19.2 的 controller 日誌回報：

```text
Updating reclaimable pods
admission webhook "vworkload.kb.io" denied the request:
status.reclaimablePods[launcher]: Required value: cannot be removed
```

Workload 保留 `reclaimablePods: [{name: launcher, count: 1}]`，而 JobSet 已在 restart 流程中。
這是本次觀察到的 reconciliation 阻礙，不直接推論所有相同版本都存在同樣問題。
未關閉 webhook、未強改 status、未刪除歷史 JobSet。下一步需另備狀態快照，評估升級修正或受控重建該 demo 工作。

恢復工具預設只檢查；以下加入 `--execute` 才會重新准入：

```bash
.venv/bin/python -m scripts.recover_stale_placement WORKLOAD_NAME --output /tmp/placement-check.json
```

工具支援的 Active 開關行為見 [Kueue Workload 文件](https://kueue.sigs.k8s.io/docs/concepts/workload/)。此版本工具未能修復上述舊狀態，不能把它列為成功恢復 evidence。

## 4. 新 MPI 工作：Completed 與 ranks 成功

直接以 repo renderer 產生新 JobSet `mpi-validation-20260921`，server dry-run 通過後建立。
更新模板：移除 rank shell 的 `sleep 900`、以 launcher 作為 successPolicy 目標，launcher／worker child Jobs 設定 300／330 秒執行期限。
deadline 不包含排隊等待，而且 failurePolicy 最多仍可重建一次，不是全流程的 330 秒總 timeout。

JobSet 最終 `Completed=True`、restarts=0。Launcher log：

```text
RANK=1 HOST=mpi-validation-20260921-worker-1-0
RANK=2 HOST=mpi-validation-20260921-worker-2-0
RANK=0 HOST=mpi-validation-20260921-worker-0-0
```

完成後 worker Pods 已收尾，launcher Pod 保留 Succeeded。保存的 [JSON](../evidence/mpi-validation-20260921.json) 含 UID、時間、條件、log 與剩餘 Pod placement。
可再次唯讀收集：

```bash
.venv/bin/python -m scripts.collect_mpi mpi-validation-20260921 \
  --timeout 5 --output /tmp/mpi-validation.json
```

成功条件需同時滿足 `Completed=True` 與 ranks 0／1／2。依據 [JobSet successPolicy](https://jobset.sigs.k8s.io/docs/reference/jobset.v1alpha2/)，launcher 完成即可讓整組工作成功。

**範圍：** CPU MPI rank smoke test，直接提交 JobSet；不是多 GPU 效能、跨實體節點 scaling，也沒有驗證 API final-state sync。API 的舊 image 仍是 jobset-dispatch-v4，尚未包含新模板。
