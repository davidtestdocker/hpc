# Week15 Day5 - Benchmark Engine

## 今日目標

建立正式的 AI Inference Benchmark 流程。

今天不自己重造壓測工具，而是使用：

```text
vLLM 官方 Benchmark Tool
```

進行 serving benchmark，並將結果保存成 JSON artifact，作為後續 Performance Analyzer 的輸入資料。

今日完成：

- vLLM 官方 `bench serve`
- Concurrency Benchmark
- Throughput Benchmark
- TTFT Benchmark
- TPOT Benchmark
- ITL Benchmark
- GPU Utilization Verification
- GPU Memory Verification
- Benchmark JSON Artifact
- Serving Saturation Analysis

---

# 今日新增平台能力

新增：

```text
Inference Benchmark Capability
```

流程：

```text
vLLM Server
    ↓
vllm bench serve
    ↓
Different Concurrency
    ↓
Throughput / Latency
    ↓
GPU Util / GPU Memory
    ↓
Official JSON Result
```

---

# 1. 為什麼使用官方 Benchmark Tool

原本曾嘗試自行使用 Python 建立：

```text
ThreadPoolExecutor
HTTP Load Generator
GPU Sampler
Custom Parser
```

但正式 Day5 改成使用：

```text
vllm bench serve
```

原因：

```text
Benchmark Tool
應由專業工具負責：

- Request Generation
- Concurrency Control
- Latency Measurement
- Throughput Measurement
- Percentile Statistics
```

平台本身不重新實作這些功能。

因此：

```text
Benchmark Tool
→ 負責測試

Platform
→ 負責保存、比較、分析結果
```

---

# 2. vLLM Benchmark Tool

確認 vLLM 提供：

```text
vllm bench latency
vllm bench serve
vllm bench startup
vllm bench sweep
vllm bench throughput
```

Day5 使用：

```text
vllm bench serve
```

用途：

```text
Benchmark Online LLM Serving Performance
```

也就是測試已經啟動中的：

```text
vLLM Server
↓
Qwen
↓
NVIDIA L4
```

---

# 3. Benchmark 基本參數

基本指令：

```bash
vllm bench serve \
  --backend openai \
  --base-url http://127.0.0.1:8000 \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --dataset-name random \
  --num-prompts 20 \
  --max-concurrency 1
```

---

# 4. backend

```bash
--backend openai
```

代表使用：

```text
OpenAI-compatible API
```

送 inference request。

vLLM 本身提供：

```text
/v1/completions
/v1/chat/completions
```

等 OpenAI-compatible API。

---

# 5. base-url

```bash
--base-url http://127.0.0.1:8000
```

代表 benchmark client 直接連：

```text
同一個 Pod 內
vLLM Server
Port 8000
```

這樣可以避免：

```text
NodePort
VPC Peering
Cross-region Network
```

等額外 network latency 干擾純 inference benchmark。

---

# 6. model

```bash
--model Qwen/Qwen2.5-0.5B-Instruct
```

指定目前 vLLM Server 載入的模型。

---

# 7. random dataset

```bash
--dataset-name random
```

代表 benchmark tool 自動產生 random prompt。

目的：

```text
不先引入真實 Dataset 差異
專注測 Runtime / Serving Performance
```

---

# 8. num-prompts

```bash
--num-prompts 20
```

代表總共產生：

```text
20 個 inference requests
```

---

# 9. max-concurrency

例如：

```bash
--max-concurrency 4
```

代表：

```text
同時間最多允許 4 個 requests 執行
```

Day5 使用不同 concurrency：

```text
1
4
8
16
32
64
```

目的：

```text
逐步增加 Serving Load
↓
觀察 Throughput 是否增加
↓
觀察 Latency 是否惡化
↓
找出 High-load / Saturation Trend
```

---

# 10. Benchmark Metrics

vLLM 官方 benchmark 直接提供：

```text
Request Throughput
Output Token Throughput
Total Token Throughput

TTFT
TPOT
ITL

Median
Mean
P99
```

---

# 11. Request Throughput

```text
Request throughput (req/s)
```

代表：

```text
每秒完成多少 inference requests
```

數值越高：

```text
Serving Capacity 越高
```

---

# 12. Output Token Throughput

```text
Output token throughput (tok/s)
```

代表：

```text
整個 Server 每秒產生多少 Output Tokens
```

對 LLM serving 而言是非常重要的 throughput metric。

---

# 13. TTFT

TTFT：

```text
Time To First Token
```

代表：

```text
Request 送出
↓
模型開始處理
↓
第一個 Token 出現
```

中間花多久。

TTFT 很直接影響：

```text
User Perceived Responsiveness
```

---

# 14. TPOT

TPOT：

```text
Time Per Output Token
```

代表第一個 token 產生之後：

```text
後續每個 output token
平均需要多久
```

主要反映：

```text
Decode Performance
```

---

# 15. ITL

ITL：

```text
Inter-Token Latency
```

代表：

```text
Token
↓
等待多久
↓
下一個 Token
```

對 streaming LLM response 很重要。

---

# 16. Baseline Benchmark

Concurrency：

```text
1
```

