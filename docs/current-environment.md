# 已有結果總覽：不用再開 VM 或重跑測試

以下直接列出 repo 已保存的結果與解讀，沒有要求你執行任何命令。這次只是從現有 JSON／報告整理，不是新實測。每課原本的詳細教學與輸出也已完整放回 docs/week*/ 的 `.md`。

日期和環境各自標示；CPU bootstrap、主平台 CPU MPI、單 L4 訓練是不同驗收，不混成一個從頭到尾都測過的系統。失敗和未完成的部分照實保留。

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

來源：[完整原始驗收 JSON](<evidence/automatic-worker-20260922.json>)。無須再提交一次工作。

### CPU 叢集重建：已保存的驗收結果

日期：2026-09-21。環境：隔離 CPU-only GKE 重建驗收；不是主環境的多 GPU 實驗。該次叢集已清理，讀這份結果不需要重新建立。

```json
{
  "recorded_at": "2026-09-21",
  "scope": "fresh CPU-only GKE bootstrap and platform acceptance; excludes GPU and MPI execution",
  "result": "pass",
  "terraform": {
    "apply": "3 added",
    "post_apply_plan": "No changes",
    "destroy": "3 destroyed",
    "state_resources_after_destroy": 0,
    "cluster_lookup_after_destroy": "404 Not Found"
  },
  "controllers": {
    "jobset": "v0.12.0 Ready on system-pool with 100m CPU request",
    "kueue": "v0.19.2 Ready on system-pool with Recreate deployment strategy"
  },
  "platform": {
    "api": "Running on system-pool; /health healthy",
    "redis": "Running on system-pool; connected; PVC Bound",
    "postgres": "Running on system-pool; jobs table query succeeded; PVC Bound",
    "overlay_diff_after_apply": "empty"
  },
  "security": {
    "postgres_secret": "created from external env file; value not captured",
    "mpi_ssh_key": "generated in temporary directory; value not captured",
    "api_service_account_create_jobsets": "yes",
    "api_service_account_delete_pods": "no"
  },
  "limitations": [
    "gpu-pool had zero nodes because project-wide GPU quota was exhausted",
    "no MPI workload was submitted in this CPU-only rehearsal",
    "database initialization used create_all rather than schema migration"
  ]
}
```

解讀：Terraform 建立 3 個資源、無 drift，JobSet／Kueue controllers 和 API／Redis／DB 驗收成功；create JobSet 權限允許，delete Pod 權限拒絕。最後 destroy 3、state 空、cluster 查詢 404，證明當次隔離叢集已刪除。**不包含 GPU 或 MPI 執行驗收**，也不是所有雲端資源的停費證明。

來源：[原始 CPU bootstrap JSON](<evidence/cpu-bootstrap-acceptance-20260921.json>)。

### Redis 持久化：已保存結果

日期：2026-09-21。環境：`gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg`／`hpc-platform-dev`。驗收前所有來源 DB 為空，不是非空資料備份還原。

```json
{
  "passed": true,
  "steps": [
    {
      "time": "2026-09-21T09:24:19.579997+00:00",
      "step": "preconditions passed",
      "source_uid": "1857a5ad-ebd4-4728-bcf1-49d021c738a6",
      "api_replicas": 1
    },
    {
      "time": "2026-09-21T09:24:20.630917+00:00",
      "step": "API stopped; HPA with minReplicas > 0 is inactive at zero replicas"
    },
    {
      "time": "2026-09-21T09:24:22.142971+00:00",
      "step": "writes paused; all databases confirmed empty"
    },
    {
      "time": "2026-09-21T09:24:23.553226+00:00",
      "step": "Redis deployment and new PVC applied"
    },
    {
      "time": "2026-09-21T09:24:41.853190+00:00",
      "step": "Redis ready",
      "pvc_phase": "Bound"
    },
    {
      "time": "2026-09-21T09:24:55.278216+00:00",
      "step": "marker survived Pod replacement; test marker removed"
    },
    {
      "time": "2026-09-21T09:25:12.885888+00:00",
      "step": "API restored; empty-database migration and graceful restart verified"
    }
  ]
}
```

解讀：PVC Bound 後，測試 marker 在 Pod replacement 後仍存在，API 隨後恢復。這證明當次 graceful Pod replacement 的持久化，不等於磁碟遺失、非空遷移或完整災難恢復。無須你再停一次服務。

來源：[原始 Redis 驗收 JSON](<evidence/redis-persistence-migration-20260921.json>)。

### NetworkPolicy：已保存封包驗證結果

日期：2026-09-21。環境：隔離 `hpc-gpu-sg-rehearsal`，Calico、CPU-only；此叢集已在該次驗收後刪除。

