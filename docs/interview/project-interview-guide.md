# HPC AI Performance Engineering Platform — Project Interview Guide

2026-09-22 更新：自動 worker 已完成重啟接續驗收，單 L4 causal LM 已保存
新 CUDA traces。現行完整展示見 [本輪 demo](../demo/interview-demo-20260922.md)。
文末保留 9/21 的後續優先順序，作為歷史規劃；不能將它當成本輪未完成清單。

本指南以 [Final Architecture](../architecture/platform-architecture.md)、[Evidence Index](../evidence/README.md) 與保存的 demo 為依據。回答區分已驗證結果、架構設計與未完成工作；不把歷史環境描述為即時 cluster 狀態。

## 30 秒版本

我用 FastAPI、Redis、PostgreSQL、Kueue 和 JobSet 建立可自動提交與回收 MPI 結果的平台，驗證 worker 重啟後接續執行與 DB 狀態回寫。效能方面，在單 L4 上用固定 13M causal LM 比較 batch 8／16，分開記錄 throughput 與 CUDA profiler，展示效能收益、延遲和記憶體代價。兩條路徑各有實測證據與明確範圍。

## 2 分鐘版本

1. **問題**：單獨跑通 benchmark 不足以展示平台能力，因此我把 submission、queue、admission、execution 與 troubleshooting 分層，讓每個成果都有 evidence。
2. **Main E2E**：API 建立 job ID、commit DB 後發布 Redis job／queue；獨立 polling worker 自動建立動態 JobSet 並收集終態。
3. **Scheduling**：Kueue 管 queue、quota、ResourceFlavor 與 TAS；Pod placement 最後由 Kubernetes Scheduler 處理。另有 priority／preemption 的歷史驗證。
4. **Distributed execution**：JobSet 管 launcher／worker grouping，launcher 經 DNS／SSH 用 mpirun 啟動三個 ranks。這是 CPU MPI workload，三個 worker Pods 不等於三台實體 nodes。
5. **Performance／Observability**：本輪 L4 BF16 Transformer 重複量測顯示 batch 8→16 tokens/s +74.4%、step latency +14.0%、memory +50.8%；固定組 vLLM JSON 另顯示 concurrency 32→64 throughput +29.6%、TTFT +137.8%。
6. **Failure troubleshooting**：以 JobSet exit 42、Ray NODE_DIED、Slurm node 不回應、NCCL Socket fallback 展示不同 failure domains。Ray／Slurm 是平行案例，未串入 API。
7. **Current boundary**：自動 polling worker／collector 和重啟接續已驗證；artifact storage、跨資料庫原子交易、完整 GitOps 尚未完成。訓練 benchmark 尚未接入 MPI dispatcher。

## Architecture Questions

### 為什麼 Redis + PostgreSQL 都需要？

Redis 承載 job queue 與 API 查詢使用的即時 job state，PostgreSQL 保存初始 metadata。這讓排隊操作與結構化保存有不同責任，但目前 DB 還不是完整 lifecycle 的唯一真相來源。兩者寫入沒有跨系統 transaction，失敗一致性也是後續要補的部分。

### Kueue 與 Kubernetes Scheduler 差在哪？

Kueue 在 workload 層處理 queue、quota、flavor 與 topology admission。Kubernetes Scheduler 處理已建立 Pod 的 node placement。因此排障要先看 Workload 是否 Admitted，再看 Pod 是否 Scheduled，不能將兩層 Pending 混在一起。

### JobSet 解決什麼？

MPI 有 launcher 與多個 worker child Jobs，需要共同管理。JobSet 提供 grouping、DNS 與 failure policy，使 child Job failure 可觸發整組 Recreate。它不等於 checkpoint 系統，也不會替 API 自動收回 benchmark result。

### 為什麼 system-pool / gpu-pool 分開？

system-pool 承載 CPU platform services，gpu-pool 提供 L4 workload 資源，讓服務與 compute 工作有清楚部署分工。Node Pool 是 nodes 的管理群組，不是單一 node，也不是 GKE managed control plane。現有主 overlay 已用 nodeSelector 指定 API／Redis／PostgreSQL 到 system-pool，已完成 rollout 與實際 Pod placement 驗收。

### Taint / Toleration 的作用？

GPU pool 的 `nvidia.com/gpu=present:NoSchedule` 會排除沒有對應 toleration 的 Pod。主 MPI 整合曾因此卡在 Kueue topology admission，補上 launcher／worker tolerations 後成功執行。Toleration 只提供允許條件，不代表強制選 GPU node，更不代表 workload 實際使用 GPU。

### 為什麼 API 使用專用 ServiceAccount？

