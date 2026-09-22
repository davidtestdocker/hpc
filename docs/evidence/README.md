# Platform Evidence Index

## 2026-09-22 訓練與 profiling

[13M causal LM 報告](../performance/causal-lm-l4-20260922.md) 對應
[raw artifact bundle](../../benchmark/results/causal-lm-20260922/evidence.json)：
六次交錯 batch 8／16 量測、兩份 CUDA traces、文字快照、image digest、hashes 與
GPU 遙測。byte-token throughput +81.29%，step latency +10.25%，peak memory +41.96%。
小型模型、單 L4、byte tokenizer 的結果不可延伸為大型 pretrained LLM 或 multi-GPU。
實驗後主平台檢查見 [preflight](platform-after-training-20260922.json)。

## 2026-09-22 自動流程更新

[自動 worker 驗收](automatic-worker-20260922.json) 保存兩筆真實 CPU MPI
自動 completed、ranks 0／1／2、唯一 JobSet、queued／submitted 兩階段 worker
停啟接續，以及三次 simulated dispatch failure 後 failed。操作見
[runbook](../runbooks/automatic-worker.md)。下方 9/21 手動流程紀錄保留為歷史，
其中「缺 worker daemon／持續 reconciliation」已由本次背景 polling 補上；
artifact storage、跨資料庫原子交易與 watch 仍未完成。

## 2026-09-21 現況盤點

[Preflight JSON](platform-preflight-20260921.json) 是本輪唯讀實測：node、Kueue 與 queue 前置條件通過；JobSet controller 未就緒，整體結果為失敗。system node 的 CPU requests 餘額 292m 小於 controller 的 500m，詳見 [runbook](../runbooks/platform-bootstrap.md)。

後續已套用 controller 修復與 Redis Deployment／PVC。[修復後 preflight](platform-preflight-after-20260921.json) 全部通過；[Redis 遷移報告](redis-persistence-migration-20260921.json) 保存空資料庫檢查、API 維護與恢復，以及 test key 在 Pod 替換後保留的結果。其餘主 overlay 尚未完整部署；不是從零重建、非空資料搬移或 MPI 成功的證據。以下索引保留歷史驗證範圍。

另以新模板直接提交 MPI JobSet，[驗收 JSON](mpi-validation-20260921.json) 保存 Completed 與 ranks 0／1／2，非 API lifecycle 或效能測試。[舊工作恢復嘗試](mpi-placement-recovery-20260921.json) 則失敗，不能與新工作成功混用；根因與操作見 [修復 demo](../demo/platform-recovery-20260921.md)。

[Terraform 對齊證據](terraform-gpu-sg-20260921.md) 記錄主環境三個資源 import 後零 drift，以及隔離 CPU-only cluster 的 apply／RUNNING／zero drift／destroy。remote state 與全新 GPU cluster 的完整 bootstrap 尚未驗證。

[Bootstrap validation](cluster-bootstrap-validation-20260921.json) 記錄 system／GPU node
前置條件、JobSet v0.12.0／Kueue v0.19.2 官方 manifests checksum，以及
queue／TAS 與[完整平台](cluster-bootstrap-validation-platform-20260921.json)的 server
dry-run 全部通過。`execute=false`，因此只證明 bootstrap 實作與現有 API 相容，
尚未證明全新 GPU cluster 的 install／rollout／MPI acceptance。

[GPU bootstrap rehearsal](gpu-bootstrap-rehearsal-20260921.json) 保存全新 Spot L4
叢集的真實嘗試：control plane 與 system-pool 建立成功，但 GPU pool 被專案全域
`GPUS_ALL_REGIONS=1/1` 阻擋；區域 Spot L4 本身為 0/1。Terraform 隨後完成
3-resource destroy、state 空白且 cluster 查詢 404。[Quota preflight](gpu-quota-preflight-20260921.json)
現在能在 apply 前檢出同一限制。

[CPU-only bootstrap execution](cpu-bootstrap-execution-20260921.json) 與
[acceptance](cpu-bootstrap-acceptance-20260921.json) 證明全新 GKE 從釘版
controllers、Kueue resources、兩個 runtime Secrets 到三個平台服務皆可建立；
LocalQueue Active、PVC Bound、API／Redis healthy、DB table 可查、RBAC allow／deny
與 overlay zero-diff 均通過。最後 Terraform destroy 3、state 空白、GKE 404。
此結果刻意排除 GPU readiness 與 MPI execution。

