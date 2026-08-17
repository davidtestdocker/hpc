# Week15 Day6 - Performance Analyzer

## 今日目標

建立 AI Performance Analyzer。

Day5 已經可以回答：

```text
What happened?
```

例如：

```text
Throughput
TTFT
TPOT
ITL
GPU Utilization
GPU Memory
```

Day6 的目標進一步變成：

```text
Why did it happen?
```

也就是根據：

```text
Benchmark Result
+
Profiler Evidence
+
Hardware Evidence
```

判斷：

```text
Serving Saturation
GPU Bottleneck
CPU Bottleneck
DataLoader Bottleneck
Memory Bottleneck
```

---

# 今日新增平台能力

新增：

```text
Performance Analyzer
```

整體流程：

```text
Official Benchmark / Profiler
            ↓
     Performance Evidence
            ↓
    Performance Analyzer
            ↓
      Bottleneck Diagnosis
            ↓
       Recommendation
```

核心原則：

```text
官方工具負責 Measurement

平台負責：
Comparison
Diagnosis
Recommendation
```

不重新自己實作：

```text
Load Generator
Profiler
GPU Monitor
```

---

# 1. Day6 使用的工具

Inference：

```text
vLLM bench serve
```

Training：

```text
PyTorch Profiler
```

GPU Hardware：

```text
NVIDIA GPU Telemetry
```

Analyzer：

```text
analysis/performance_analyzer.py
```

---

# 2. Bottleneck 是什麼

Bottleneck：

```text
瓶頸
```

代表：

> 整個系統中限制效能繼續提升的部分。

例如：

```text
CPU 每秒只能準備 30 個 samples
GPU 可以處理 100 個 samples

整體 throughput
=
30 samples/s
```

此時：

```text
CPU / DataLoader
=
Bottleneck
```

GPU 再快也沒有用。

---

# 3. 常見 AI Performance Bottleneck

## GPU Bottleneck

```text
GPU compute 已經非常忙
↓
增加 workload
↓
Throughput 增益開始變小
↓
Latency 快速增加
```

---

## CPU Bottleneck

```text
CPU preprocessing
Python execution
Framework overhead
```

速度不夠快。

結果可能是：

```text
GPU 在等 CPU
```

---

## DataLoader Bottleneck

```text
CPU 準備 batch 太慢
↓
GPU 做完目前 batch
↓
下一批資料還沒準備好
↓
GPU idle
```

---

## Memory Bottleneck

可能包含：

```text
CPU RAM
GPU VRAM
Memory Bandwidth
CPU → GPU Transfer
```

限制效能。

---

# 4. Performance Analyzer

建立：

```text
analysis/performance_analyzer.py
```

用途：

```text
讀官方 vLLM benchmark JSON
↓
比較不同 workload
↓
計算 Performance Delta
↓
辨識 scaling / saturation trend
```

它不是 profiler。

它不負責：

```text
測 TTFT
測 TPOT
產生 HTTP workload
監控 GPU
```

這些交給官方工具。

---

# 5. Inference Benchmark Experimental Design

一開始 benchmark 使用：

```text
c1 / c4 / c8 / c16
num_prompts = 20

c32
num_prompts = 64

c64
num_prompts = 128
```

這會造成 experimental variable 不一致。

Performance Engineering 的重要原則：

```text
一次只改一個主要變數
```

如果要研究：

```text
Concurrency
```

就應固定：

```text
Model
Dataset
Prompt Length
Output Length
Backend
GPU
Server Configuration
num_prompts
```

只改：

```text
max_concurrency
```

---

# 6. Fixed High-load Benchmark

重新固定：

```text
num_prompts = 128
```

比較：

```text
Concurrency 16
Concurrency 32
Concurrency 64
```

---

# 7. Concurrency 16

結果：

```text
Request Throughput:
16.75 req/s

Mean TTFT:
135.60 ms

Mean TPOT:
6.40 ms
```

---

# 8. Concurrency 32

結果：

```text
Request Throughput:
24.99 req/s

Mean TTFT:
188.66 ms

Mean TPOT:
8.35 ms
```

---

