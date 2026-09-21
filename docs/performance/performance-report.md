# Performance Report

本報告彙整 repo 已保存的 performance evidence。2026-09-21 L4 Transformer benchmark 是本輪重跑；其餘多數結果來自不同歷史環境，不能視為同一次主 MPI E2E 的自動收集結果。能力與來源索引見 [Evidence Index](../evidence/README.md)。

## NVIDIA L4：Synthetic Transformer Training

本輪使用 PyTorch 2.12／CUDA 12.6，以固定小型 Transformer、BF16、10 warmup
steps 與每組 3×20 measured steps，比較 batch size 8／16。Batch 16 的 token
throughput 比 batch 8 高 74.4%，代價是 mean step latency +14.0% 與 peak
allocated memory +50.8%。完整方法、raw runs 與限制見
[L4 training report](transformer-training-l4-20260921.md)。這是 synthetic 小模型、
單一 time-sharing share，不代表大型 pretrained LLM 或 multi-GPU scaling。

## vLLM：Concurrency 與 Latency Tradeoff

採用 [analyzer](../../analysis/performance_analyzer.py) 指定的固定組：[c16-fixed](../../benchmark/results/vllm-c16-fixed.json)、[c32-fixed](../../benchmark/results/vllm-c32-fixed.json)、[c64](../../benchmark/results/vllm-c64.json)。三份 JSON 的 model 均為 `Qwen/Qwen2.5-0.5B-Instruct`，`num_prompts=128`、`completed=128`、`failed=0`、`request_rate=inf`，總 input／output tokens 分別為 131072／16384。沒有混用較早的 20 或 64 requests 結果。

表格 concurrency 使用設定欄位 `max_concurrency`；其餘依序使用 `completed`、`request_throughput`、`mean_ttft_ms`、`mean_tpot_ms`，小數四捨五入至三位。

| Concurrency | Completed requests | Request throughput (req/s) | Mean TTFT (ms) | Mean TPOT (ms/token) |
|---:|---:|---:|---:|---:|
| 16 | 128 | 16.748 | 135.601 | 6.401 |
| 32 | 128 | 24.988 | 188.663 | 8.348 |
| 64 | 128 | 32.379 | 448.579 | 11.271 |

TTFT 是首 token 等待時間，TPOT 是後續每個 output token 的平均時間。以下變化由未四捨五入的 JSON 值計算：

| Concurrency 變化 | Throughput | Mean TTFT | Mean TPOT |
|---|---:|---:|---:|
| 16 → 32 | +49.2% | +39.1% | +30.4% |
| 32 → 64 | +29.6% | +137.8% | +35.0% |

在這三個測點中，latency 從 16 → 32 就已增加；到 64 時 TTFT 增幅明顯高於 throughput 增幅，吞吐量仍提高，但首 token 等待代價大幅上升。若重視 responsiveness，32 是值得進一步驗證的折衷測點，不能在沒有 latency SLO 的情況下宣稱它是最佳設定。

[歷史分析](../week15/Day6-Performance-Analyzer.md) 與 analyzer 以 latency 增幅是否超過 throughput 增幅判定 `SATURATION_CANDIDATE`。這是瓶頸候選訊號，不是單憑三筆數據就證明 GPU 硬體飽和。

限制：每個 concurrency 只有本組保存的單次結果，時間戳不同，並非重複試驗的平均或 confidence interval。JSON 另有 `max_concurrent_requests`（32／64／99），與設定欄位不同；本報告未將它當作 concurrency，也未替其差異推定原因。結論只適用於這個模型、token workload 與歷史 serving 環境，不能泛化成所有模型／GPU 的容量建議。

## CPU / Storage / Network Baselines

