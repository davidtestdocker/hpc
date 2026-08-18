# Week15 Day7 - AI Runtime Platform v1 Integration

## 今日目標

完成：

```text
AI Runtime Platform v1
```

Day7 不再新增新的 Benchmark Tool、Profiler 或 Monitoring Stack。

今天的重點是把 Week15 前面已經完成的能力正式整合：

```text
AI Runtime
      │
      ▼
Training Runtime
      │
      ▼
Inference Runtime
      │
      ▼
Benchmark Engine
      │
      ▼
Performance Analyzer
```

並驗證整條平台流程：

```text
Git
↓
ArgoCD
↓
Kubernetes
↓
GPU Node
↓
Prometheus
↓
Grafana
```

---

# 今日新增平台能力

正式完成：

```text
AI Runtime Platform v1
```

平台現在可以處理：

```text
Training Workload
+
Inference Workload
+
Benchmark
+
Performance Analysis
+
Observability
```

---

# 1. AI Runtime Platform v1 Architecture

Week15 最終整合架構：

```text
                  Git Repository
                        │
                        ▼
                     ArgoCD
                        │
                        ▼
                   Kubernetes
                        │
                        ▼
                    GPU Node
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
      PyTorch Runtime          vLLM Runtime
             │                     │
             ▼                     ▼
         Training              Inference
             │                     │
             ▼                     ▼
      PyTorch Profiler        vLLM Benchmark
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
              Performance Evidence
                        │
                        ▼
             Performance Analyzer
                        │
                        ▼
                 Prometheus
                        │
                        ▼
                    Grafana
```

---

# 2. GitOps Integration

平台設定與 Runtime 都由 Git Repository 管理。

流程：

```text
Code / Config Change
        ↓
Git Commit
        ↓
Git Push
        ↓
ArgoCD
        ↓
Kubernetes Desired State
```

例如：

```text
runtime/pytorch/train.py
helm/vllm/
helm/prometheus/
kustomize/overlays/gpu-sg/
```

都透過 GitOps 管理。

---

# 3. ArgoCD

SG GPU Runtime 使用：

```text
Application:
hpc-gpu-sg
```

ArgoCD source：

```text
kustomize/overlays/gpu-sg
```

Day7 驗證：

```text
SYNC STATUS:
Synced
```

代表 Git Repository 與 Kubernetes Desired State 一致。

---

# 4. Kubernetes Runtime Layer

SG Kubernetes Namespace：

```text
hpc-platform-dev
```

主要 Runtime：

```text
Deployment
├── pytorch-runtime
└── vllm

Job
└── pytorch-training
```

其中：

```text
PyTorch Runtime
=
Training / Compute Runtime

vLLM Runtime
=
LLM Inference Runtime
```

---

# 5. GPU Node

Inference 與 Training 都執行於：

```text
GKE GPU Node Pool
```

目前 GPU Runtime Node：

```text
gpu-pool
```

GPU：

```text
NVIDIA L4
```

Kubernetes workload 使用：

```yaml
nvidia.com/gpu: 1
```

取得 GPU Resource。

---

# 6. GKE GPU Node Taint

GPU Node 曾出現：

```text
nvidia.com/gpu=present:NoSchedule
```

這個 taint 造成 GKE system connectivity agent 無法排程。

結果：

```text
kubectl exec
kubectl logs
```

可能出現：

```text
No agent available
```

Day7 再次遇到此問題。

確認：

```text
nvidia.com/gpu=present:NoSchedule
```

後移除 taint：

```bash
kubectl taint nodes <GPU_NODE> \
  nvidia.com/gpu=present:NoSchedule-
```

移除後：

```text
kubectl exec
```

恢復正常。

---

# 7. Inference Runtime

Inference Runtime 使用：

```text
vLLM
```

模型：

```text
Qwen/Qwen2.5-0.5B-Instruct
```

架構：

```text
Kubernetes Deployment
        ↓
vLLM Server
        ↓
Qwen Model
        ↓
OpenAI-compatible API
```

---

# 8. Inference Runtime Verification

使用：

```bash
curl http://127.0.0.1:8000/v1/models
```

成功回傳：

```text
Qwen/Qwen2.5-0.5B-Instruct
```

因此驗證：

```text
Kubernetes
↓
vLLM Runtime
↓
Model Loaded
↓
Inference API
```

全部正常。

---

# 9. Inference Runtime 與 Benchmark 的差別

Inference Runtime：

```text
vLLM Server
+
Qwen Model
```

負責：

```text
真正執行 inference
```

Benchmark Tool：