API 要建立 JobSet，需有明確 Kubernetes identity。`api-jobset-runner` 只在 hpc-platform-dev 授予 JobSet get／list／watch／create，避免給 cluster-admin。這是 Kubernetes resource 權限，不等於 HTTP API 已有完整使用者 authentication。

### Worker 如何自動執行並在重啟後接續？

2026-09-22 已拆成獨立 `api-worker`，每五秒掃描 Redis 的持久化 job records，
以可續期 lease 協調同一 job。固定 JobSet name 與 owner label 防止重試時建立
第二份資源；submitted 工作自動輪詢終態，先寫 DB 再發布 Redis result。
實機驗證兩個階段的 worker 停啟接續。仍不保證跨 DB／Redis 原子交易或 exactly-once。

## Distributed / HPC Questions

### MPI launcher / worker 怎麼運作？

Renderer 同時替換 JobSet 名稱與三個 worker DNS，launcher 等待 SSH 可用後執行 mpirun。Worker 容器提供 sshd，三個 ranks 輸出 rank／hostname。Template 以 launcher successPolicy 與 child Job deadline 結束工作；這證明 distributed launch，不是 GPU performance 測試。

### Slurm 與 Kubernetes / Kueue 差在哪？

Slurm 案例以 partition、node allocation 與 sbatch 管理 CPU HPC 工作，再由 mpirun 啟動 ranks。Kubernetes 管 Pod lifecycle／placement，Kueue 補 workload queue／admission。本 repo 驗證的是兩條獨立路徑，沒有把 Slurm 接在 Kubernetes 主 E2E 後面。

### Ray scheduler 與 Kubernetes scheduler 的責任差異？

Kubernetes 決定 Ray head／worker Pods 放在哪些 nodes，Ray 再分配 task／actor 所需的 runtime resources。歷史案例 Pods Running，但 Ray GPU=0，要求 num_gpus=1 的 task 仍 pending。因此應檢查 Ray resource demand／availability，不能只看 Pod 健康。

### JobSet recovery 與 Ray retry 的差異？

JobSet 案例在 worker exit 42 後整組 Recreate launcher／workers。Ray 案例則對失敗 task 依 max_retries=2 重試，另由 KubeRay 補 worker Pod。Ray evidence 到另一 node 的 attempt 1 RUNNING，JobSet evidence 到 JobsReady，兩者都不應延伸成 application state 完整復原。

### DDP / AllReduce / NCCL 的角色？

DDP 組織多個 training processes 的資料平行訓練，AllReduce 是聚合並分發結果的 collective，可用於梯度同步。NCCL 提供 NVIDIA GPU collective communication backend。本 repo 的 DDP profiling 是 CPU／Gloo，NCCL 是獨立單 GPU 實驗，不能合併宣稱已做 multi-GPU training scaling。

### NCCL 為什麼 fallback 到 Socket？

Raw log 顯示 SPCX plugin 可載入，但 NET/IB 找不到 device，SPCX／IB network 初始化失敗。之後 Socket 初始化並被指定給 communicator，最後 Init COMPLETE。環境沒有 RDMA hardware，而且只有一個 rank，所以證明 backend selection，不是跨 node transport performance。

## Performance Questions

### vLLM concurrency 16 / 32 / 64 看到了什麼？

固定 128 requests 的 throughput 是 16.748／24.988／32.379 req/s，mean TTFT 是 135.601／188.663／448.579 ms。Concurrency 提高持續帶來吞吐量，但 64 的首 token 等待增幅更大。數據來自 Qwen2.5-0.5B-Instruct 的保存結果，不是所有模型／GPU 的容量結論，詳見 [Performance Report](../performance/performance-report.md)。

### Throughput 與 TTFT tradeoff 怎麼判讀？

16→32 的 throughput 增加 49.2%、TTFT 增加 39.1%，32→64 則是 29.6% 與 137.8%。因此後一段的 latency 代價增長更快，可列為 saturation candidate。沒有 latency SLO、重複測量與更多測點時，不能直接宣稱 concurrency 32 是最佳設定。

### 怎麼判斷 bottleneck？

先固定 workload 條件，將 latency／throughput 變化與 profiler、資源 metrics 對照。CPU DDP 歷史 profiler 中 addmm／mm 合計約 67% CPU time，支持當次 matrix compute 佔主要時間，但不同 worker run 的 limits／profiling 條件也需考慮。接著應控制單一變因再驗證，而不是由一個 utilization 值直接宣判硬體瓶頸。

### Profiler、DCGM、Prometheus 各負責什麼？

