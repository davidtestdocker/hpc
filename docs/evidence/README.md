# Platform Evidence Index

此索引將 HPC AI Performance Engineering Platform 的能力對應到 repo 內實作、原始結果與實驗紀錄。架構分工見 [Final Architecture](../architecture/platform-architecture.md)，主展示入口為 [MPI E2E demo](../demo/end-to-end-mpi-jobset-demo.md)。Supporting experiments 與主線平行，沒有 MPI → Ray → Slurm 的自動 pipeline。

## Evidence 使用方式

- **實作／設定**：程式與 manifest 證明 repo 保存了什麼；不單獨代表 runtime 驗證成功。
- **結果 artifact**：保存的 JSON／log，可直接檢查該次輸出；仍需遵守當時環境與 workload 限制。
- **歷史紀錄**：Week 文件或 demo 內保存的指令、事件與結果；不是本輪重跑結果，也不是即時 cluster 狀態。只有文件摘錄時，不宣稱另有完整 raw capture。

## Capability Evidence

| Capability | Evidence | What was verified | Limitation |
|---|---|---|---|
| Main MPI E2E | [成功紀錄](../demo/end-to-end-mpi-jobset-demo.md)、[API](../../api/main.py)、[dispatcher](../../api/workloads/dispatcher.py)、[template](../../api/workloads/templates/jobset-mpi.yaml) | API／DB 初始 metadata／Redis queue → 動態 JobSet；Kueue admission、1 launcher + 3 workers、rank 0／1／2 輸出 | 成功輸出保存在 demo；CPU MPI workload，不代表 GPU benchmark 或多實體 node；API 停在 submitted |
| Kueue TAS | [TAS 實驗紀錄](../week19/day6-topology-aware-gpu-scheduling.md)、[Topology](../../k8s/gpu-scheduling/topology.yaml)、[ResourceFlavor](../../k8s/gpu-scheduling/resourceflavor.yaml) | hostname topology request、topologyAssignment 與兩個 Pod 的 same-hostname placement | 歷史環境單 GPU node；Pod 最後仍為 ContainerCreating，只驗證 placement；未驗證 multi-node／cross-zone 選擇 |
| Kueue Priority / Preemption | [preemption 紀錄](../week19/day4-priority-preemption-multi-tenancy.md)、[ClusterQueue](../../k8s/gpu-scheduling/clusterqueue.yaml)、[PriorityClass](../../k8s/gpu-scheduling/priorityclasses.yaml) | Low workload 被 evict、quota 釋放、high workload admitted 並 Running | 執行證據在 Week 文件；同一 ClusterQueue、單 L4 time-sharing shares，不是四張實體 GPU，也不是完整 tenant isolation |
| JobSet Recovery | [JobSet recovery demo](../demo/jobset-recovery-demo.md)、[failure／recovery 紀錄](../week20/day4-ha-node-failure-recovery.md)、[固定名稱 example](../../k8s/gpu-scheduling/examples/jobset-mpi.yaml)、[目前動態 template](../../api/workloads/templates/jobset-mpi.yaml) | Worker exit 42 → RestartJobSet／Recreate → restarts=1、JobsReady；另記錄 cordon／uncordon admission blockage | Recovery evidence 來自歷史 mpi-real；未另證明動態 JobSet 本次也做過 fault injection；cordon 不是硬體故障，單 GPU node 無 node failover |
| Ray Resource Mismatch | [Ray supporting demo](../demo/ray-worker-recovery-demo.md)、[RayJob](../../ray-resource-mismatch-job.yaml)、[排障紀錄](../week20/day5-ai-hpc-production-troubleshooting.md)、[RayCluster](../../ray-cluster.yaml) | Pods Running、Ray GPU=0，但 num_gpus=1 task pending；定位 Ray scheduler resource mismatch | CPU Ray cluster 的歷史紀錄；不是 GPU Ray workload 成功執行證據，未接入主 API |
| Ray NODE_DIED Retry | [Ray recovery demo](../demo/ray-worker-recovery-demo.md)、[recovery RayJob](../../ray-worker-recovery-job.yaml)、[runbook](../runbooks/ai-hpc-job-troubleshooting.md)、[實驗紀錄](../week20/day5-ai-hpc-production-troubleshooting.md) | attempt 0 NODE_DIED 後，以 max_retries=2／soft affinity 在其他 Ray node 開始 attempt 1；KubeRay 另補 worker Pod | 保存的證據到 retry RUNNING；不額外宣稱最終 SUCCEEDED、Actor state recovery 或 exactly-once |
| Slurm Multi-node MPI | [Slurm supporting demo](../demo/slurm-failure-troubleshooting-demo.md)、[multi-node 紀錄](../week17/day4-slurm-multinode-hpc-cluster.md)、[MPI sbatch](../../mpi-multinode.slurm)、[MPI source](../../mpi_hello.c) | compute-01／02 的 Slurm allocation、4 tasks 與 mpirun rank 輸出；PMI 相容性排障 | 歷史 CPU VM 環境；無 shared filesystem；multi-node OSU benchmark 未完成，非 GPU Slurm evidence |
| Slurm Node Failure Troubleshooting | [Slurm troubleshooting demo](../demo/slurm-failure-troubleshooting-demo.md)、[排障紀錄](../week20/day5-ai-hpc-production-troubleshooting.md)、[runbook](../runbooks/ai-hpc-job-troubleshooting.md)、[pending script](../../slurm/pending-cpu-test.sbatch) | Node DOWN+NOT_RESPONDING、job PENDING；追到 compute VM 已不存在而 slurm.conf 仍保留 | 未宣稱恢復成功；accounting storage disabled，無 sacct／SlurmDBD 歷史查詢能力 |
| NCCL Transport Fallback | [NCCL fallback demo](../demo/nccl-transport-fallback-demo.md)、[原始 NCCL log](../../benchmark/results/week16-day4-nccl-single-gpu.txt)、[transport 排障紀錄](../week18/day5-nccl-transport-debugging.md) | NET/IB : No device found、SPCX／IB 初始化失敗、NET/Socket 被選用、communicator Init COMPLETE | 1 GPU／1 rank／1 node；不代表實際 inter-node traffic、RDMA bandwidth、TCP vs RDMA 比較或 RoCE／PFC／ECN 驗證 |
| PyTorch DDP / Profiling | [DDP 紀錄](../week16/day2-pytorch-ddp.md)、[profiler 分析](../../Day6-Distributed-Training-Bottleneck-Analysis.md)、[scaling 程式](../../runtime/pytorch/distributed_scaling.py) | CPU／Gloo DDP、parameter checksum、1→2 workers scaling 與 profiler operator 分析 | Profiling 為 single-node CPU／Gloo；結果摘錄在文件，不能當作 multi-GPU／NCCL scaling evidence |
| vLLM Performance | [c16 result](../../benchmark/results/vllm-c16-fixed.json)、[c32 result](../../benchmark/results/vllm-c32-fixed.json)、[c64 result](../../benchmark/results/vllm-c64.json)、[analyzer](../../analysis/performance_analyzer.py)、[分析紀錄](../week15/Day6-Performance-Analyzer.md) | Qwen2.5-0.5B-Instruct、各 128 completed requests 的 concurrency／throughput／TTFT／TPOT 比較 | 僅支持該組 workload／環境的效能結論；非通用 SLO、非主 E2E 自動回收結果 |
| GPU / DCGM Monitoring | [dashboard 驗證](../week14/Day6-gpu-dashboard-establish-and-gpuworkload-verification.md)、[DCGM integration](../week14/Day5-GPU-Metrics-Monitoring-integration.md)、[exporter manifest](../../benchmark/k8s/dcgm-exporter-remote.yaml) | CUDA workload 前後 utilization、temperature、VRAM 等指標由 DCGM／Prometheus／Grafana 觀察 | 早期 dashboard 數據是 P100，不可標為 hpc-gpu-sg L4 本次結果；manifest 存在不代表目前 scrape target 健康 |
| Linux Performance | [CPU analysis](../week12/Day1-Linux-CPU-Performance-Analysis.md)、[perf](../week12/Day6-Linux-CPU-Profiling-with-perf.md)、[strace](../week12/Day7-Linux-System-Call-Analysis-with-strace.md)、[CPU report](../../benchmark/cpu/results/cpu_benchmark_20260810.md) | Linux CPU／process／system-call 診斷紀錄與 stress-ng CPU saturation baseline | 歷史環境的輸出／報告；不是主 MPI job 的自動 profiling 或跨機型可直接比較的結果 |
| RBAC / Security | [API JobSet RBAC](../../k8s/security/api-jobset-rbac.yaml)、[RBAC 驗證](../week20/day1-rbac-serviceaccount-least-privilege.md)、[Pod hardening](../week20/day2-pod-image-secret-security.md)、[NetworkPolicy 限制](../week20/day3-networkpolicy-tenant-isolation.md) | API namespace-scoped JobSet 權限設定；歷史 benchmark-runner 的允許／拒絕測試；Pod hardening 與 NetworkPolicy schema validation | benchmark-runner 與 api-jobset-runner 是不同身份；不能共用權限測試結論。NetworkPolicy 當時未 enforcement，未驗證 packet deny；非全平台一致 hardening |
| Terraform / GitOps | [Terraform GKE 紀錄](../week9/Day8-GKE-Cluster-withTerraform.md)、[GitOps 紀錄](../week10/Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md)、[Terraform dev](../../terraform/environments/dev/main.tf)、[Argo dev](../../argocd/application-dev.yaml)、[platform overlay](../../kustomize/overlays/gpu-sg-platform/kustomization.yaml) | 歷史 GKE 建置、image build／tag 更新／Argo sync／rolling update；目前 repo 保存 Helm／Kustomize 平台設定 | Terraform dev 是 hpc-dev；Argo dev 指舊 overlays/dev；不代表新 hpc-gpu-sg E2E 已完成 IaC／GitOps 對齊 |