# 9. Concurrency 64

結果：

```text
Request Throughput:
32.38 req/s

Mean TTFT:
448.58 ms

Mean TPOT:
11.27 ms
```

---

# 10. Analyzer Result

正式比較：

```text
Concurrency 16 -> 32

Throughput: +49.2%
Mean TTFT:  +39.1%
Mean TPOT:  +30.4%
Mean ITL:   +32.8%

Diagnosis:
SCALING
```

代表：

```text
Throughput Gain
>
Latency Cost
```

系統仍有不錯的 scaling。

---

# 11. Saturation Candidate

```text
Concurrency 32 -> 64

Throughput: +29.6%
Mean TTFT: +137.8%
Mean TPOT: +35.0%
Mean ITL:  +39.2%

Diagnosis:
SATURATION_CANDIDATE
```

---

# 12. SATURATION_CANDIDATE

意思：

```text
可能正在進入飽和區
```

不是直接宣稱：

```text
GPU Bottleneck Confirmed
```

因為只有 application metrics 還不夠。

需要結合：

```text
Hardware Evidence
```

才能確認真正 bottleneck。

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
模型處理
↓
第一個 Token 出現
```

所花的時間。

可以理解成：

> 使用者按下送出後，多久開始看到模型回答。

---

# 14. Throughput / TTFT Trade-off

Concurrency：

```text
32 → 64
```

Throughput：

```text
+29.6%
```

但 TTFT：

```text
+137.8%
```

代表：

> 系統每秒確實能處理更多 request，但每個 request 等第一個 token 的時間大幅增加。

也就是：

```text
Throughput ↑

但

Latency ↑↑
```

---

# 15. Inference Diagnosis

結合 Day5 GPU evidence：

```text
SM Utilization 曾達 100%
GPU Memory 約 21.6 GB
```

再加上：

```text
32 → 64

Throughput +29.6%
TTFT      +137.8%
```

可以判斷：

```text
Serving workload
開始進入高負載 / saturation region
```

增加 concurrency 後：

```text
更多 request 同時競爭 GPU
↓
Throughput 還能增加
↓
但 queueing / contention 增加
↓
TTFT 快速惡化
```

---

# 16. Training Performance Analysis

Day6 Training 使用：

```text
PyTorch Profiler
```

直接接進現有：

```text
runtime/pytorch/train.py
```

不建立另一套 training benchmark。

---

# 17. PyTorch Profiler

Profiler 用來回答：

```text
Training 時間到底花在哪？
```

可以觀察：

```text
CPU Operation
CUDA Operation
Tensor Shape
CPU Memory
CUDA Memory
DataLoader
CPU → GPU Copy
Forward
Backward
Optimizer
```

---

# 18. Profiler Activities

設定：

```python
activities=[
    ProfilerActivity.CPU,
    ProfilerActivity.CUDA,
]
```

代表同時監控：

```text
CPU Activity
+
CUDA / GPU Activity
```

---

# 19. record_shapes

```python
record_shapes=True
```

代表記錄 Tensor Shape。

例如：

```text
[512, 1024]
```

Tensor shape 會直接影響 operator performance。

---

# 20. profile_memory

```python
profile_memory=True
```

代表同時記錄：

```text
CPU Memory
CUDA Memory
```

allocation / deallocation 行為。

---

# 21. Profiler Warm-up

第一次 profiling 出現：

```text
Runtime Triggered Module Loading
~227 ms
```

這是：

```text
第一次執行才需要的初始化成本
```

不能直接拿來當 steady-state training bottleneck。

因此使用 PyTorch Profiler Schedule。

---

# 22. Profiler Schedule

設定：

```python
schedule(
    wait=2,
    warmup=2,
    active=5,
    repeat=1,
)
```

代表：

```text
Step 1-2
wait
不記錄

Step 3-4
warmup
熱身

