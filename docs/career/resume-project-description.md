# HPC AI Performance Engineering Platform — Resume Project Description

## 中文履歷版

### 一句話版本

建立 API 驅動的 HPC／AI 平台，自動提交 MPI、回收結果並在 worker 重啟後接續；以單 L4 小型 causal LM 的重複量測與 CUDA profiling 展示效能分析能力。

### 3 Bullet 版本

- 整合 FastAPI／Redis／PostgreSQL、Kueue 與 JobSet，以獨立 polling worker 自動提交 MPI 並收集終態／logs／ranks；實測 queued／submitted 兩階段重啟接續、唯一 JobSet、API／DB 狀態同步與模擬失敗 dead-letter。
- 驗證 Kueue quota／priority／preemption／單 GPU node TAS 與 JobSet recovery，並整理獨立 Ray NODE_DIED retry、Slurm CPU multi-node MPI／node failure、NCCL Socket fallback 案例，建立可追溯的跨層排障 evidence。
- 在 L4 上以固定 13M causal LM、文字 byte tokens、暖機與每組三次交錯量測比較 batch 8／16：byte-token throughput +81.29%、step latency +10.25%、peak allocated memory +41.96%；另保存兩份 CUDA traces，分析固定 optimizer 成本與 GEMM 工作量的取捨。

### English Resume Version

**1-line project description**

Built an HPC/AI platform with automatic MPI dispatch, result collection and worker restart recovery, supported by single-L4 causal language-model benchmarks and CUDA profiling.

**3 resume bullets**

- Integrated FastAPI, Redis, PostgreSQL, Kueue and JobSet with a polling worker; validated automatic MPI completion, queued/submitted restart recovery, a single JobSet per tested job, status synchronization and simulated dispatch failure handling.
- Validated Kueue quota, priority preemption, single-GPU-node topology placement, and JobSet recovery; documented separate Ray task retries, Slurm CPU multi-node MPI and node-failure investigations, and NCCL Socket fallback cases.
- Benchmarked a 13M causal language model on one NVIDIA L4 using fixed byte-token data, warmup and three interleaved repetitions per batch. Batch 8 to 16 increased byte-token throughput by 81.29%, with 10.25% higher step latency and 41.96% higher peak allocated memory; separate CUDA traces supported analysis of optimizer and GEMM costs.

## Evidence 與使用邊界

面試依 [9/22 展示順序](../demo/interview-demo-20260922.md) 開啟自動 MPI 驗收與 causal LM profiling，再以 [Evidence Index](../evidence/README.md) 查原始結果。[架構文件](../architecture/platform-architecture.md) 說明平台與獨立效能實驗的分工。

上述成果限於已保存的驗收範圍。主線為背景 polling worker；訓練為單 L4、13M 小型模型與 byte tokens，未驗證 pretrained LLM 品質或 multi-GPU／RDMA。TAS 為單 GPU node，歷史 dashboard 來自 P100。CPU-only fresh bootstrap 已通過；remote state、GitOps、跨資料庫原子交易與完整 HA 尚未完成。訓練 runner、Ray／Slurm 仍未接入 MPI API。