```text
vllm bench serve
```

負責：

```text
產生 workload
控制 concurrency
量測 throughput
量測 latency
```

因此：

```text
Inference Runtime
        ↓
Benchmark Tool
        ↓
Performance Metrics
```

---

# 10. Day7 Inference Benchmark Verification

Day7 使用：

```text
num_prompts = 16
max_concurrency = 4
```

結果：

```text
Successful requests:
16

Failed requests:
0

Request throughput:
5.33 req/s

Output token throughput:
681.65 tok/s

Mean TTFT:
68.68 ms

P99 TTFT:
93.38 ms

Mean TPOT:
5.35 ms

Mean ITL:
5.40 ms
```

驗證：

```text
Inference Runtime
↓
Benchmark
```

流程正常。

---

# 11. Benchmark Artifact

Day7 Benchmark 使用：

```text
--save-result
```

將正式結果存成：

```text
day7-vllm.json
```

最後保存到：

```text
benchmark/results/day7-vllm.json
```

因此形成：

```text
Inference Runtime
↓
Benchmark
↓
Official JSON Artifact
```

---

# 12. Benchmark Engine

Week15 Day5 已建立正式 Benchmark 能力。

核心方式：

```text
vLLM Official Benchmark Tool
```

而不是自行重造：

```text
HTTP Load Generator
Latency Calculator
Concurrency Engine
```

平台只負責：

```text
執行 benchmark
保存 artifact
分析 result
```

---

# 13. Performance Analyzer Integration

Day6 建立：

```text
analysis/performance_analyzer.py
```

它直接讀：

```text
benchmark/results/
```

裡面的官方 vLLM JSON。

分析：

```text
Concurrency 16
↓
Concurrency 32
↓
Concurrency 64
```

---

# 14. Analyzer Verification

Day7 再次執行：

```bash
python3 analysis/performance_analyzer.py
```

結果：

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

系統仍然具有不錯 scaling。

---

# 15. Saturation Analysis

第二段：

```text
Concurrency 32 -> 64
```

結果：

```text
Throughput: +29.6%

Mean TTFT:
+137.8%

Mean TPOT:
+35.0%

Mean ITL:
+39.2%
```

Analyzer：

```text
SATURATION_CANDIDATE
```

原因：

```text
Latency Cost
>
Throughput Gain
```

代表 workload 已開始進入：

```text
High-load / Saturation Region
```

---

# 16. Training Runtime

Training Runtime 使用：

```text
PyTorch
```

Training workload：

```text
runtime/pytorch/train.py
```

執行方式：

```text
Kubernetes Job
↓
pytorch-training
↓
NVIDIA L4
```

---

# 17. Training Performance Analysis

Day6 使用：

```text
PyTorch Profiler
```

分析：

```text
CPU Time
CUDA Time
Memory
DataLoader
CPU → GPU Copy
Forward
Backward
Optimizer
```

---

# 18. DataLoader Bottleneck

原始設定：

```python
num_workers=0
```

Profiler：

```text
DataLoader CPU total:
44.849 ms

ProfilerStep CPU total:
60.817 ms

Self CPU total:
64.924 ms
```

DataLoader 佔非常明顯 CPU execution time。

因此建立假設：

```text
DataLoader Bottleneck Candidate
```

---

# 19. Controlled Experiment

只修改：

```text
num_workers
```

從：

```text
0
```

改為：

```text
2
```

其他：

```text
Model
Dataset
Batch Size
GPU
Profiler
Optimizer
```

全部不變。

---

# 20. Training Optimization Result

修改後：

```text
DataLoader CPU total:
12.244 ms

ProfilerStep CPU total:
34.939 ms

Self CPU total:
38.913 ms

Self CUDA total:
6.506 ms
```

---

# 21. Performance Improvement

DataLoader：

```text
44.849 ms
→
12.244 ms
```

約改善：

```text
73%
```

Training Step：

```text
60.817 ms
→
34.939 ms
```

約改善：

```text
43%
```

CUDA Compute：

```text
6.122 ms
→
6.506 ms
```

基本沒有重大變化。

因此確認：

```text
Original Bottleneck
=
DataLoader / CPU-side Data Preparation
```

---

# 22. Training Runtime Flow

Training Runtime 完整流程：

```text
Git
↓
ArgoCD
↓
Kubernetes Job
↓
PyTorch Runtime
↓
GPU Training
↓
PyTorch Profiler
↓
Performance Evidence
↓
Bottleneck Analysis
```

---

# 23. Inference Runtime Flow

Inference Runtime 完整流程：