Step 5-9
active
正式記錄
```

總共：

```text
9 training steps
```

其中正式分析：

```text
5 steps
```

---

# 23. Training Step

一個 training step：

```text
取得一個 Batch
↓
CPU → GPU
↓
Forward
↓
Loss
↓
Backward
↓
Optimizer Step
```

通常：

```text
1 step
=
1 batch / 1 training iteration
```

---

# 24. prof.step()

```python
prof.step()
```

代表：

> 告訴 Profiler 一個 training iteration 已完成。

Profiler 依此知道：

```text
Step 1
Step 2
Step 3
...
```

的邊界。

---

# 25. key_averages()

```python
prof.key_averages()
```

把大量 profiler event：

```text
aten::linear
aten::linear
aten::relu
cudaMemcpyAsync
...
```

依 operation 彙總成：

```text
Calls
CPU Time
CUDA Time
CPU Memory
CUDA Memory
```

方便找到主要耗時 operation。

---

# 26. CUDA Time Table

使用：

```python
sort_by="cuda_time_total"
```

找出：

```text
最消耗 GPU / CUDA 時間的 operations
```

例如：

```text
aten::addmm
aten::mm
SGEMM
Memcpy HtoD
```

---

# 27. CPU Time Table

使用：

```python
sort_by="cpu_time_total"
```

找出：

```text
最消耗 CPU 時間的 operations
```

這對：

```text
CPU Bottleneck
DataLoader Bottleneck
```

尤其重要。

---

# 28. DataLoader num_workers

原始設定：

```python
num_workers=0
```

代表：

```text
沒有額外 DataLoader worker process
```

Training main process 自己：

```text
準備資料
+
執行 training
```

---

# 29. num_workers

例如：

```python
num_workers=2
```

代表：

```text
2 個 CPU worker process
```

在背景幫 DataLoader 準備 batch。

概念：

```text
Worker 1 ─┐
          ├→ Ready Batch → Training Process → GPU
Worker 2 ─┘
```

目的是降低：

```text
GPU 等資料
```

的時間。

---

# 30. Baseline - num_workers=0

PyTorch Profiler：

```text
DataLoader CPU total:
44.849 ms

ProfilerStep CPU total:
60.817 ms

Self CPU time total:
64.924 ms

Self CUDA time total:
6.122 ms
```

其中 DataLoader：

```text
44.849 ms
```

佔有非常明顯的 CPU execution time。

---

# 31. DataLoader Evidence

Profiler 顯示：

```text
enumerate(DataLoader)
44.849 ms
```

另外：

```text
aten::select
18.785 ms

aten::stack
7.254 ms

aten::cat
5.565 ms
```

這些 operation 都與 CPU 端：

```text
取資料
組 batch
```

有關。

因此形成 hypothesis：

```text
DataLoader Bottleneck Candidate
```

---

# 32. Controlled Experiment

為了驗證 hypothesis，只修改：

```text
num_workers
```

從：

```text
0
```

改成：

```text
2
```

其他保持不變：

```text
Model
Batch Size
Dataset
GPU
Profiler Schedule
Optimizer
Workload
```

---

# 33. num_workers=2 Result

Profiler 結果：

```text
DataLoader CPU total:
12.244 ms

ProfilerStep CPU total:
34.939 ms

Self CPU time total:
38.913 ms

Self CUDA time total:
6.506 ms
```

---

# 34. Before / After

## DataLoader

```text
44.849 ms
→
12.244 ms
```

改善約：

```text
73%
```

---

## Training Step

```text
60.817 ms
→
34.939 ms
```

改善約：

```text
43%
```

---

## CUDA Time

```text
6.122 ms
→
6.506 ms
```

基本沒有重大變化。

---

# 35. Training Diagnosis

這個結果證明：

```text
GPU 本身沒有突然變快
```

真正改善的是：

```text
DataLoader / CPU-side data preparation
```

因此：

```text
Original Bottleneck:
DataLoader / CPU-side Bottleneck
```

可以被實驗確認。

---

# 36. 為什麼 num_workers=2 有效

原本：

```text
num_workers=0

Main Training Process
↓
自己準備 batch
↓
GPU 等資料
```

改成：

```text
num_workers=2