結果：

```text
Request Throughput:
1.48 req/s

Output Token Throughput:
189.28 tok/s

Mean TTFT:
31.33 ms

P99 TTFT:
39.66 ms

Mean TPOT:
5.07 ms

Mean ITL:
5.11 ms
```

這組作為：

```text
Single-request Baseline
```

---

# 17. Concurrency Benchmark

正式結果：

```text
Conc      Req/s      Tok/s   MeanTTFT    P99TTFT     TPOT      ITL

1          1.48      189.28      31.33       39.66     5.07     5.11

4          5.58      713.70      53.81       60.38     5.21     5.24

8          8.61     1102.16      85.50      100.80     5.45     5.50

16        12.09     1546.96     127.85      166.37     5.94     6.02

32        25.68     3286.47     210.07      338.44     7.97     7.97

64        32.38     4144.53     448.58      818.07    11.27    11.90
```

---

# 18. Scaling Behavior

## Concurrency 1 → 4

```text
Request Throughput
1.48
→
5.58 req/s
```

Throughput 大幅增加。

TTFT：

```text
31.33
→
53.81 ms
```

仍屬合理增加。

---

## Concurrency 4 → 8

```text
Request Throughput
5.58
→
8.61 req/s
```

仍然有明顯 throughput gain。

TPOT：

```text
5.21
→
5.45 ms
```

變化仍小。

---

## Concurrency 8 → 16

```text
Request Throughput
8.61
→
12.09 req/s
```

仍有 throughput 提升。

但：

```text
Mean TTFT
85.50
→
127.85 ms
```

Latency trade-off 開始變明顯。

---

# 19. High-load Region

Concurrency：

```text
32
```

結果：

```text
Request Throughput:
25.68 req/s

Output Throughput:
3286.47 tok/s

Mean TTFT:
210.07 ms

P99 TTFT:
338.44 ms

Mean TPOT:
7.97 ms
```

此時：

```text
Throughput 很高
但 TTFT / TPOT 已開始明顯增加
```

代表開始進入：

```text
High-load Region
```

---

# 20. Saturation Trend

Concurrency：

```text
64
```

結果：

```text
Request Throughput:
32.38 req/s

Output Throughput:
4144.53 tok/s

Mean TTFT:
448.58 ms

P99 TTFT:
818.07 ms

Mean TPOT:
11.27 ms
```

比較：

```text
Concurrency
32
→
64
```

Request Throughput：

```text
25.68
→
32.38 req/s
```

約增加：

```text
26%
```

但 Mean TTFT：

```text
210.07
→
448.58 ms
```

增加超過：

```text
100%
```

TPOT：

```text
7.97
→
11.27 ms
```

也明顯惡化。

因此：

```text
32 之後開始進入明顯 High-load Region

64 已出現：
Latency Cost
增加速度
>
Throughput Benefit
```

---

# 21. Saturation Point

Saturation Point：

```text
飽和點
```

代表：

```text
繼續增加 Workload
↓
Throughput 提升開始變小
↓
Latency 卻快速惡化
```

本次結果不能單純說：

```text
32 就是唯一最佳 Concurrency
```

因為最佳點會受到：

```text
SLA
TTFT Requirement
Throughput Requirement
Cost Requirement
```

影響。

例如：

```text
要求低 TTFT
→ 可能選 8 / 16

追求較高 Throughput
→ 可能選 32

只追求最大 Throughput
→ 64 還能增加 capacity
```

---

# 22. Throughput / Latency Trade-off

本次測試完整觀察到：

```text
Concurrency ↑
↓
Throughput ↑
↓
GPU Load ↑
↓
Queue / Resource Contention ↑
↓
TTFT ↑
TPOT ↑
ITL ↑
```

因此：

```text
Higher Throughput
```

通常不是免費的。

必須交換：

```text
Higher Latency
```

這就是：

```text
Throughput / Latency Trade-off
```

---

# 23. GPU Utilization

Day5 使用 NVIDIA：

```text
nvidia-smi dmon
```

進行 GPU runtime monitoring。

指令：

```bash
nvidia-smi dmon -s um
```

其中：

```text
u
=
Utilization

m
=
Memory
```

---

# 24. SM Utilization

SM：

```text
Streaming Multiprocessor
```

是 NVIDIA GPU 主要的運算單元。

SM 裡包含：

```text
CUDA Cores
Tensor Cores
Schedulers
Registers
Shared Memory
```

`SM Utilization` 代表：

```text
GPU 主要 Compute Units
有多少比例時間正在忙
```

---

# 25. GPU Utilization Verification

在：

```text
Concurrency = 32
```

Benchmark 執行期間觀察：

```text
SM Utilization

18%
100%
100%
```

代表高負載 inference 執行期間：

```text
L4 GPU Compute Units
曾達到 100% Utilization
```

這不代表：

```text
GPU 所有硬體資源全部 100%
```

而是：

```text
SM Compute Activity
在取樣期間達到滿載
```

---

# 26. GPU Memory

同一時間：

```text
fb = 21568 MB
```

代表：

```text
Framebuffer Memory Used
≈
21.6 GB
```