```text
Git
↓
ArgoCD
↓
Kubernetes Deployment
↓
vLLM Runtime
↓
Qwen Model
↓
Inference
↓
vLLM Benchmark
↓
JSON Artifact
↓
Performance Analyzer
```

---

# 24. Prometheus Integration

中央 Prometheus 位於 Taiwan GKE Cluster。

SG vLLM 提供：

```text
/metrics
```

Prometheus 使用：

```text
job_name:
vllm-sg
```

抓取 SG vLLM Runtime Metrics。

---

# 25. Cross-region Monitoring

目前架構：

```text
Taiwan Prometheus
        ↓
VPC Peering
        ↓
SG GPU Node Internal IP
        ↓
NodePort 30800
        ↓
vllm-service
        ↓
vLLM Pod
        ↓
/metrics
```

---

# 26. SG Node Internal IP

目前 SG GPU Node Internal IP：

```text
10.148.0.12
```

vLLM Pod IP：

```text
10.56.0.5
```

兩者不同。

流程：

```text
Prometheus
↓
10.148.0.12:30800
↓
NodePort
↓
Service
↓
Pod 10.56.0.5:8000
```

---

# 27. Static Node IP Limitation

目前 Prometheus config 使用：

```text
10.148.0.12:30800
```

這是：

```text
Lab Workaround
```

不是 production-grade architecture。

原因：

```text
GKE Node 被重建
↓
Internal IP 可能改變
↓
Prometheus Static Target 失效
```

實際上已經發生：

```text
10.148.0.9
→
10.148.0.10
→
10.148.0.11
→
10.148.0.12
```

因此後續 production design 應改為：

```text
Stable Endpoint
或
Service Discovery
```

避免直接綁 Node IP。

---

# 28. Prometheus Target Failure

Day7 一開始：

```text
vllm-sg
```

target：

```text
http://10.148.0.9:30800/metrics
```

已失效。

Prometheus：

```text
health = down
```

錯誤：

```text
context deadline exceeded
```

原因不是 vLLM 壞掉，而是：

```text
Node Internal IP 已改變
```

---

# 29. Prometheus Target Recovery

更新 target：

```text
10.148.0.12:30800
```

之後重新驗證：

```text
scrapeUrl =
http://10.148.0.12:30800/metrics

health =
up

lastError =
empty
```

因此確認：

```text
Taiwan Prometheus
↓
VPC Peering
↓
SG vLLM
```

監控鏈路正常。

---

# 30. Prometheus Query Verification

使用：

```text
up{job="vllm-sg"}
```

查詢。

結果：

```text
value = 1
```

Prometheus：

```text
up = 1
```

代表：

```text
Target 可正常 Scrape
```

---

# 31. Grafana Integration

Grafana：

```text
grafana-69699bfb89-tq7f5
```

狀態：

```text
1/1 Running
```

Grafana datasource 使用 Prometheus。

因此：

```text
Grafana
↓
Prometheus
↓
vllm-sg
↓
SG Runtime Metrics
```

資料鏈路成立。

---

# 32. Observability Flow

完整 Observability：

```text
vLLM Runtime
      ↓
/metrics
      ↓
NodePort
      ↓
VPC Peering
      ↓
Prometheus
      ↓
PromQL
      ↓
Grafana
```

---

# 33. AI Runtime Platform v1

Week15 最終平台：

```text
                    Git
                     │
                     ▼
                   ArgoCD
                     │
                     ▼
                 Kubernetes
                     │
                     ▼
                  GPU Node
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    Training Runtime      Inference Runtime
       PyTorch                 vLLM
          │                     │
          ▼                     ▼
      Training              Inference
          │                     │
          ▼                     ▼
 PyTorch Profiler        vLLM Benchmark
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
             Performance Evidence
                     │
                     ▼
             Performance Analyzer
                     │
                     ▼
                 Prometheus
                     │
                     ▼
                  Grafana
```

---

# 34. Full End-to-End Flow

Day7 最終驗證：

```text
Git Push
      │
      ▼
ArgoCD
      │
      ▼
Kubernetes
      │
      ▼
GPU Runtime
      │
      ├───────────────┐
      ▼               ▼
Training          Inference
PyTorch             vLLM
      │               │
      ▼               ▼
Profiler          Benchmark
      │               │
      └───────┬───────┘
              ▼
     Performance Evidence
              │
              ▼
     Performance Analyzer
              │
              ▼
          Prometheus
              │
              ▼
           Grafana
```

---

# 35. Week15 Day1-7 Integration

Week15：

