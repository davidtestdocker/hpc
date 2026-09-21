# L4 synthetic Transformer training baseline

日期：2026-09-21。這是單一 NVIDIA L4 time-sharing share 上的 BF16 synthetic
Transformer language-model kernel baseline，用來驗證量測方法與 batch-size
取捨；不是 pretrained LLM 收斂品質、端到端資料管線或 multi-GPU scaling。

## 固定條件

- PyTorch `2.12.0+cu126`、CUDA 12.6、BF16 autocast。
- 4 layers、hidden size 512、8 heads、vocab 4096、sequence length 256。
- 固定 seed 20260921；10 warmup steps；每個設定 3 repetitions × 20 measured steps。
- synthetic tokens 已在 GPU，排除 tokenizer、storage、network 與 DataLoader。
- 每步包含 forward、cross entropy、backward 與 AdamW update，前後都有 CUDA synchronize。

## 結果

| Batch | Mean step | Mean tokens/s | CV | Peak allocated memory |
|---:|---:|---:|---:|---:|
| 8 | 20.37 ms | 101,096 | 9.05% | 484.7 MiB |
| 16 | 23.23 ms | 176,335 | 0.47% | 731.1 MiB |

Batch 8 → 16 的 token throughput 增加 **74.4%**，mean step latency 增加
**14.0%**，peak allocated memory 增加 **50.8%**。對 throughput-oriented
workload，batch 16 在這次測試較合適；若單步 latency 或記憶體才是限制，
仍需依 SLO 選擇。Batch 8 第一個 repetition 較慢，使 CV 達 9.05%；不能用
單次結果代表穩態，因此報告保留三次 raw runs。

原始結果：[batch 8](../../benchmark/results/transformer-train-b8-20260921.json)、
[batch 16](../../benchmark/results/transformer-train-b16-20260921.json)。程式與
Jobs 分別在 [benchmark script](../../benchmark/gpu/transformer_train_benchmark.py)、
[baseline manifest](../../benchmark/k8s/transformer-training-baseline.yaml) 與
[batch-16 manifest](../../benchmark/k8s/transformer-training-batch16.yaml)。

## 限制

- GKE GPU time-sharing 不保證獨占算力；沒有同步收集 DCGM utilization／power。
- 模型規模很小，記憶體與 kernel mix 不代表真實 7B／70B LLM。
- 沒有 gradient accumulation、activation checkpointing、FlashAttention、DDP／FSDP。
- batch 變大也改變單步處理 token 數；本報告同時呈現 latency、throughput 與 memory，避免只報最佳數字。