[NetworkPolicy 封包證據](network-policy-validation-20260921.json) 保存隔離 Calico GKE 的 policy 前 baseline、explicit allow、deny timeout 與移除 policy 後恢復。測試叢集已 destroy；主 `hpc-gpu-sg` enforcement 仍關閉。

[MPI API lifecycle](mpi-api-lifecycle-20260921.json) 保存新 image rollout、API job accepted／submitted／completed、JobSet terminal condition、ranks 0／1／2、Redis/API 與 PostgreSQL status 一致，以及 collector 最小 RBAC 驗收。

[最終 preflight](platform-preflight-final-20260921.json) 是 collector rollout 與 lifecycle 驗收後的唯讀檢查，10 項前置條件全部通過；它不取代 workload 成功證據。

[Bootstrap rehearsal 後 preflight](platform-preflight-post-bootstrap-20260921.json)
再次確認主叢集的 10 項前置條件全部通過，證明隔離 Terraform states 的建立／銷毀
沒有改動主環境；它同樣不取代 MPI lifecycle evidence。

此索引將 HPC AI Performance Engineering Platform 的能力對應到 repo 內實作、原始結果與實驗紀錄。架構分工見 [Final Architecture](../architecture/platform-architecture.md)，主展示入口為 [MPI E2E demo](../demo/end-to-end-mpi-jobset-demo.md)。Supporting experiments 與主線平行，沒有 MPI → Ray → Slurm 的自動 pipeline。

## Evidence 使用方式

[完整 overlay 部署](platform-deployment-20260921.json) 保存既有主 GKE 的 apply、
三個服務 rollout 與 DB 初始化；[部署後健康檢查](platform-deployment-health-20260921.json)
驗證 API Service、Redis 連線及既有 MPI job 在 API／PostgreSQL 仍為 completed。
這是既有叢集部署驗收，尚未證明空白叢集完整 bootstrap。

[平台部署 dry-run](platform-deploy-dry-run-20260921.json) 記錄新增部署工具在主 GKE
通過前置檢查、Redis storage guard 與 server dry-run。此次 `execute=false`，
未套用完整 overlay，不代表新叢集 bootstrap 或 rollout 已驗證。

- **實作／設定**：程式與 manifest 證明 repo 保存了什麼；不單獨代表 runtime 驗證成功。
- **結果 artifact**：保存的 JSON／log，可直接檢查該次輸出；仍需遵守當時環境與 workload 限制。
- **歷史紀錄**：Week 文件或 demo 內保存的指令、事件與結果；不是本輪重跑結果，也不是即時 cluster 狀態。只有文件摘錄時，不宣稱另有完整 raw capture。

## Capability Evidence

