# HPC AI Performance Engineering Platform — Resume Project Description

## 中文履歷版

### 一句話版本

建立 API 驅動的 HPC／AI workload submission 平台，串接 FastAPI、Redis、PostgreSQL、Kubernetes JobSet 與 Kueue，完成 MPI rank execution，並以獨立效能分析與故障案例展示跨層工程能力。

### 3 Bullet 版本

- 整合 FastAPI／Redis／PostgreSQL 與 Kubernetes Python Client，動態建立 JobSet，經 Kueue admission 啟動 1 launcher、3 workers 與 3 MPI ranks；completion collector 回收終態／logs／ranks，實測 API 與 PostgreSQL status 完成同步。
- 驗證 Kueue quota／priority／preemption／單 GPU node TAS 與 JobSet recovery，並整理獨立 Ray NODE_DIED retry、Slurm CPU multi-node MPI／node failure、NCCL Socket fallback 案例，建立可追溯的跨層排障 evidence。
- 在 L4 上以 warmup 與 3 次重複量測分析 synthetic Transformer training，量化 batch 8→16 的 tokens/s +74.4%、step latency +14.0%、memory +50.8%；另分析 Qwen2.5-0.5B-Instruct concurrency 32→64 的 throughput +29.6%／TTFT +137.8% 取捨。

### English Resume Version

**1-line project description**

Built an API-driven HPC/AI workload submission platform with Kubernetes JobSet and Kueue, supported by performance analysis and distributed-systems failure investigations.

**3 resume bullets**

- Integrated FastAPI, Redis, PostgreSQL, and the Kubernetes Python client to dispatch dynamic JobSets through Kueue, then collected terminal status and ranks 0/1/2 back into API/Redis and PostgreSQL state.
- Validated Kueue quota, priority preemption, single-GPU-node topology placement, and JobSet recovery; documented separate Ray task retries, Slurm CPU multi-node MPI and node-failure investigations, and NCCL Socket fallback cases.
- Built a repeated BF16 Transformer training benchmark on NVIDIA L4; increasing batch size from 8 to 16 improved token throughput by 74.4% while step latency rose 14.0% and peak memory 50.8%. Also quantified vLLM throughput/TTFT tradeoffs for Qwen2.5-0.5B-Instruct.

## Evidence 與使用邊界

面試可依序開啟 [主 E2E](../demo/end-to-end-mpi-jobset-demo.md)、[Evidence Index](../evidence/README.md)、[Performance Report](../performance/performance-report.md)。[架構文件](../architecture/platform-architecture.md) 說明 platform 與 supporting paths 的分工。

上述成果不代表 production-ready、multi-node GPU／RDMA benchmark、Ray／Slurm API integration 或 complete HA。主線 worker／collector 仍是手動 HTTP handlers；TAS 為單 GPU node，舊 dashboard 數據來自 P100。Terraform 已完成主環境 import／zero drift 與隔離 apply／destroy；全新 CPU-only cluster bootstrap 已實際通過，但 remote state、全新 GPU cluster MPI 驗收與 GitOps 尚未完成。
