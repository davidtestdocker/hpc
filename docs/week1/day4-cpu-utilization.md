<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day4 — CPU utilization

[上一課](<day3-context-switch.md>) · [本週目錄](README.md) · [下一課](<day5-memory.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史教材數值摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

us／sy／id 不是 top 的所有欄位，三項不一定加總 100%。整機彙總百分比與單一程序百分比不能直接混用；yes 的 system time 比例取決於執行路徑，不可當成所有計算負載的固定比例。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<day4-cpu-utilization.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
us = 8.3%
sy = 17.9%
id = 73.4%
```

原文空閒階段是 us=1.2%、sy=0.8%、id=97.8%；啟動一個 yes 後出現上列數值，表示该次 CPU 時間分布改變。它不是 process_monitor.py 的輸出。

**仍缺的證據／不能證明的事：** 缺完整 top 行、取樣時間、各 CPU 資料與精確日期；不能從一次數值推論目前 worker 的 CPU 壓力。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 4－CPU Utilization（CPU 使用率）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day1-Linux-CPU-Performance-Analysis](../week12/Day1-Linux-CPU-Performance-Analysis.md)。

---

## 今日目標

理解 CPU 使用率的真正意義，以及 User、Kernel、Idle 三種 CPU 時間的差異。

---

# CPU 使用率不是一個數字

CPU 使用率代表 CPU 在不同工作上的時間分布。

主要可以分為：

- us（User）
- sy（System）
- id（Idle）

今天只學這三個欄位。

---

# us（User）

代表 CPU 花多少時間執行 User Process。

例如：

- Python
- FastAPI
- vLLM
- Benchmark Worker
- Prometheus

---

# sy（System）

代表 CPU 花多少時間執行 Linux Kernel。

例如：

- Scheduler
- System Call
- Memory Management
- File System
- Network

---

# id（Idle）

代表 CPU 閒置時間。

如果 id 很高，代表 CPU 還有很多可用資源。

---

# 實驗一：沒有高 CPU Process

使用：

```bash
top
```

觀察：

```
us = 1.2%
sy = 0.8%
id = 97.8%
```

代表：

CPU 幾乎處於閒置狀態。

---

# 實驗二：建立一個高 CPU Process

執行：

```bash
yes > /dev/null &
```

再次觀察：

```
us = 8.3%
sy = 17.9%
id = 73.4%
```

可以看到：

CPU 開始花時間執行 User Process 與 Linux Kernel。

---

# 今日重點

CPU 使用率不是單一數值。

Performance Engineer 更關心：

- User Time
- System Time
- Idle Time

而不是只看 CPU 百分比。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來分析：

- Benchmark Worker
- vLLM
- FastAPI

時，不只需要知道 CPU 是否很忙，更需要判斷：

- CPU 是否真的在執行應用程式？
- 是否大量時間花在 Linux Kernel？
- 是否還有 CPU 可用資源？

CPU Utilization 是 Performance Analysis 最重要的基礎指標之一。