## Capability Matrix

狀態是證據標記，可同時存在，不是成熟度分數：

- **Implemented**：repo 有對應程式、script 或 declarative manifest；以「範圍」欄為準。
- **Validated**：repo 保存範圍內的執行或觀察結果；本索引使用既有 evidence，未重新執行實驗。
- **Documented**：有可追溯的說明與結果入口。
- **Partial**：該列涵蓋的能力仍有未整合或未驗證部分，明列於最後一欄。

| 分類 | 範圍 | 狀態 | Partial 邊界／未完成項目 |
|---|---|---|---|
| Platform | API submission、Redis queue、MPI dispatch／rank execution | Implemented · Validated · Documented · Partial | 缺 worker daemon、completion watcher、final status sync、result collector、full lifecycle state machine |
| Distributed Compute | MPI JobSet、Ray tasks／recovery、Slurm multi-node MPI | Implemented · Validated · Documented · Partial | 各自獨立；Ray／Slurm 未接 API；Ray retry evidence 到 RUNNING，Slurm 歷史 compute VM 已移除 |
| GPU / AI Performance | PyTorch runtime／DDP profiling、vLLM result analysis、NCCL transport | Implemented · Validated · Documented · Partial | DDP profiling 是 CPU／Gloo；NCCL 單 GPU；無 multi-node GPU scaling／RDMA performance evidence |
| Scheduling | Kueue queue／quota／priority／preemption／TAS | Implemented · Validated · Documented · Partial | 單實體 GPU node 的 quota／placement 實驗；無 multi-node／cross-zone TAS 驗證 |
| Observability | API metrics、Prometheus／Grafana／DCGM 設定與歷史監控 | Implemented · Validated · Documented · Partial | 缺主 E2E per-job metrics／result 關聯；舊 P100 dashboard evidence 與目前 L4 分開 |
| Infrastructure | Terraform、Helm、Kustomize、Argo CD | Implemented · Validated · Documented · Partial | 歷史部署有驗證，新 gpu-sg-platform 未完成 Terraform／Argo CD 對齊與完整 cluster bootstrap |
| Security | Namespace RBAC、Pod hardening、NetworkPolicy manifests | Implemented · Validated · Documented · Partial | Validated 限歷史 RBAC／hardening／schema 範圍；無 NetworkPolicy packet-deny 驗證或全平台 hardening |
| Troubleshooting | Kueue、JobSet、Ray、Slurm、NCCL failure-domain 定位 | Implemented · Validated · Documented · Partial | 有 failure scripts／hooks 與紀錄；單 GPU node 無 node failover，Slurm 未驗證恢復，非完整 HA 認證 |

## Historical Evidence Boundary

TAS、priority／preemption、JobSet recovery、Ray mismatch／retry、Slurm multi-node／failure、DDP profiling、GPU dashboard、Linux tools 與 Terraform／GitOps 的執行結果主要保存在歷史文件內。部分能力另有 scripts／manifests，但不能用設定檔取代執行證據。

NCCL 有獨立 raw log，vLLM 有 JSON artifacts；主 MPI E2E 的成功輸出保存在 demo 文件。這些同樣是已保存的執行紀錄，不表示環境目前仍在運行。重新演示時應依各文件的前置條件與環境限制準備，不在本索引建立新實驗或補造結果。
