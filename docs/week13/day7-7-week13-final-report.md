<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-7 — Week13 整合報告子章

[上一課](<day7-6-result-integration.md>) · [本週目錄](README.md) · [下一課](<day7-benchmark-report.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史綜合報告。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

本課Random標示與run_fio.sh readwrite不符，修正為混合順序。保存summary不等於完整歷史artifact；PG退出碼缺口也適用此報告。

## 程式／設定與來源

本次核對：[benchmark/run_all.sh](<../../benchmark/run_all.sh>)、[benchmark/storage/run_fio.sh](<../../benchmark/storage/run_fio.sh>)、[benchmark/postgres/run_pgbench.sh](<../../benchmark/postgres/run_pgbench.sh>)

## 已有結果與解讀

來源：[記錄／示例原文](<day7-7-week13-final-report.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Random Read/Write
```

框架目前是獨立shell工具集，不等於API真實CPU/memory/disk分支；HTML/Grafana歷史比較是計畫。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