```json
{
  "environment": {
    "cluster": "hpc-gpu-sg-rehearsal",
    "zone": "asia-southeast1-a",
    "lifecycle": "terraform apply then destroy",
    "network_policy": {
      "enabled": true,
      "provider": "CALICO"
    },
    "system_node": {
      "count": 1,
      "machine_type": "e2-standard-2",
      "ready": true
    },
    "gpu_node_count": 0
  },
  "test": {
    "namespace": "network-policy-validation",
    "server": "server:80",
    "policy": "allow-labeled-client-to-server",
    "baseline": {
      "allowed_client_exit_code": 0,
      "denied_client_exit_code": 0
    },
    "with_policy": {
      "allowed_client_exit_code": 0,
      "denied_client_exit_code": 1,
      "denied_client_output": "wget: download timed out"
    },
    "after_policy_delete": {
      "denied_client_exit_code": 0
    }
  },
  "cleanup": {
    "terraform": "0 added, 0 changed, 3 destroyed",
    "state_resources_after_destroy": 0,
    "gke_describe_after_destroy": "404 Not Found"
  },
  "result": "pass"
}
```

解讀：policy 前兩個 client 都成功；套用後 allowed 成功、denied timeout；移除 policy 後 denied 恢復。這支持該次隔離叢集的 ingress 規則有效，**主 hpc-gpu-sg enforcement 仍關閉**。不需要你再開 VM 重測。

來源：[原始 NetworkPolicy JSON](<evidence/network-policy-validation-20260921.json>)。

### 單 L4 訓練：已保存的實測數據

日期：2026-09-22；環境：GKE hpc-gpu-sg、單 NVIDIA L4、PyTorch 2.12.0+cu126。模型為 13M causal LM、byte tokenizer，不是 pretrained 大模型。20 warmup、40 measured steps，各 batch 三次交錯量測。

| Batch | 次數 | Mean byte tokens/s | Mean step ms | Peak allocated MiB | Throughput CV |
|---:|---:|---:|---:|---:|---:|
| 8 | 3 | 110,785 | 18.50 | 375.02 | 3.21% |
| 16 | 3 | 200,841 | 20.39 | 532.39 | 0.42% |

結果：吞吐 **+81.29%**，每步時間 **+10.25%**，顯存峰值 **+41.96%**。每步工作量加倍，所以不是「每步變快」，也不能推出模型品質更好。

另做的五步 CUDA profiling：batch 8／16 的 multi-tensor kernel 累積時間約 21.71／21.72 ms，GEMM 約 12.27／23.84 ms。這支持每步固定 optimizer 成本被較大 batch 攤薄的推論；kernel 時間總和不是 wall time，也不直接證明 compute-bound 或 memory-bound。

你不需要再跑 GPU：[保存的摘要](<../benchmark/results/causal-lm-20260922/summary.json>)、[原始逐步數據](<../benchmark/results/causal-lm-20260922/result.json>)、[完整解讀與限制](<performance/causal-lm-l4-20260922.md>)已足夠直接閱讀。

### 已保存的 Slurm CPU 多節點结果

環境：歷史 hpc-demo controller／compute-01、compute-02 CPU VM；不是目前 GKE／GPU。日期依下方原始教材，未另推定新日期。

```text
JOB_ID=14
NODELIST=compute-[01-02]
NTASKS=4
Hello from rank 0 out of 4 processes
Hello from rank 1 out of 4 processes
Hello from rank 3 out of 4 processes
Hello from rank 2 out of 4 processes
```

這證明該次 allocation 和四 ranks 啟動。後來的失敗紀錄為 `State=DOWN+NOT_RESPONDING`、job PENDING，原因是 VM 已不存在但 Slurm 仍留節點設定；沒有修復成功紀錄，不能寫成成功恢復。完整原文與输出保留在下方，不需重建 VM。

### 已保存的 Ray 結果

環境：獨立 Ray 2.47.1 CPU cluster，namespace ray-system；時間依下方原始紀錄，不冒充今天的服務狀態。

```text
{'CPU': 1.0, 'GPU': 1.0}: 1+ pending tasks/actors

attempt_number: 0
state: FAILED
error_type: NODE_DIED

attempt_number: 1
state: RUNNING
```

前一個案例是 CPU Ray cluster 無法滿足 GPU task，Pod Running 不代表 task 可排程。後一個是另一項故障實驗：worker 消失後 task 在其他 Ray node 重試到 RUNNING；沒有最終 SUCCEEDED 證據。兩個案例不可混成同一工作。下方保留原始教學與輸出，無須再開服務。

### 已保存的本機驗證結果

2026-09-22 教材改寫時，在此 repo 開發環境執行並記錄：`53 passed`；三個 Helm charts lint 通過，完整主 overlay 離線渲染出 14 個物件。這是本機測試與渲染結果，**不是遠端 GitHub Actions 整條 CI 成功，也不是新雲端驗收**。

目前 CI 改的是 values-dev.yaml，主 overlay 使用獨立 api-values.yaml，因此不能說 push 一定更新主展示。下方完整保留原本課程與當時輸出；不要求你再跑一次 pytest。

## VM 刪除與這份文件的關係

閱讀上面的結果不依賴 VM 還活著。這份文件沒有刪除 VM，也不能證明目前所有付費資源已停用。若 repo 或尚未回收的 log 只存在待刪 VM 磁碟上，刪除前要先確認已有另一份可取得的備份；現有文件不能替不存在的備份作保證。