Worker 1
Worker 2
↓
平行準備 batch
↓
Training Process 更快拿到資料
↓
GPU 等待時間降低
```

---

# 37. Bottleneck Analysis Method

Day6 使用的不是：

```text
看到 GPU 低
→ 猜 CPU 慢
```

而是：

```text
Profiler
↓
發現 DataLoader time 高
↓
提出 Hypothesis
↓
只改 num_workers
↓
重新 Profile
↓
DataLoader time -73%
↓
Training step -43%
↓
確認 Bottleneck
```

這才是：

```text
Evidence-based Performance Engineering
```

---

# 38. Day6 Inference Case

```text
vLLM Benchmark
↓
Concurrency 16 / 32 / 64
↓
Performance Analyzer
↓
32 → 64

Throughput +29.6%
TTFT +137.8%
↓
SATURATION_CANDIDATE
```

---

# 39. Day6 Training Case

```text
PyTorch Training
↓
PyTorch Profiler
↓
DataLoader CPU Time 高
↓
num_workers 0 → 2
↓
DataLoader Time -73%
↓
Training Step Time -43%
↓
DATALOADER BOTTLENECK CONFIRMED
```

---

# 40. Performance Analyzer Architecture

```text
                 AI Workload
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
     vLLM Serving           PyTorch Training
          │                       │
          ▼                       ▼
     vLLM Bench             PyTorch Profiler
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
             Performance Evidence
                      │
                      ▼
        analysis/performance_analyzer.py
                      │
                      ▼
                Diagnosis
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
    Serving Saturation    Training Bottleneck
                                │
                                ▼
                         DataLoader / CPU
                                │
                                ▼
                         Recommendation
```

---

# 41. Day6 最重要觀念

Performance Engineer 不是只看：

```text
GPU Utilization = 50%
```

而是必須回答：

```text
為什麼只有 50%？
```

可能原因：

```text
CPU 不夠快
DataLoader 太慢
Memory Copy 太慢
GPU Compute 飽和
Request Queueing
Batch Size 不適合
Communication Bottleneck
```

所以流程應該是：

```text
Measure
↓
Profile
↓
Hypothesis
↓
Controlled Experiment
↓
Validate
↓
Optimize
```

---

# 42. Day6 完成成果

Week15 Day6 完成：

```text
Performance Analyzer
+
vLLM JSON Analysis
+
Controlled Benchmark Comparison
+
Serving Saturation Detection
+
PyTorch Profiler
+
Profiler Warm-up
+
CPU Profiling
+
CUDA Profiling
+
Memory Profiling
+
DataLoader Analysis
+
Controlled num_workers Experiment
+
DataLoader Bottleneck Confirmation
```

平台從：

```text
Day5
可以量效能
```

進化成：

```text
Day6
可以根據 evidence 找效能瓶頸
```

---

# Interview Review

## Q1：你怎麼判斷 AI workload 的 bottleneck？

不能只看單一 metric。

我會結合：

```text
Application Benchmark
+
Profiler
+
Hardware Telemetry
```

先建立 performance evidence，再提出 bottleneck hypothesis。

接著只修改一個變數做 controlled experiment，確認 performance 是否改善。

例如本次：

```text
DataLoader CPU time 高
↓
num_workers 0 → 2
↓
DataLoader time 約下降 73%
↓
Training step CPU time 約下降 43%
```

因此確認原本存在 DataLoader / CPU-side bottleneck。

---

## Q2：為什麼不能看到 GPU utilization 低就直接說 CPU bottleneck？

因為 GPU utilization 低可能有很多原因：

```text
CPU
DataLoader
Memory Copy
Storage
Network
Small Batch
Synchronization
Communication
Framework Overhead
```

GPU utilization 只能告訴我們：

```text
GPU 忙不忙
```

不能直接告訴：

```text
為什麼不忙
```

所以需要 profiler 與 workload metrics 找真正 root cause。

---

# Week15 Day6 Complete

```text
Benchmark
    ↓
Profiler
    ↓
Performance Evidence
    ↓
Hypothesis
    ↓
Controlled Experiment
    ↓
Bottleneck Diagnosis
    ↓
Recommendation
```

Day6 完成：

```text
Serving Saturation Analysis
+
Training DataLoader Bottleneck Analysis
```