| Capability | Evidence | What was verified | Limitation |
|---|---|---|---|
| Main MPI E2E | [9/22 自動驗收](automatic-worker-20260922.json)、[9/21 手動歷史驗收](mpi-api-lifecycle-20260921.json)、[worker](../../api/worker.py)、[collector](../../api/workloads/collector.py) | 自動提交／收集 MPI、queued／submitted 重啟接續、ranks 0／1／2、DB 狀態及失敗 dead-letter 核對 | CPU MPI rank smoke test，非 GPU 效能；仍缺 artifact storage、跨 DB 原子交易和 Redis 全失恢復 |
| Kueue TAS | [TAS 實驗紀錄](../history/20260922-before-current/week19/day6-topology-aware-gpu-scheduling.md.txt)、[Topology](../../k8s/gpu-scheduling/topology.yaml)、[ResourceFlavor](../../k8s/gpu-scheduling/resourceflavor.yaml) | hostname topology request、topologyAssignment 與兩個 Pod 的 same-hostname placement | 歷史環境單 GPU node；Pod 最後仍為 ContainerCreating，只驗證 placement；未驗證 multi-node／cross-zone 選擇 |
| Kueue Priority / Preemption | [preemption 紀錄](../history/20260922-before-current/week19/day4-priority-preemption-multi-tenancy.md.txt)、[ClusterQueue](../../k8s/gpu-scheduling/clusterqueue.yaml)、[PriorityClass](../../k8s/gpu-scheduling/priorityclasses.yaml) | Low workload 被 evict、quota 釋放、high workload admitted 並 Running | 執行證據在 Week 文件；同一 ClusterQueue、單 L4 time-sharing shares，不是四張實體 GPU，也不是完整 tenant isolation |
| JobSet Recovery | [JobSet recovery demo](../demo/jobset-recovery-demo.md)、[failure／recovery 紀錄](../history/20260922-before-current/week20/day4-ha-node-failure-recovery.md.txt)、[固定名稱 example](../../k8s/gpu-scheduling/examples/jobset-mpi.yaml)、[目前動態 template](../../api/workloads/templates/jobset-mpi.yaml) | Worker exit 42 → RestartJobSet／Recreate → restarts=1、JobsReady；另記錄 cordon／uncordon admission blockage | Recovery evidence 來自歷史 mpi-real；未另證明動態 JobSet 本次也做過 fault injection；cordon 不是硬體故障，單 GPU node 無 node failover |
| Ray Resource Mismatch | [Ray supporting demo](../demo/ray-worker-recovery-demo.md)、[RayJob](../../ray-resource-mismatch-job.yaml)、[排障紀錄](../history/20260922-before-current/week20/day5-ai-hpc-production-troubleshooting.md.txt)、[RayCluster](../../ray-cluster.yaml) | Pods Running、Ray GPU=0，但 num_gpus=1 task pending；定位 Ray scheduler resource mismatch | CPU Ray cluster 的歷史紀錄；不是 GPU Ray workload 成功執行證據，未接入主 API |
| Ray NODE_DIED Retry | [Ray recovery demo](../demo/ray-worker-recovery-demo.md)、[recovery RayJob](../../ray-worker-recovery-job.yaml)、[runbook](../runbooks/ai-hpc-job-troubleshooting.md)、[實驗紀錄](../history/20260922-before-current/week20/day5-ai-hpc-production-troubleshooting.md.txt) | attempt 0 NODE_DIED 後，以 max_retries=2／soft affinity 在其他 Ray node 開始 attempt 1；KubeRay 另補 worker Pod | 保存的證據到 retry RUNNING；不額外宣稱最終 SUCCEEDED、Actor state recovery 或 exactly-once |
| Slurm Multi-node MPI | [Slurm supporting demo](../demo/slurm-failure-troubleshooting-demo.md)、[multi-node 紀錄](../history/20260922-before-current/week17/day4-slurm-multinode-hpc-cluster.md.txt)、[MPI sbatch](../../mpi-multinode.slurm)、[MPI source](../../mpi_hello.c) | compute-01／02 的 Slurm allocation、4 tasks 與 mpirun rank 輸出；PMI 相容性排障 | 歷史 CPU VM 環境；無 shared filesystem；multi-node OSU benchmark 未完成，非 GPU Slurm evidence |
| Slurm Node Failure Troubleshooting | [Slurm troubleshooting demo](../demo/slurm-failure-troubleshooting-demo.md)、[排障紀錄](../history/20260922-before-current/week20/day5-ai-hpc-production-troubleshooting.md.txt)、[runbook](../runbooks/ai-hpc-job-troubleshooting.md)、[pending script](../../slurm/pending-cpu-test.sbatch) | Node DOWN+NOT_RESPONDING、job PENDING；追到 compute VM 已不存在而 slurm.conf 仍保留 | 未宣稱恢復成功；accounting storage disabled，無 sacct／SlurmDBD 歷史查詢能力 |
| NCCL Transport Fallback | [NCCL fallback demo](../demo/nccl-transport-fallback-demo.md)、[原始 NCCL log](../../benchmark/results/week16-day4-nccl-single-gpu.txt)、[transport 排障紀錄](../history/20260922-before-current/week18/day5-nccl-transport-debugging.md.txt) | NET/IB : No device found、SPCX／IB 初始化失敗、NET/Socket 被選用、communicator Init COMPLETE | 1 GPU／1 rank／1 node；不代表實際 inter-node traffic、RDMA bandwidth、TCP vs RDMA 比較或 RoCE／PFC／ECN 驗證 |
| PyTorch DDP / Profiling | [DDP 紀錄](../history/20260922-before-current/week16/day2-pytorch-ddp.md.txt)、[profiler 分析](../../Day6-Distributed-Training-Bottleneck-Analysis.md)、[scaling 程式](../../runtime/pytorch/distributed_scaling.py) | CPU／Gloo DDP、parameter checksum、1→2 workers scaling 與 profiler operator 分析 | Profiling 為 single-node CPU／Gloo；結果摘錄在文件，不能當作 multi-GPU／NCCL scaling evidence |
| vLLM Performance | [c16 result](../../benchmark/results/vllm-c16-fixed.json)、[c32 result](../../benchmark/results/vllm-c32-fixed.json)、[c64 result](../../benchmark/results/vllm-c64.json)、[analyzer](../../analysis/performance_analyzer.py)、[分析紀錄](../history/20260922-before-current/week15/Day6-Performance-Analyzer.md.txt) | Qwen2.5-0.5B-Instruct、各 128 completed requests 的 concurrency／throughput／TTFT／TPOT 比較 | 僅支持該組 workload／環境的效能結論；非通用 SLO、非主 E2E 自動回收結果 |
| L4 Transformer Training | [比較報告](../performance/transformer-training-l4-20260921.md)、[batch 8](../../benchmark/results/transformer-train-b8-20260921.json)、[batch 16](../../benchmark/results/transformer-train-b16-20260921.json)、[程式](../../benchmark/gpu/transformer_train_benchmark.py) | BF16、10 warmup、3×20 measured steps；batch 8→16 tokens/s +74.4%，同時記錄 latency、memory、CV | synthetic 小模型、單 L4 time-sharing share；無真實 dataset／tokenizer、DCGM、multi-GPU 或 pretrained LLM quality |
| GPU / DCGM Monitoring | [dashboard 驗證](../history/20260922-before-current/week14/Day6-gpu-dashboard-establish-and-gpuworkload-verification.md.txt)、[DCGM integration](../history/20260922-before-current/week14/Day5-GPU-Metrics-Monitoring-integration.md.txt)、[exporter manifest](../../benchmark/k8s/dcgm-exporter-remote.yaml) | CUDA workload 前後 utilization、temperature、VRAM 等指標由 DCGM／Prometheus／Grafana 觀察 | 早期 dashboard 數據是 P100，不可標為 hpc-gpu-sg L4 本次結果；manifest 存在不代表目前 scrape target 健康 |
| Linux Performance | [CPU analysis](../history/20260922-before-current/week12/Day1-Linux-CPU-Performance-Analysis.md.txt)、[perf](../history/20260922-before-current/week12/Day6-Linux-CPU-Profiling-with-perf.md.txt)、[strace](../history/20260922-before-current/week12/Day7-Linux-System-Call-Analysis-with-strace.md.txt)、[CPU report](../../benchmark/cpu/results/cpu_benchmark_20260810.md) | Linux CPU／process／system-call 診斷紀錄與 stress-ng CPU saturation baseline | 歷史環境的輸出／報告；不是主 MPI job 的自動 profiling 或跨機型可直接比較的結果 |
| RBAC / Security | [API JobSet RBAC](../../k8s/security/api-jobset-rbac.yaml)、[RBAC 驗證](../history/20260922-before-current/week20/day1-rbac-serviceaccount-least-privilege.md.txt)、[Pod hardening](../history/20260922-before-current/week20/day2-pod-image-secret-security.md.txt)、[NetworkPolicy 實測](network-policy-validation-20260921.json) | API namespace-scoped JobSet 權限設定；歷史 benchmark-runner 允許／拒絕；隔離 Calico GKE ingress baseline／allow／deny／recovery | benchmark-runner 與 api-jobset-runner 是不同身份；NetworkPolicy 實測不在主 cluster，未涵蓋 egress、跨 namespace 或全平台 hardening |
| Terraform / GitOps | [Terraform 證據](terraform-gpu-sg-20260921.md)、[CPU-only bootstrap 驗收](cpu-bootstrap-acceptance-20260921.json)、[gpu-sg root](../../terraform/environments/gpu-sg/main.tf)、[歷史 GitOps 紀錄](../history/20260922-before-current/week10/Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md.txt) | 主環境 import 零 drift；全新 CPU-only cluster 完成 controllers／Secrets／queues／平台 bootstrap、health／RBAC／PVC 驗收及銷毀 | 不涵蓋全新 GPU cluster MPI 執行；缺 remote state；Argo dev 仍指舊 overlays/dev |
| L4 Causal LM / CUDA Profiling | [9/22 報告](../performance/causal-lm-l4-20260922.md)、[原始證據與 hashes](../../benchmark/results/causal-lm-20260922/evidence.json) | 13M causal LM、文字 byte tokens、交錯三次量測、兩份 CUDA traces、同步 nvidia-smi 遙測 | 單 L4 time-sharing；非 pretrained LLM 品質或多 GPU 結論；獨立 runner 尚未接 MPI API |

