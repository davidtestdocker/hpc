# 自動 MPI 工作流程

日期：2026-09-22。主環境 `hpc-gpu-sg`、namespace `hpc-platform-dev`。

`api-worker` 使用與 API 相同的映像、Redis／PostgreSQL 設定和最小 RBAC，
以獨立 Deployment 在 system-pool 執行 `python -m api.worker`。
每五秒掃描 Redis job records：accepted／retrying／processing 提交工作，
submitted 查詢 JobSet 終態並回收 launcher log／rank，DB 回寫成功後才發布 Redis 終態。
本次 MPI 是 CPU rank smoke test，不是 GPU 或 MPI 吞吐量 benchmark。

## 操作

程式閱讀順序：`api/main.py:create_benchmark` 建立工作 →
`api/worker.py:run` 定期呼叫 `tick` → `reconcile_job` 依狀態提交或收集 →
`api/workloads/dispatcher.py`／`collector.py` 呼叫 Kubernetes → 回寫 DB／Redis。
這些入口及 `helm/api/templates/worker.yaml` 已補中文流程與設計註解。

主 overlay 的 `worker.enabled: true` 同時啟用背景 worker 並關閉三個手動
`/worker/*` endpoint（回傳 409）。使用 `POST /benchmark` 提交 MPI，再以
`GET /jobs/{job_id}` 查詢；不需要呼叫 dispatch 或 collect endpoint。

```bash
kubectl --context gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg \
  -n hpc-platform-dev port-forward service/api-service 18081:8000
curl -fsS -X POST http://127.0.0.1:18081/benchmark \
  -H 'Content-Type: application/json' -d '{"benchmark":"mpi"}'
```

部署沿用 `scripts.deploy_platform.py`；該工具也等待 worker rollout。
健康排查先看 `deployment/api-worker` 日誌，再查 JobSet／Kueue 狀態。
JobSet 長期 Pending 不等於 worker 壞掉，應確認 admission 與 node placement。

## 重啟與失敗

- 每個 job 使用 120 秒 Redis lease，每 30 秒續期；依賴故障記錄於日誌並在下輪重試。
- JobSet 名稱由 job ID 決定。create 回傳 409 時，僅接回 owner label 相符的資源，避免重複執行。
- worker 掃描持久化 job record，因此程序在提交前或提交後重啟都可以接續。
- Redis 狀態與 queue publication／cleanup 各自使用 transaction。終態 DB 先寫，Redis 後寫；失敗可重試。
- `simulate_failure: true` 為 dispatch 測試，三次後 failed 並進 dead-letter queue；它不模擬 MPI kernel failure。
- 已完成工作以 `worker:done:<id>` 標記，避免反覆讀取 DB。仍保留 API 結果與原始 JobSet。

此版本依賴 Redis PVC，尚無跨 DB／Redis 原子交易、Redis 資料全失恢復或
exactly-once 保證。DB insert 成功、Redis publication 失敗時可能留下 DB-only
accepted row，API 不會回傳成功；這種情況尚需人工核對。log 仍保存在 Redis，
object storage、歷史結果清理和大規模索引另待補強。

## 驗收

```bash
PYTHONPATH=. .venv/bin/python -m scripts.validate_automatic_worker \
  --context gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg \
  --url http://127.0.0.1:18081 --execute \
  --output /tmp/automatic-worker-validation.json
```

腳本會提交三筆工作並短暫停啟 worker：驗證 queued restart、提交後 collector
restart、正常完成、模擬 dispatch 重試耗盡；finally 恢復 worker 副本。
只適合 demo 維護時段。結果見 [本輪證據](../evidence/automatic-worker-20260922.json)。

本輪結果：兩筆 MPI 自動 completed 且包含 ranks 0／1／2；停啟後只存在一個
對應 JobSet；一筆 simulated dispatch failure 三次後 failed。PostgreSQL 狀態
一致，job_queue／processing_queue 為空，失敗 ID 位於 dead-letter；三個手動
端點皆回傳 409。新映像 digest 為
`sha256:c333faed0680094ea940d8548d212d71745084be6ecf6b52b38d079d3ac84a29`。