Profiler 對應 application operators 與執行時間，DCGM 提供 GPU telemetry，Prometheus 收集 time-series metrics 供跨層對照。它們分別回答時間花在哪裡、GPU 狀態如何、指標如何隨時間變化。Repo 的 dashboard 驗證含歷史 P100 環境，不能直接稱為本次 L4／MPI job 的關聯分析。

### 為什麼不能拿 single-node iperf3 當實體 network bandwidth？

Client／server Pods 在同一 node，流量路徑可能主要位於該 host 的 networking stack。18.8 Gbit/s 證明當次 Pod／Service TCP 路徑的吞吐量，不代表跨主機 NIC 上限。紀錄還有 10367 retransmissions，缺少額外 counters／packet evidence，不能單靠吞吐量宣稱網路完全健康。

## Failure / Troubleshooting Questions

### JobSet worker exit 42 後發生什麼？

歷史 mpi-real 的 worker hook 偵測 `/tmp/fail-worker` 後 exit 42，child Job failure 觸發 RestartJobSet。Policy 設 maxRestarts=1、Recreate，結果保存 restarts=1 與 JobsReady。這沒有證明動態 mpi-<job_id> 已重跑 recovery，也沒有 checkpoint 或 benchmark completion evidence，見 [JobSet demo](../demo/jobset-recovery-demo.md)。

### Kueue TAS admission blockage 怎麼定位？

唯一 GPU node cordon 後，歷史 event 顯示沒有 hostname topology domains，workload 未 admission、Pod 尚未建立。Uncordon 後出現 QuotaReserved=True／Admitted=True。這是 scheduling availability injection，不是真實硬體 failure 或 multi-node failover。

### Ray NODE_DIED 後怎麼確認 recovery？

先確認 attempt 0 FAILED／NODE_DIED，再看 attempt 1 的位置與 state。歷史紀錄指出 task 在另一 Ray node RUNNING，KubeRay 同時補回不足的 worker Pod。沒有保存最終 SUCCEEDED，所以回答限定 task retry 已啟動，見 [Ray demo](../demo/ray-worker-recovery-demo.md)。

### Slurm DOWN+NOT_RESPONDING 的根因是什麼？

從 sinfo、scontrol node state、squeue pending reason 一路追到 GCE VM 已不存在，但 slurm.conf 還保留 compute-01／02。Controller 沒有 slurmd heartbeat，因此 node 不可用，job PENDING。Accounting storage disabled 也限制 sacct 歷史查詢，案例只有根因定位、沒有修復成功證據，見 [Slurm demo](../demo/slurm-failure-troubleshooting-demo.md)。

### NCCL NET/IB No device found 是否表示整個 NCCL 失敗？

不能只看單一錯誤行，還要看後續 backend 與 communicator 初始化。這份 log 後續選到 Socket 並 Init COMPLETE，因此 NCCL 初始化成功但沒有 RDMA path。只有 1 GPU／1 rank／1 node，沒有 ib_write_bw、RoCE／PFC／ECN validation，見 [NCCL demo](../demo/nccl-transport-fallback-demo.md)。

### GKE GPU taint 問題如何解決？

主 E2E 原先因 launcher／worker 缺 toleration，GPU node 被 Kueue topology placement 排除，JobSet 維持 suspended。補上對應 `nvidia.com/gpu=present:NoSchedule` toleration 後 admission 成功並看到 ranks。這是 workload eligibility 修正，不是移除 GPU pool 的隔離條件，也不是保證 GPU 計算，見 [主 E2E](../demo/end-to-end-mpi-jobset-demo.md)。

## Honest Limitations

目前有 automatic polling worker／collector 與重啟驗證；仍缺 artifact object storage、跨 Redis／PostgreSQL 原子交易與完整 lifecycle state machine。没有 multi-node GPU scaling／RDMA，也未完成主 E2E GitOps alignment。Redis 非空備份還原、schema migration 與整體 HA 仍待補強；Ray／Slurm 未接 API。

以下保留 2026-09-21 當時的開發排序（1／2 的背景 worker 與 polling 已於 9/22 補上；不是職缺原文）：

1. 先明確定義 durable job state、dispatch 冪等與 queue／DB 失敗處理，再引入獨立 worker daemon。
2. 將手動 completion collector 改成 background watch／reconciliation，補 retry 與補償流程。
3. 把 launcher log 與大型結果移至 object storage，API 只保存 artifact metadata。
4. 對齊 IaC／GitOps、Redis persistence 與 Alembic，提升新環境重現能力。
5. 有對應 GPU／RDMA hardware 後，再做受控 multi-node scaling 與 network benchmarks。
