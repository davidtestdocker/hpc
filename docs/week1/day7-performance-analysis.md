# Week 1 Day 7－Performance Analysis（效能分析）

[上一課](<day6-disk-io.md>) · [本週目錄](README.md) · [下一週](../week2/README.md)

## 今日目標

建立 Performance Engineer 的分析思維。

理解效能分析不是猜測，而是透過資料一步一步排除瓶頸，最後找出真正影響系統效能的原因。

---

# 為什麼需要 Performance Analysis？

假設未來平台執行 Benchmark 後得到：

```
TPS = 20
```

這只能代表：

系統效能不好。

但是：

不知道原因。

真正重要的是回答：

- CPU 是否成為瓶頸？
- Memory 是否不足？
- Disk 是否過慢？
- Network 是否有問題？
- GPU 是否已經滿載？

Performance Engineer 的工作就是找出真正原因，而不是猜測。

---

# Performance Analysis 的流程

未來整個平台都會遵循固定分析流程：

```
Benchmark

↓

Process

↓

CPU

↓

Memory

↓

Disk

↓

Network

↓

GPU

↓

Application

↓

Performance Report
```

每一層都負責排除一種可能性。

---

# 第一層：Process

先確認有哪些 Process 正在執行。

例如：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

確認是否有異常 Process。

---

# 第二層：CPU

查看：

- CPU Usage
- User Time
- System Time
- Idle Time

確認：

CPU 是否真的很忙。

如果 CPU Idle 很高，就代表 CPU 並不是瓶頸。

---

# 第三層：Memory

查看：

```bash
free -h
```

確認：

- Available Memory
- 是否還有足夠 RAM

如果 Available 很高，Memory 通常不是瓶頸。

---

# 第四層：Disk

查看：

```bash
iostat
```

重點觀察：

```
%iowait
```

如果 iowait 很高，代表 CPU 花大量時間等待磁碟。

Disk I/O 很可能就是瓶頸。

---

# 第五層：Network

目前尚未學習。

Week 1 結束後會開始加入。

---

# 第六層：GPU

目前尚未學習。

Week 9 開始加入 GPU 與 vLLM。

---

# 第七層：Application

如果：

- CPU 正常
- Memory 正常
- Disk 正常
- Network 正常
- GPU 正常

才開始懷疑：

- Benchmark Worker
- vLLM
- FastAPI
- Application Logic

---

# Week 1 學習成果

本週建立了 Linux Performance Analysis 的基礎觀念：

- Program
- Process
- Scheduler
- Context Switch
- CPU Utilization
- Memory
- Disk I/O

理解 Linux 如何執行程式，以及如何分析 CPU、Memory、Disk 是否成為系統瓶頸。

---

# 與 HPC AI Performance Engineering Platform 的關聯

Week 2 開始將建立 Monitoring Framework：

```
monitoring/

process_monitor.py
cpu_monitor.py
memory_monitor.py
disk_monitor.py
system_monitor.py
```

這些模組的目的不是單純收集資料，而是提供 Performance Analysis 所需的資訊。

未來平台將自動完成：

```
Benchmark

↓

Collect Metrics

↓

Performance Analysis

↓

Optimization Report
```

這也是整個 HPC AI Performance Engineering Platform 的核心能力。

---

# Week 1 重點整理

本週建立了 Performance Engineer 最重要的分析流程：

```
Program
        │
        ▼
Process
        │
        ▼
CPU
        │
        ▼
Memory
        │
        ▼
Disk
        │
        ▼
Performance Analysis
```

之後所有 Monitoring、Benchmark、Analysis、Optimization 都會建立在這個基礎之上。

## 補充：2026-09-23 實際執行與解讀

以下是助理在目前 Linux 工作環境新執行的結果，原有教材與舊觀察保留在上方。這次程序清單受執行沙箱限制；整機 CPU、記憶體與裝置統計的可見範圍不一定與程序清單相同。不能把新結果冒充當年的 VM 紀錄。

各指令的時間、參數與結束碼見 [執行紀錄](results/20260923/execution.json)。

本課的 `free -h` 與 `iostat` 已在同次採集執行，可直接讀 [記憶體完整輸出](results/20260923/free-h.stdout.txt) 與 [I/O 完整輸出](results/20260923/iostat.stdout.txt)，解讀分別補在 Day5、Day6。

原文 `TPS = 20` 是假設數字，沒有對應的 benchmark 程式、輸入或目標，不能當成實測，也不能單憑 20 判斷快慢。原文列出的監控模組與自動報告流程是構想，並非這次已執行的功能。

分析時，整機 idle 高不排除單核心受限，available 高不排除記憶體頻寬問題，低 iowait 也不保證所有 I/O 正常；不必等排除所有硬體後才查看程式錯誤。這些是對上方舊教材的補充，舊文內容保留。