L4 可用 VRAM 約：

```text
23 GB
```

因此 vLLM Runtime 已使用大量 GPU Memory。

---

# 27. mem 欄位

`nvidia-smi dmon`：

```text
mem = 100%
```

不是：

```text
VRAM Used = 100%
```

而是：

```text
GPU Memory Controller Utilization
```

真正 VRAM 使用量要看：

```text
fb
```

例如：

```text
fb = 21568 MB
```

---

# 28. GPU Saturation Evidence

Concurrency 32 時觀察：

```text
SM Utilization:
100%

Memory Controller:
100%

VRAM:
~21.6 GB
```

因此可以合理判斷：

```text
GPU Compute
+
Memory Activity
```

都已經處於非常高負載。

這也能解釋為什麼：

```text
32
→
64
```

之後：

```text
Throughput 還能增加

但

TTFT
TPOT
ITL
惡化速度變快
```

因為 GPU 已經沒有大量閒置 compute capacity。

---

# 29. Official Benchmark JSON

vLLM Benchmark 支援：

```text
--save-result
```

直接將結果存成：

```text
JSON
```

不需要自己解析 terminal output。

例如：

```bash
vllm bench serve \
  ... \
  --save-result \
  --result-dir /tmp/benchmark-results \
  --result-filename vllm-c1.json
```

---

# 30. Benchmark Artifacts

Day5 最後保存：

```text
benchmark/results/
├── vllm-c1.json
├── vllm-c4.json
├── vllm-c8.json
├── vllm-c16.json
├── vllm-c32.json
└── vllm-c64.json
```

這些是：

```text
Official vLLM Benchmark Results
```

不是自行重新計算的結果。

---

# 31. JSON Example

官方 JSON 包含：

```text
model_id

num_prompts

max_concurrency

duration

completed

failed

request_throughput

output_throughput

total_token_throughput

mean_ttft_ms

median_ttft_ms

p99_ttft_ms

mean_tpot_ms

p99_tpot_ms

mean_itl_ms

p99_itl_ms
```

---

# 32. 為什麼保留 Benchmark JSON

如果只看 Terminal：

```text
Benchmark 完
↓
數字就只存在 terminal history
```

保存 JSON 後：

```text
Benchmark
↓
Structured Result
↓
Versioned Artifact
↓
Repeatable Analysis
```

後續可以：

```text
比較不同 Concurrency
比較不同 Runtime
比較不同 GPU
比較不同 Model
比較不同版本
```

---

# 33. Day5 Final Architecture

```text
                Benchmark Workload
                        │
                        ▼
                 vllm bench serve
                        │
                        ▼
                  vLLM Server
                        │
                        ▼
              Qwen2.5-0.5B-Instruct
                        │
                        ▼
                    NVIDIA L4
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
   Serving Performance       GPU Telemetry
            │                       │
            │                  nvidia-smi dmon
            │                       │
            └───────────┬───────────┘
                        ▼
                 Benchmark Result
                        │
                        ▼
                   JSON Artifact
                        │
                        ▼
                Day6 Performance
                    Analyzer
```

---

# 34. Day5 完成成果

Week15 Day5 完成：

```text
Official vLLM Benchmark Tool
+
Concurrency Benchmark
+
Serving Throughput
+
Output Token Throughput
+
TTFT
+
TPOT
+
ITL
+
P99 Latency
+
GPU SM Utilization
+
GPU Memory
+
Saturation Trend
+
Benchmark JSON Artifacts
```

平台從：

```text
Runtime 可以執行
```

進化成：

```text
Runtime 可以被正式 Benchmark
```

---

# 35. 與 Day6 的關係

Day5：

```text
產生 Performance Data
```

例如：

```text
Concurrency
Throughput
TTFT
TPOT
ITL
GPU Util
GPU Memory
```

Day6：

```text
讀 Performance Data
↓
分析 Bottleneck
↓
回答為什麼效能變差
```

核心差異：

```text
Day5
What happened?

Day6
Why did it happen?
```

---

# Interview Review

## Q1：為什麼 LLM Serving Benchmark 要測不同 Concurrency？

因為單一 request 的 latency 無法代表 production serving capacity。

需要逐步增加 concurrent requests，觀察：

```text
Throughput
TTFT
TPOT
ITL
GPU Utilization
```

的變化。

當 throughput 墅益開始下降，而 latency 快速增加時，代表系統開始接近 saturation region。

---

## Q2：為什麼不能只看 GPU Utilization？

因為 GPU Utilization 只告訴我們：

```text
GPU 忙不忙
```

但無法直接回答：

```text
使用者 Latency
Serving Throughput
TTFT
Token Generation Performance
```

因此 Performance Engineering 必須同時觀察：

```text
Application Metrics

+

GPU Hardware Metrics
```

才能判斷真正的 serving behavior。

---

# Week15 Day5 Complete

```text
Concurrency Sweep
        ↓
vLLM Official Benchmark
        ↓
Throughput / Latency
        ↓
GPU Util / GPU Memory
        ↓
Saturation Trend
        ↓
Official JSON Artifacts
        ↓
Ready for Day6 Analyzer
```