```text
Day1
PyTorch GPU Runtime

Day2
PyTorch Training Runtime

Day3
vLLM Inference Runtime + Monitoring

Day4
Runtime Abstraction / RuntimeManager

Day5
Benchmark Engine

Day6
Performance Analyzer

Day7
AI Runtime Platform v1 Integration
```

最後形成：

```text
AI Runtime Platform v1
```

---

# 36. Platform Capability

現在平台已具有：

```text
GPU Runtime
Training Runtime
Inference Runtime
Runtime Abstraction
Benchmark Capability
Profiler Capability
Performance Analysis
Bottleneck Diagnosis
GitOps Deployment
Kubernetes Scheduling
GPU Scheduling
Prometheus Monitoring
Grafana Visualization
Cross-region Runtime Monitoring
```

---

# 37. Performance Engineering Workflow

Week15 最重要的 Performance Engineering 流程：

```text
Run Workload
↓
Measure
↓
Profile
↓
Collect Evidence
↓
Find Bottleneck
↓
Create Hypothesis
↓
Controlled Experiment
↓
Validate Improvement
↓
Recommendation
```

---

# 38. Day7 驗證成果

完成：

```text
[✓] Git → ArgoCD
[✓] ArgoCD → Kubernetes
[✓] Kubernetes → GPU Node
[✓] vLLM Inference Runtime
[✓] Qwen Model Serving
[✓] Inference Runtime → Benchmark
[✓] Benchmark → JSON Artifact
[✓] JSON → Performance Analyzer
[✓] Scaling Diagnosis
[✓] Saturation Diagnosis
[✓] PyTorch Training Runtime
[✓] PyTorch Profiler
[✓] DataLoader Bottleneck Analysis
[✓] Prometheus → SG vLLM
[✓] Prometheus Target UP
[✓] Grafana Runtime
```

---

# 39. Known Technical Debt

目前仍有一個明確的 lab limitation：

```text
Prometheus vllm-sg target
使用 SG Node Internal IP
```

例如：

```text
10.148.0.12:30800
```

GKE Node 重建後：

```text
IP 可能改變
```

因此 production-grade 版本應使用：

```text
Stable Internal Endpoint
Service Discovery
Internal Load Balancer
或其他跨 Cluster Monitoring Architecture
```

而不是 static Node IP。

---

# 40. Day7 Final Result

Week15 Day7 正式完成：

```text
AI Runtime Platform v1
```

平台已經從：

```text
單獨的 GPU Workload
```

進化成：

```text
GitOps Managed
Kubernetes-based
GPU Runtime Platform
```

並整合：

```text
Training
Inference
Benchmark
Profiler
Performance Analyzer
Prometheus
Grafana
```

---

# Interview Review

## Q1：你的 AI Runtime Platform v1 解決什麼問題？

它提供一條完整 GPU workload lifecycle：

```text
Git
↓
GitOps Deployment
↓
Kubernetes GPU Runtime
↓
Training / Inference
↓
Benchmark / Profiling
↓
Performance Analysis
↓
Monitoring
```

因此平台不只可以執行 AI workload，也能分析 workload 的：

```text
Throughput
Latency
GPU Behavior
CPU Behavior
DataLoader Bottleneck
Serving Saturation
```

---

## Q2：Benchmark、Profiler、Performance Analyzer 有什麼差別？

Benchmark：

```text
量整體 workload performance
```

例如：

```text
Throughput
TTFT
TPOT
ITL
```

Profiler：

```text
看 workload 內部時間花在哪裡
```

例如：

```text
CPU Operation
CUDA Kernel
DataLoader
Memory Copy
Forward
Backward
```

Performance Analyzer：

```text
讀取 Benchmark / Profiler Evidence
↓
比較不同 experiment
↓
判斷 performance behavior
↓
找 bottleneck
↓
產生 recommendation
```

三者角色不同：

```text
Benchmark
=
What happened?

Profiler
=
Where did the time go?

Performance Analyzer
=
Why did performance behave this way?
```

---

# Week15 Complete

Week15 最終成果：

```text
AI Runtime Platform v1

Training Runtime
+
Inference Runtime
+
Benchmark Engine
+
Performance Analyzer
+
GitOps
+
Kubernetes
+
GPU
+
Prometheus
+
Grafana
```

完整流程：

```text
Git Push
↓
ArgoCD
↓
Kubernetes
↓
GPU Runtime
↓
Training / Inference
↓
Benchmark / Profiler
↓
Performance Analysis
↓
Prometheus
↓
Grafana
```

Week15 完成。
