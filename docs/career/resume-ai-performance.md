# HPC AI 效能工程師版

## 專案標題

HPC AI Performance Engineering Platform — L4 Training、vLLM、MPI／NCCL

## 履歷摘要

建立可提交 distributed workload 並保存結果的 HPC／AI 平台，使用受控 workload、
warmup、重複量測與 profiler 分析 NVIDIA L4 training／LLM serving 的吞吐、延遲
與記憶體取捨。

## 建議 Bullet

- 在 NVIDIA L4 time-sharing share 建立 BF16 synthetic Transformer training
  benchmark，固定 seed／模型／sequence，執行 10 warmup steps 與 3×20 measured
  steps，保存 step latency、tokens/s、peak memory 與 CV raw JSON。
- 以 batch size 作單變因調校：8→16 時 tokens/s 由 101,096 提升至 176,335
 （+74.4%），mean step latency 增加 14.0%，peak memory 增加 50.8%，以
  throughput／latency／memory 同時評估取捨。
- 分析 Qwen2.5-0.5B-Instruct 固定 128-request vLLM 結果；concurrency 32→64
  throughput +29.6%，mean TTFT +137.8%，定位 saturation candidate 並保留
  workload／環境限制。
- 實作 MPI JobSet completion collector，從 Kubernetes terminal condition 與
  launcher log 回收 ranks 0／1／2，將 API／Redis 與 PostgreSQL status 同步為
  completed，建立 workload submission 到 result collection 的可追溯主線。
- 使用 PyTorch profiler、CPU／Gloo DDP、NCCL raw log 與 DCGM／Prometheus
  歷史案例分析 operator、scaling 與 transport；明確區分單 GPU Socket fallback
  與尚未完成的 multi-node GPU／RDMA 效能驗證。

## 面試邊界

本輪 Transformer 是 synthetic 小模型，沒有真實 tokenizer／dataset、DCGM 同步
telemetry、FSDP 或 multi-GPU scaling；GPU time-sharing 也不保證獨占算力。數據只
支持該次 L4 workload，不能泛化為大型 LLM 容量結論。
