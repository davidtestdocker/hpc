<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day1 — 程序與 PID

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-cpu-scheduler.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史教材輸出（跨頁接回）。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現行程式只呼叫 ps -eo pid,comm、擷取字串並印出；沒有 PPID、CPU、RSS、狀態、JSON 或長駐採樣。check=False 且未檢查 returncode，不能僅依 Python 結束就判定 ps 成功。 benchmark.py 沒有保存為檔案，原文 python benchmark.py 只能當示意。Linux 實際排程執行緒；四個實體核心不必然等於四個邏輯 CPU，也不能一概推為最多四個程序。原文約 150 個程序只是 Week1 的文字觀察，與這份兩程序輸出是不同環境。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)、[docker/Dockerfile](<../../docker/Dockerfile>)、[compose.yaml](<../../compose.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<../week3/day6-containerize-monitoring.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
PID COMMAND
1   python3
7   ps
```

這段輸出是 Week3 Day6 保存的 hpc-monitor:v5 容器案例：PID 1 是 Python 主程序，PID 7 是它呼叫的 ps。它說明容器內程序列舉，不是 Week1 Ubuntu VM 的完整程序清單。現在直接放在本頁，不需重新執行。

**仍缺的證據／不能證明的事：** 舊文未記錄此執行的精確日期、映像 digest 或独立原始 log；只能稱為舊教材保存的容器輸出，不能稱本次重跑或最新映像驗收。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 1－Linux Process（程序）

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

文中的 `benchmark.py` 是示意檔名，儲存庫未保存該檔案；下方監控程式是程序查詢的現有對照。

- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

理解 Linux 如何執行程式，以及 CPU 如何透過 Scheduler（排程器）分配 Process（程序）到 CPU Core 執行。

今天不是學 Linux 指令，而是建立 Linux Performance Analysis 的核心觀念。

---

# 為什麼要學 Process？

在 HPC AI Performance Engineering Platform 中，所有服務本質上都是 Linux Process，例如：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM
- Python Monitoring Script

當未來需要分析效能瓶頸時，第一步就是確認有哪些 Process 正在執行，以及它們之間的關係。

---

# Program 與 Process

## Program（程式）

Program 是儲存在磁碟上的程式檔案。

例如：

- python
- nginx
- benchmark.py

Program 本身不會執行。

只有被 Linux 載入記憶體後，才會建立 Process。

---

## Process（程序）

Process 是正在執行中的程式。

每個 Process 都會有自己的：

- PID（Process ID）
- PPID（Parent Process ID）
- 記憶體空間
- 執行狀態

例如：

```bash
python benchmark.py
```

Linux 會建立一個新的 Process。

---

# Linux Scheduler

CPU 不會同時執行所有 Process。

Scheduler（排程器）會決定：

- 哪個 Process 可以先執行
- 執行多久
- 下一個換誰執行

例如：

Process A

↓

Process B

↓

Process C

↓

Process A

↓

Process D

CPU 就是不斷在不同 Process 之間切換。

---

# CPU Core

假設：

4 Core CPU

同一時間最多可以同時執行四個工作。

例如：

Core0 → Process A

Core1 → Process B

Core2 → Process C

Core3 → Process D

如果系統有 100 個 Process，就只能透過 Scheduler 不斷切換。

---

# Kernel Thread

使用：

```bash
ps -ef
```

可以看到大量名稱像是：

- kthreadd
- kworker
- ksoftirqd
- migration

它們不是使用者啟動的程式。

而是 Linux Kernel 自己建立的背景工作。

例如：

- 處理硬體事件
- 管理記憶體
- 執行背景工作
- 處理系統資源

因此稱為 Kernel Thread。

---

# User Process

User Process 是使用者啟動的程式。

例如：

- bash
- python
- docker
- prometheus

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

全部都屬於 User Process。

---

# PID 與 PPID

PID（Process ID）

Linux 會替每個 Process 分配一個唯一編號。

例如：

```
PID 323404
bash
```

---

PPID（Parent Process ID）

每個 Process 都有自己的父程序。

例如：

```
sshd
    │
    ▼
bash
    │
    ▼
python benchmark.py
```

bash 啟動了 python，因此：

- bash 是 Parent Process
- python 是 Child Process

Linux 會記錄這個父子關係，方便管理 Process。

---

# 今天使用的指令

查看目前所有 Process：

```bash
ps -ef
```

---

# 今天實際觀察

在 GCP Ubuntu VM 中：

- 約有 150 個 Process
- 觀察到大量 Kernel Thread
- 看到 systemd、sshd 等系統服務
- 看到 bash、VS Code Server 等 User Process

可以將 Process 分成三大類：

```
Linux

├── Kernel Thread
│      ├── kthreadd
│      ├── kworker
│      ├── ksoftirqd
│
├── System Service
│      ├── systemd
│      ├── sshd
│      ├── chronyd
│
└── User Process
       ├── bash
       ├── python
       ├── vscode-server
```

---

# 今日重點整理

今天建立了以下觀念：

- Program 是磁碟上的程式。
- Process 是正在執行中的程式。
- CPU Core 數量決定同時可執行的工作數。
- Scheduler 負責分配 CPU 執行 Process。
- Linux Process 可分為 Kernel Thread 與 User Process。
- PID 用來識別 Process。
- PPID 用來記錄 Parent Process。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的每一個服務，本質上都是 Linux Process。

例如：

- FastAPI
- Prometheus
- Grafana
- Benchmark Worker
- vLLM

效能分析的第一步，就是理解：

- 有哪些 Process？
- 是誰建立它？
- 它目前是否正在執行？
- 它是否成為系統瓶頸？

理解 Process，是後續 CPU Scheduling、Context Switch、System Monitoring 與 Performance Analysis 的基礎。