| 測項 | 測試方法 | 關鍵指標 | 觀察 | Limitation |
|---|---|---|---|---|
| CPU | [stress-ng report](../../benchmark/cpu/results/cpu_benchmark_20260810.md)：GKE hpc-dev、2-core node，`stress-ng --cpu 2 --timeout 60s --metrics-brief` | Node CPU 由 422m 升至約 2000m | 兩個 CPU workers 能將節點 CPU 推至飽和；適合作為 workload／monitoring baseline | 原文件同時記錄 21%／103%，保留其量測口徑差異，不解讀為額外 CPU capacity；非 application throughput 或目前 L4 node 的結果 |
| Storage | [fio report](../../benchmark/storage/results/fio_20260810.md)：fio 3.33、1G 檔案、4 KiB、`rw=readwrite`、`direct=1`、60 秒 | Read／write：4512／4490 KiB/s、1128／1122 IOPS；平均 latency 437.99／444.73 µs；p99 898／775 µs | 本次小 block mixed read/write baseline 約 0.44 ms 平均 latency；不足以單獨定位底層 storage bottleneck | 目標是 container filesystem／node ephemeral storage，不是 PostgreSQL PVC；沒有證明最大 sequential bandwidth 或 random I/O 表現 |
| Network | [iperf3 report](../../benchmark/network/results/iperf3_20260810.md)：iperf3 3.12，`iperf3 -c iperf3-server -t 30`，同 node 的 client／server Pods 經 Service 使用 TCP | 平均 18.8 Gbit/s、65.7 GBytes、10367 retransmissions | 完成 Pod／Service TCP 傳輸，但 retransmissions 需進一步診斷，不能只憑吞吐量判定網路完全健康 | 同 node 流量，不代表實體 NIC／cross-node throughput；未提供足以定位 retransmission 根因的 counters／packet evidence |

## Distributed / GPU Performance Evidence

| 領域 | 已保存結果 | 解讀與限制 |
|---|---|---|
| PyTorch DDP／profiler | [DDP 紀錄](../week16/day2-pytorch-ddp.md)、[profiler 分析](../../Day6-Distributed-Training-Bottleneck-Analysis.md)：1 worker 5813.76 samples/s；2 workers profiling run 4753.08 samples/s；`aten::addmm` 33.78%、`aten::mm` 33.56% | Single-node CPU／Gloo；operator 摘錄支持 matrix compute 佔主要 CPU 時間。不同 CPU limits 與 profiling 條件，不視為嚴格同條件 scaling；不是 multi-node GPU／NCCL scaling |
| NCCL transport | [Raw log](../../benchmark/results/week16-day4-nccl-single-gpu.txt)、[fallback demo](../demo/nccl-transport-fallback-demo.md)：`NET/IB : No device found` → `Using network Socket` → `Init COMPLETE` | 1 GPU／1 rank／1 node；沒有 RDMA hardware，僅證明 transport discovery／fallback 與初始化。無 inter-node NCCL traffic、ib_write_bw 或 TCP vs RDMA performance comparison |
| DCGM／GPU monitoring | [Dashboard 歷史紀錄](../week14/Day6-gpu-dashboard-establish-and-gpuworkload-verification.md)：utilization 約 0% → 100%、temperature 約 51°C → 60°C、VRAM used 0 → 約 256 MiB | 歷史 P100 環境的 workload／metrics 對照；不是目前 hpc-gpu-sg L4 dashboard 結果，GPU utilization 上升也不等於 application throughput 最佳化 |

DDP 的另一份 [scaling 紀錄](../week16/day5-distributed-training-scaling.md) 保存 2 workers 5549.91 samples/s，與上表 profiling run 是不同紀錄，不能互相替換。此處保留來源與測試條件，不將差值歸因為單一已證實瓶頸。

## 結果使用邊界

本報告支持 vLLM throughput／latency tradeoff、基礎資源量測、CPU DDP profiling 與 GPU observability 的展示。沒有 multi-node GPU scaling、RDMA benchmark、RoCE／PFC／ECN validation，也沒有由主 API 自動收集的 per-job performance report。原始 artifacts 與歷史文件是判讀依據，摘要不取代來源。