## Capability Matrix

狀態是證據標記，可同時存在，不是成熟度分數：

- **Implemented**：repo 有對應程式、script 或 declarative manifest；以「範圍」欄為準。
- **Validated**：repo 保存範圍內的執行或觀察結果；本索引使用既有 evidence，未重新執行實驗。
- **Documented**：有可追溯的說明與結果入口。
- **Partial**：該列涵蓋的能力仍有未整合或未驗證部分，明列於最後一欄。

| 分類 | 範圍 | 狀態 | Partial 邊界／未完成項目 |
|---|---|---|---|
| Platform | API submission、背景 polling worker、MPI dispatch／rank execution／terminal collection | Implemented · Validated · Documented · Partial | 9/22 自動結果回收與重啟接續已驗證；仍缺 artifact storage、跨 DB／Redis 原子交易與 full lifecycle state machine |
| Distributed Compute | MPI JobSet、Ray tasks／recovery、Slurm multi-node MPI | Implemented · Validated · Documented · Partial | 各自獨立；Ray／Slurm 未接 API；Ray retry evidence 到 RUNNING，Slurm 歷史 compute VM 已移除 |
| GPU / AI Performance | 13M causal LM training／CUDA profiling、歷史 DDP／vLLM／NCCL | Implemented · Validated · Documented · Partial | 單 L4 time-sharing、byte corpus；無 pretrained LLM 品質、multi-node GPU scaling／RDMA 結論 |
| Scheduling | Kueue queue／quota／priority／preemption／TAS | Implemented · Validated · Documented · Partial | 單實體 GPU node 的 quota／placement 實驗；無 multi-node／cross-zone TAS 驗證 |
| Observability | API metrics、Prometheus／Grafana／DCGM 設定與歷史監控 | Implemented · Validated · Documented · Partial | 缺主 E2E per-job metrics／result 關聯；舊 P100 dashboard evidence 與目前 L4 分開 |
| Infrastructure | Terraform、bootstrap、Helm、Kustomize、Argo CD | Implemented · Validated · Documented · Partial | 全新 CPU-only cluster 已完成 Terraform、controllers、queues、Secrets、platform apply／acceptance／destroy；Spot GPU rehearsal 被全域 quota 阻擋並清理，尚缺全新 GPU MPI 執行、remote state 與 Argo CD 對齊 |
| Security | Namespace RBAC、Pod hardening、NetworkPolicy manifests | Implemented · Validated · Documented · Partial | 隔離 Calico GKE 已驗證 ingress packet allow／deny／recovery；主 cluster enforcement、egress／跨 namespace 與全平台 hardening未完成 |
| Troubleshooting | Kueue、JobSet、Ray、Slurm、NCCL failure-domain 定位 | Implemented · Validated · Documented · Partial | 有 failure scripts／hooks 與紀錄；單 GPU node 無 node failover，Slurm 未驗證恢復，非完整 HA 認證 |

## Historical Evidence Boundary

TAS、priority／preemption、JobSet recovery、Ray mismatch／retry、Slurm multi-node／failure、DDP profiling、GPU dashboard、Linux tools 與 Terraform／GitOps 的執行結果主要保存在歷史文件內。部分能力另有 scripts／manifests，但不能用設定檔取代執行證據。

NCCL 有獨立 raw log，vLLM 有 JSON artifacts；主 MPI E2E 的成功輸出保存在 demo 文件。這些同樣是已保存的執行紀錄，不表示環境目前仍在運行。重新演示時應依各文件的前置條件與環境限制準備，不在本索引建立新實驗或補造結果。
