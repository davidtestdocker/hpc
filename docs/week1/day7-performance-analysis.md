<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day7 — 系統效能分析流程

[上一課](<day6-disk-io.md>) · [本週目錄](README.md) · [下一週](../week2/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：概念示例與未落實規劃。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現有 monitoring/ 只保存 process_monitor.py，沒有 cpu_monitor.py、memory_monitor.py、disk_monitor.py、system_monitor.py。CPU 整體 idle 高仍可能單核心受限；available 高不排除記憶體頻寬瓶頸；也不必等所有硬體都排除才調查 application logic。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day7-performance-analysis.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
TPS = 20
```

原文明寫「假設」：TPS=20 是示例，沒有 workload、baseline 或目標，不能直接解讀成效能不好。cpu_monitor.py 等模組是規劃，不是已交付的監控框架。

**仍缺的證據／不能證明的事：** 沒有完整 Benchmark→自動收所有 metrics→分析報告的本課執行結果；不再把規劃寫成現行功能。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 7－Performance Analysis（效能分析）

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

規劃中的 `cpu_monitor.py`、`memory_monitor.py`、`disk_monitor.py`、`system_monitor.py` 尚未保存為獨立檔案。

- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

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
