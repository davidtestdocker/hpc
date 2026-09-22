<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-7 — Week13 整合報告子章

[上一課](<day7-6-result-integration.md>) · [本週目錄](README.md) · [下一課](<day7-benchmark-report.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

報告依序交代問題、控制條件、結果、解釋和限制。一次調校沒有改善也可形成有效結論，前提是方法可靠，而非只挑成功或隱藏代價。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[docs/performance/causal-lm-l4-20260922.md](<../performance/causal-lm-l4-20260922.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
## 未開 profiler 的結果

| Batch | Mean byte tokens/s | Mean step | Throughput CV | Max peak allocated |
|---:|---:|---:|---:|---:|
| 8 | 110,785 | 18.50 ms | 3.21% | 375.02 MiB |
| 16 | 200,841 | 20.39 ms | 0.42% | 532.39 MiB |

Batch 8→16：throughput **+81.29%**、step latency **+10.25%**、peak allocated
memory **+41.96%**。單步工作量加倍，因此 throughput 提升並非每步變快。
本次 batch 8 的三次範圍為 107,240～114,348；batch 16 為 199,914～201,588。
這是單次實驗中的三次重複，沒有跨日／跨機器的統計推廣。

## Profiling 如何解釋這個取捨

分析器只加總 raw trace 的 `cat=kernel, ph=X` 事件，避免 CPU operator、
record_function 與 GPU kernel 被重複加總。以下皆為 **五步 profiling** 的 CUDA
kernel duration sum，不能當 wall time、GPU utilization 或硬體峰值效率。

| Trace 觀察 | Batch 8 | Batch 16 |
|---|---:|---:|
| CUDA kernel events | 1,575 | 1,665 |
| 全部 kernel duration sum | 48.81 ms | 78.04 ms |
| 名稱包含 multi_tensor 的 kernel sum | 21.71 ms | 21.72 ms |
| 名稱包含 GEMM 的 kernel sum | 12.27 ms | 23.84 ms |
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day7-7-week13-final-report.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day7-7 - Week13 Final Report

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/cpu/results/cpu_benchmark_20260810.md](../../benchmark/cpu/results/cpu_benchmark_20260810.md)
- [benchmark/network/results/iperf3_20260810.md](../../benchmark/network/results/iperf3_20260810.md)
- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口
- [benchmark/storage/results/fio_20260810.md](../../benchmark/storage/results/fio_20260810.md)

---

# Week13 Objective

完成 HPC AI Benchmark Platform 第一版。

本週目標：

建立可重複執行的 Benchmark Framework，

並完成：

- CPU Benchmark
- Storage Benchmark
- PostgreSQL Benchmark
- Network Benchmark

最後整合為統一 Benchmark Framework。

---

# Week13 Architecture

```text
                  Benchmark Runner

                        │

                   run_all.sh

                        │

      ┌─────────┬─────────┬──────────┬──────────┐

      │         │         │          │

     CPU     Storage   PostgreSQL  Network

      │         │         │          │

 stress-ng      fio     pgbench    iperf3

      │         │         │          │

      └─────────┴─────────┴──────────┘

                        │

                 Result Collection

                        │

             results/<timestamp>/

                        │

       cpu.log
       storage.log
       postgres.log
       network.log
```

---

# Platform Components

Benchmark Runner

```text
benchmark Pod
```

Framework

```text
run_all.sh
```

CPU

```text
stress-ng
```

Storage

```text
fio
```

Database

```text
pgbench
```

Network

```text
iperf3
```

---

# Week13 Completed

## CPU Benchmark

Tool

```text
stress-ng
```

完成：

- CPU Stress Test
- Multi Worker
- CPU Throughput
- CPU Benchmark Script

---

## Storage Benchmark

Tool

```text
fio
```

完成：

- Random Read/Write
- IOPS
- Bandwidth
- Latency
- Storage Benchmark Script

---

## PostgreSQL Benchmark

Tool

```text
pgbench
```

完成：

- TPS
- Latency
- Client Benchmark
- PostgreSQL Benchmark Script

---

## Network Benchmark

Tool

```text
iperf3
```

完成：

- TCP Throughput
- Sender
- Receiver
- Retransmission
- Kubernetes Service Benchmark

---

# Benchmark Framework

Framework：

```text
run_all.sh
```

功能：

- Execute Benchmark
- PASS / FAIL
- Fail Fast
- Exit Code Validation
- Benchmark Summary

---

# Result Integration

Framework：

每次執行：

建立：

```text
results/<timestamp>/
```

Result：

```text
cpu.log

storage.log

postgres.log

network.log
```

所有 Benchmark：

集中保存。

---

# Framework Design

Benchmark Module：

只負責：

```text
Run Benchmark
```

Framework：

負責：

```text
Run

↓

Collect

↓

Save

↓

Summary
```

完成：

Separation of Responsibilities。

---

# Week13 Skills

完成：

Linux

- stress-ng
- fio
- iperf3
- pgbench

Kubernetes

- Benchmark Runner
- Service
- Pod Communication

Shell

- Function
- Exit Code
- pipefail
- tee
- Framework Design

Performance Engineering

- CPU
- Storage
- Database
- Network

---

# Platform Capability

目前平台：

已具備：

✅ CPU Benchmark

✅ Storage Benchmark

✅ PostgreSQL Benchmark

✅ Network Benchmark

✅ Benchmark Runner

✅ Benchmark Framework

✅ Result Collection

✅ Benchmark History

---

# Week13 Directory

```text
benchmark/

├──cpu/
│
├──storage/
│
├──postgres/
│
├──network/
│
├──results/
│
└──run_all.sh
```

---

# Platform Improvement

目前：

Framework Version

```text
v2
```

下一階段：

- Python Benchmark Framework
- JSON Output
- HTML Report
- Benchmark Dashboard
- Grafana Integration
- Historical Comparison

---

# Interview Questions

## Q1

為什麼建立 Benchmark Framework？

Answer：

統一管理不同 Benchmark，

降低人工操作，

提高 Benchmark Automation。

---

## Q2

為什麼需要 Benchmark Runner？

Answer：

建立固定 Runtime，

避免每次重新建立 Benchmark Environment。

---

## Q3

Framework 與 Benchmark Module 如何分工？

Answer：

Module：

只負責執行 Benchmark。

Framework：

負責：

- Execute
- Error Handling
- Result Collection
- Summary

---

## Q4

為什麼使用 tee？

Answer：

同時：

輸出 Terminal

與

保存 Log。

---

## Q5

為什麼使用 pipefail？

Answer：

避免：

Pipeline 中：

Benchmark Fail，

但 tee Success，

造成誤判。

---

# Week13 Conclusion

Week13 完成 HPC AI Benchmark Platform 第一版。

建立：

- Modular Benchmark Architecture
- Benchmark Framework
- Result Integration
- Benchmark Runner
- Performance Baseline

平台已具備 CPU、Storage、Database、Network Benchmark 能力。

下一週將進入 GPU Platform，加入 CUDA、GPU Monitoring 與 GPU Performance Benchmark。
