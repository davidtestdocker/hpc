<!-- readable-curriculum: 2026-09-22 -->
# Week12 Day5 — CPU baseline 與 sysbench

[上一課](<Day4-Linux-Historical-Performance-Analysis.md>) · [本週目錄](README.md) · [下一課](<Day6-Linux-CPU-Profiling-with-perf.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史sysbench表格。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

1與4threads吞吐約2.22倍，不能僅凭此歸因context switch；SMT、主機干擾等需證據。sysbench也可作壓力負載，工具不是互斥分類；4threads不保證固定4CPU。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<Day5-Linux-CPU-Benchmark-with-sysbench.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
8024.75
```

3615.85→8024.75 events/s是本 workload 基線，缺重複量測／變異；不是通用CPU分數。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 診斷方法繼續適用；舊 perf／strace／CPU 數據不代表主 MPI 的自動 profiling。
> **閱讀順序**：先學本文基礎，再讀[Week12 現行對照與檢核](../learning-guide.md#week12)及[對應現行入口](../performance/performance-report.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week12 Day5 - Linux CPU Benchmark with sysbench

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[performance-report](../performance/performance-report.md)。

---

## 目標

本章節學習使用 `sysbench` 建立可重現的 CPU Benchmark，了解 Benchmark 的概念，並學會分析 Throughput、Latency、Scaling 與 Baseline，建立 Performance Engineering 的基本思維。

完成本章後，可以回答：

- Benchmark 是什麼？
- Benchmark 與 Stress Test 有什麼差異？
- 為什麼 Performance Engineer 需要 Benchmark？
- `sysbench cpu` 在測什麼？
- `events per second` 是什麼？
- Throughput 與 Latency 有什麼差異？
- 為什麼增加 Threads 不一定有線性成長？
- 如何建立 Performance Baseline？

---

# 今日學習重點

- Benchmark
- Stress Test
- Throughput
- Latency
- Thread
- Scaling
- Performance Baseline
- sysbench CPU Benchmark

---

# Lab Environment

OS

```text
Ubuntu 24.04
```

CPU

```text
AMD EPYC 7B12
```

Logical CPU

```text
4 vCPU
```

Benchmark Tool

```text
sysbench 1.0.20
```

---

# 為什麼需要 Benchmark？

Performance Engineer 的工作流程：

```
建立 Workload
        │
        ▼
Benchmark
        │
        ▼
Measure
        │
        ▼
Analyze
        │
        ▼
Optimize
```

沒有 Benchmark，

就沒有可比較的效能數據。

---

# Benchmark 與 Stress Test

Benchmark

目的：

```
量測效能
```

特色：

- 固定工作量
- 可重現
- 可比較

---

Stress Test

目的：

```
測試系統極限
```

特色：

- 持續增加負載
- 驗證穩定性
- 找出瓶頸

例如：

| 工具 | 類型 |
|------|------|
| sysbench | Benchmark |
| stress-ng | Stress Test |

---

# 為什麼選擇 sysbench？

Linux 上常見 Benchmark 工具：

- sysbench
- fio
- Phoronix Test Suite
- SPEC CPU（商業）

本課程使用：

```
sysbench
```

原因：

- 安裝簡單
- 免費
- 可測 CPU、Memory、Threads
- 適合作為後續 `perf`、`strace` 的分析目標

---

# Step1：確認版本

```bash
sysbench --version
```

輸出：

```text
sysbench 1.0.20
```

---

# Step2：CPU Benchmark

執行：

```bash
sysbench cpu run
```

範例輸出：

```text
CPU speed:
events per second: 3615.85
```

---

# sysbench CPU 在測什麼？

`sysbench cpu`

主要透過：

```
Prime Number Calculation
```

大量計算質數。

因此：

- CPU Bound
- 不依賴 Disk
- 不依賴 Network
- 可重現

適合作為 CPU Benchmark。

---

# Number of threads

例如：

```text
Number of threads: 1
```

代表：

```
sysbench 建立 1 個 Worker Thread
```

不是：

- 1 顆 CPU
- 1 個 Core

而是：

```
1 個 Software Thread
```

若：

```bash
sysbench cpu --threads=4 run
```

代表：

建立：

```
Thread1
Thread2
Thread3
Thread4
```

Linux Scheduler

將它們排程到：

```
CPU0
CPU1
CPU2
CPU3
```

---

# events per second

例如：

```text
events per second: 3615.85
```

代表：

```
每秒完成約 3616 次 Benchmark 工作
```

這是：

```
CPU Throughput
```

也是：

CPU Benchmark

最重要的指標。

---

# total time

預設：

```text
10 秒
```

因此：

```
total time
```

通常固定。

真正比較 CPU：

應看：

```
events per second
```

而不是：

```
total time
```

---

# total number of events

例如：

```text
36162
```

代表：

10 秒內：

總共完成：

36162 次 Benchmark 工作。

關係：

```
events/sec

×

Benchmark 時間

≈

total events
```

---

# Latency

Latency：

代表：

```
完成一次 Benchmark 工作所需時間
```

例如：

```text
avg latency

0.28 ms
```

Throughput：

```
每秒完成多少工作
```

Latency：

```
完成一次工作需要多久
```

兩者都屬於重要效能指標。

---

# Throughput vs Latency

| 指標 | 代表 |
|------|------|
| Throughput | 每秒完成多少工作 |
| Latency | 完成一次工作所需時間 |

例如：

AI Training：

通常重視：

```
Throughput
```

AI Inference：

通常重視：

```
Latency
```

---

# Multi-thread Benchmark

執行：

```bash
sysbench cpu --threads=4 run
```

例如：

```
1 Thread

3615 events/sec
```

```
4 Threads

8025 events/sec
```

並非：

```
3615 × 4
```

原因：

- Scheduler
- Context Switch
- Cache
- VM 資源競爭
- Hypervisor

因此：

增加 Thread

不代表：

效能一定線性成長。

---

# Scaling

理論：

```
1 Thread

↓

4 Thread

↓

4 倍效能
```

實際：

```
3615

↓

8025
```

約：

```
2.22 倍
```

代表：

沒有完全線性擴展。

---

# Threads Fairness

例如：

```text
events(avg/stddev)
```

用途：

觀察：

多個 Worker Thread

是否平均分配工作。

單執行緒：

```
stddev = 0
```

屬於正常。

多執行緒：

stddev 越小，

代表：

Load Balance 越好。

---

# Performance Baseline

Benchmark

不只是：

跑一次。

更重要的是：

建立：

Baseline。

例如：

| CPU | Threads | Events/sec | Avg Latency |
|------|---------|-----------:|------------:|
| AMD EPYC 7B12 | 1 | 3615.85 | 0.28 ms |
| AMD EPYC 7B12 | 4 | 8024.75 | 0.50 ms |

未來：

升級：

- Kernel
- VM
- CPU

即可：

比較：

Performance Regression。

---

# 今日重點

- `sysbench` 是 Benchmark，不是 Stress Test。
- `sysbench cpu` 使用質數計算測試 CPU。
- `events per second` 是 CPU Throughput，也是最重要的 Benchmark 指標。
- Throughput 與 Latency 代表不同效能面向。
- 增加 Threads 不代表效能一定線性成長。
- Performance Engineer 需要建立 Baseline，才能比較不同環境的效能。

---

# Interview

## Q1：Benchmark 與 Stress Test 有什麼差異？

**答：**

Benchmark 用於量測效能，在固定條件下建立可重現、可比較的結果，例如使用 `sysbench` 比較不同 CPU 或 VM 的效能；Stress Test 則用於驗證系統在高負載下的穩定性，例如使用 `stress-ng` 持續將 CPU 或 Memory 壓到接近極限。

---

## Q2：為什麼 `events per second` 比 `total time` 更重要？

**答：**

`sysbench cpu run` 預設執行約 10 秒，因此 `total time` 幾乎固定；真正反映 CPU 計算能力的是 `events per second`，代表 CPU 在固定 Benchmark 下每秒能完成多少工作，適合作為不同 VM、CPU 或 Kernel 的效能比較依據。

---

## Q3：增加 Threads 後，效能一定會線性提升嗎？

**答：**

不一定。增加 Threads 可能受到 CPU Scheduler、Context Switch、Cache、Hypervisor 或其他資源競爭影響，因此 Throughput 雖然通常會提升，但不一定能達到理論上的線性擴展。
