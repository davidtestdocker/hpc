# HPC AI Performance Engineering Platform — Resume Project Description

## 中文履歷版

### 一句話版本

建立 API 驅動的 HPC／AI workload submission 平台，串接 FastAPI、Redis、PostgreSQL、Kubernetes JobSet 與 Kueue，完成 MPI rank execution，並以獨立效能分析與故障案例展示跨層工程能力。

### 3 Bullet 版本

- 整合 FastAPI／Redis／PostgreSQL 與 Kubernetes Python Client，動態建立 JobSet，經 Kueue admission 啟動 1 launcher、3 workers 與 3 MPI ranks，驗證從 API 提交到 distributed execution 的流程。
- 驗證 Kueue quota／priority／preemption／單 GPU node TAS 與 JobSet recovery，並整理獨立 Ray NODE_DIED retry、Slurm CPU multi-node MPI／node failure、NCCL Socket fallback 案例，建立可追溯的跨層排障 evidence。
- 分析 Qwen2.5-0.5B-Instruct 的固定 128-request vLLM 結果，量化 concurrency 32→64 時 throughput +29.6% 與 mean TTFT +137.8% 的取捨，結合 CPU／Gloo profiling 與 Prometheus／Grafana／DCGM 歷史觀察，界定效能結論與環境限制。

### English Resume Version

**1-line project description**

Built an API-driven HPC/AI workload submission platform with Kubernetes JobSet and Kueue, supported by performance analysis and distributed-systems failure investigations.

**3 resume bullets**

- Integrated FastAPI, Redis, PostgreSQL, and the Kubernetes Python client to dispatch dynamic JobSets through Kueue admission, validating an API-to-MPI execution path with one launcher, three worker Pods, and three ranks.
- Validated Kueue quota, priority preemption, single-GPU-node topology placement, and JobSet recovery; documented separate Ray task retries, Slurm CPU multi-node MPI and node-failure investigations, and NCCL Socket fallback cases.
- Analyzed fixed 128-request vLLM runs for Qwen2.5-0.5B-Instruct, quantifying a 29.6% throughput gain against a 137.8% increase in mean TTFT from concurrency 32 to 64; used CPU/Gloo profiling and historical GPU telemetry to qualify performance conclusions.

## Evidence 與使用邊界

面試可依序開啟 [主 E2E](../demo/end-to-end-mpi-jobset-demo.md)、[Evidence Index](../evidence/README.md)、[Performance Report](../performance/performance-report.md)。[架構文件](../architecture/platform-architecture.md) 說明 platform 與 supporting paths 的分工。

上述成果不代表 production-ready、multi-node GPU／RDMA benchmark、Ray／Slurm API integration、automatic result collection 或 complete HA。主線 worker 目前是 HTTP handler，API 狀態停於 submitted；TAS 為單 GPU node，GPU dashboard 歷史數據來自 P100，不能寫成目前 L4 驗證。Terraform／Helm／Kustomize／Argo CD 有獨立部署成果，但新主線 IaC／GitOps 尚未完全對齊。
