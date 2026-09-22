<!-- readable-curriculum: 2026-09-22 -->
# Week15 Day7 — 現行 runtime 整合範圍

[上一課](<Day6-Performance-Analyzer.md>) · [本週目錄](README.md) · [下一週](../week16/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

runner 產生 Pod／ConfigMap、等待完成、收回 raw bundle，成功後清理本次資源；這是一條獨立實驗流程，不是 MPI 完成後接著訓練。失敗會保留診斷資料。

## 在現在的專案中

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

本課對照：[scripts/run_causal_lm_benchmark.py](<../../scripts/run_causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def run(context, name, output):
    """用明確 context 和唯一名稱執行一次實驗；失敗時保留現場供排查。"""
    # exist_ok=False 防止重跑覆寫舊證據；目錄建立後即保存本次輸入。
    output.mkdir(parents=True, exist_ok=False)
    base = ['kubectl', '--context', context, '--request-timeout=30s', '-n', 'hpc-platform-dev']

    def kubectl(args, data=None):
        """以參數陣列呼叫 kubectl；可用 stdin 傳 manifest，失敗立即拋出例外。"""
        return subprocess.check_output(base + args, input=data, timeout=90)

    # corpus 和程式可能日後改動，因此本次快照與現行原始碼分開保存。
    source = (ROOT / 'benchmark/gpu/causal_lm_benchmark.py').read_text()
    corpus = (ROOT / 'README.md').read_text()
    (output / 'corpus.txt').write_text(corpus)
    (output / 'benchmark-source.py').write_text(source)
    cm = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': name},
          'data': {'causal_lm_benchmark.py': source, 'corpus.txt': corpus}}
    # nodeSelector 決定 GPU pool；toleration 允許接受 GPU taint。
    # nvidia.com/gpu=1 在此叢集是一個 time-sharing share，不是額外建立一張 GPU。
    # 成功後 sleep 保留容器供 exec 取檔；emptyDir 隨 Pod 刪除，必須先收回結果。
    pod = {'apiVersion': 'v1', 'kind': 'Pod', 'metadata': {'name': name,
           'labels': {'app': 'causal-lm-benchmark'}}, 'spec': {
        'restartPolicy': 'Never', 'activeDeadlineSeconds': 1200,
        'nodeSelector': {'cloud.google.com/gke-nodepool': 'gpu-pool'},
```

## 已有結果與解讀

### 單 L4 訓練：已保存的實測數據

日期：2026-09-22；環境：GKE hpc-gpu-sg、單 NVIDIA L4、PyTorch 2.12.0+cu126。模型為 13M causal LM、byte tokenizer，不是 pretrained 大模型。20 warmup、40 measured steps，各 batch 三次交錯量測。

| Batch | 次數 | Mean byte tokens/s | Mean step ms | Peak allocated MiB | Throughput CV |
|---:|---:|---:|---:|---:|---:|
| 8 | 3 | 110,785 | 18.50 | 375.02 | 3.21% |
| 16 | 3 | 200,841 | 20.39 | 532.39 | 0.42% |

結果：吞吐 **+81.29%**，每步時間 **+10.25%**，顯存峰值 **+41.96%**。每步工作量加倍，所以不是「每步變快」，也不能推出模型品質更好。

另做的五步 CUDA profiling：batch 8／16 的 multi-tensor kernel 累積時間約 21.71／21.72 ms，GEMM 約 12.27／23.84 ms。這支持每步固定 optimizer 成本被較大 batch 攤薄的推論；kernel 時間總和不是 wall time，也不直接證明 compute-bound 或 memory-bound。

你不需要再跑 GPU：[保存的摘要](<../../benchmark/results/causal-lm-20260922/summary.json>)、[原始逐步數據](<../../benchmark/results/causal-lm-20260922/result.json>)、[完整解讀與限制](<../performance/causal-lm-l4-20260922.md>)已足夠直接閱讀。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week15/Day7-AI-Runtime-Platform-v1-Integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新 13M causal LM／單 L4 profiling 是獨立 runner，未接 MPI API；舊 runtime／vLLM 紀錄不改寫為新實驗。
> **閱讀順序**：先學本文基礎，再讀[Week15 現行對照與檢核](../learning-guide.md#week15)及[對應現行入口](../runbooks/causal-lm-benchmark.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week15 Day7 - AI Runtime Platform v1 Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [analysis/performance_analyzer.py](../../analysis/performance_analyzer.py)：效能結果分析
- [benchmark/results/day7-vllm.json](../../benchmark/results/day7-vllm.json)
- [helm/pytorch-runtime/values.yaml](../../helm/pytorch-runtime/values.yaml)
- [helm/vllm/values.yaml](../../helm/vllm/values.yaml)
- [runtime/base.py](../../runtime/base.py)：runtime 抽象介面
- [runtime/manager.py](../../runtime/manager.py)：runtime 選擇入口
- [runtime/pytorch/runtime.py](../../runtime/pytorch/runtime.py)：PyTorch runtime
- [runtime/pytorch/train.py](../../runtime/pytorch/train.py)：GPU 訓練與 profiler
- [runtime/vllm/runtime.py](../../runtime/vllm/runtime.py)：vLLM HTTP runtime

---

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
