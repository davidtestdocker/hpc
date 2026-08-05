# Week12 Day6 - Linux CPU Profiling with perf

## 目標

本章節學習使用 Linux `perf` 進行 CPU Profiling，了解 CPU Time 實際花費的位置，並學會判讀 `perf stat`、`perf record`、`perf report` 的結果，建立 Linux Performance Profiling 的基本能力。

完成本章後，可以回答：

- `perf` 是什麼？
- `perf stat`、`perf record`、`perf report` 有什麼差異？
- 如何判斷程式是 CPU Bound 還是 IO Bound？
- `task-clock` 代表什麼？
- `context-switches` 是什麼？
- `cpu-migrations` 是什麼？
- `page-faults` 是錯誤嗎？
- 為什麼在雲端 VM 上看不到 `cycles` 與 `instructions`？

---

# 今日學習重點

- Linux perf
- CPU Profiling
- Software Event
- task-clock
- Context Switch
- CPU Migration
- Page Fault
- CPU Bound
- IO Bound

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

Environment

```text
Google Cloud Platform VM
```

Profiler

```text
perf
```

Benchmark

```text
sysbench
```

---

# 為什麼需要 Profiling？

Benchmark 可以回答：

```
程式有多快？
```

Profiling 則回答：

```
CPU 時間花在哪裡？
```

Performance Engineer 的分析流程：

```
Benchmark
        │
        ▼
Measure
        │
        ▼
Profiling
        │
        ▼
Find Hotspot
        │
        ▼
Optimize
```

---

# perf 是什麼？

`perf`

為 Linux 官方提供的 Performance Profiling 工具。

可用於分析：

- CPU 使用時間
- Function Hotspot
- Scheduler
- Context Switch
- Cache
- Branch
- Hardware Counter（需硬體支援）

---

# perf 三種主要模式

| 指令 | 用途 |
|------|------|
| `perf stat` | 收集整體效能統計 |
| `perf record` | 收集 CPU Sampling |
| `perf report` | 查看 Profiling 結果 |

---

# Step1：perf stat

執行：

```bash
perf stat sysbench cpu run
```

範例：

```text
task-clock
context-switches
cpu-migrations
page-faults
```

`perf stat`

主要回答：

```
程式執行期間

CPU 發生了哪些事件？
```

---

# task-clock

例如：

```text
10008 ms task-clock
```

代表：

CPU 真正工作的時間。

不是：

```
Wall Time
```

而是：

```
CPU Time
```

---

## CPU Bound

例如：

```
Real Time

10 秒

Task Clock

9.9 秒
```

代表：

CPU 幾乎持續工作。

屬於：

```
CPU Bound
```

---

## IO Bound

例如：

```
Real Time

10 秒

Task Clock

2 秒
```

代表：

CPU 真正工作時間很少。

剩餘時間可能等待：

- Disk
- Database
- Network
- Lock

屬於：

```
IO Bound
```

---

# Context Switch

例如：

```text
102 context-switches
```

代表：

Linux Scheduler

切換 Process 或 Thread 的次數。

例如：

```
Thread A

↓

Thread B
```

CPU 需要：

- 保存 Register
- 載入 Register
- 切換 Stack

因此：

Context Switch

具有一定成本。

---

## Context Switch 過高

若：

```
Throughput 沒增加

Context Switch 卻大量增加
```

可能代表：

- Thread 過多
- Scheduler 負擔增加
- 排程成本開始影響效能

---

# CPU Migration

例如：

```text
10 cpu-migrations
```

代表：

Linux Scheduler

將 Thread

從一顆 CPU

搬移到另一顆 CPU。

例如：

```
CPU0

↓

CPU2
```

---

## 為什麼會 Migration？

Scheduler

希望平衡各 CPU 負載。

例如：

```
CPU0

100%

↓

四顆 CPU

平均工作
```

---

## Migration 過高

Migration

可能造成：

- CPU Cache 失效
- Scheduler 成本增加

在：

- HPC
- AI Training
- NUMA

通常會透過：

- CPU Affinity
- CPU Pinning

降低 Migration。

---

# Page Fault

例如：

```text
860 page-faults
```

Page Fault

並不代表程式錯誤。

Linux 採用：

```
Virtual Memory
```

第一次存取 Memory 時，

Kernel

建立：

```
Virtual Memory

↓

Physical Memory
```

即會發生：

```
Minor Page Fault
```

屬於正常現象。

---

## Major Page Fault

若：

RAM 不足，

Linux

需要：

```
Disk

↓

Swap

↓

RAM
```

則會發生：

```
Major Page Fault
```

速度遠慢於 RAM，

可能造成明顯效能下降。

---

# perf record

執行：

```bash
perf record -g -- sysbench cpu run
```

作用：

持續收集 CPU Sampling，

並產生：

```
perf.data
```

供後續分析。

---

# perf report

執行：

```bash
perf report
```

可查看：

CPU Hotspot。

例如：

```
Function A

35%

Function B

20%
```

若 Binary

沒有 Debug Symbol，

則可能只能看到：

```
Memory Address
```

而無法顯示 Function Name。

---

# GCP VM 的限制

本次實驗：

```text
cycles

instructions

branch-misses
```

皆顯示：

```text
<not supported>
```

原因：

Google Cloud VM

未提供完整 Hardware PMU。

因此：

本章主要學習：

Software Event Profiling。

Hardware Counter

將於具備 PMU 的環境再深入探討。

---

# Performance Analysis 流程

```
Application Slow
        │
        ▼
Benchmark
        │
        ▼
perf stat
        │
CPU Bound？
        │
 ┌──────┴──────┐
 │             │
Yes           No
 │             │
 ▼             ▼
perf record   分析 I/O、DB、Network
 │
 ▼
perf report
 │
 ▼
Find Hotspot
 │
 ▼
Optimize
```

---

# 今日重點

- `perf` 是 Linux 官方 Performance Profiling 工具。
- `perf stat` 用於收集整體 CPU 執行統計。
- `task-clock` 可協助判斷 CPU Bound 與 IO Bound。
- `context-switches` 過高可能代表排程成本增加。
- `cpu-migrations` 過高可能造成 CPU Cache 失效。
- `page-faults` 大多屬於正常的 Minor Page Fault。
- `perf record` 建立 Sampling。
- `perf report` 用於分析 CPU Hotspot。

---

# Interview

## Q1：`perf stat`、`perf record`、`perf report` 有什麼差異？

**答：**

- `perf stat`：收集整體效能統計，例如 task-clock、context-switches、page-faults。
- `perf record`：收集 CPU Sampling，建立 `perf.data`。
- `perf report`：分析 `perf.data`，找出 CPU Hotspot。

---

## Q2：如何利用 `task-clock` 判斷 CPU Bound 或 IO Bound？

**答：**

若 `task-clock` 接近程式實際執行時間（Wall Time），代表 CPU 大部分時間都在運算，屬於 CPU Bound；若 `task-clock` 明顯小於 Wall Time，則表示程式大量時間可能在等待 Disk、Database、Network 或 Lock，屬於 IO Bound。

---

## Q3：`page-faults` 是否代表程式發生錯誤？

**答：**

不一定。大部分 Page Fault 屬於 Minor Page Fault，是 Linux 建立 Virtual Memory 與 Physical Memory 映射時的正常行為；只有因 RAM 不足而需要從 Swap 或 Disk 載入資料的 Major Page Fault，才可能造成明顯的效能問題。
