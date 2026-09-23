# Week 1 Day 1－Linux Process（程序）

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-cpu-scheduler.md>)

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

## 補充：2026-09-23 實際執行與解讀

以下是助理在目前 Linux 工作環境新執行的結果，原有教材與舊觀察保留在上方。這次程序清單受執行沙箱限制；整機 CPU、記憶體與裝置統計的可見範圍不一定與程序清單相同。不能把新結果冒充當年的 VM 紀錄。

各指令的時間、參數與結束碼見 [執行紀錄](results/20260923/execution.json)。

### `ps -ef`：程序與父子關係

以下保留欄位標題與本次 Python、ps 兩列；較長的沙箱啟動列見 [完整輸出](results/20260923/ps-ef.stdout.txt)。

```text
UID          PID    PPID  C STIME TTY          TIME CMD
root           2       1  0 07:33 ?        00:00:00 python3 /tmp/collect_week1_outputs.py
root           7       2  0 07:33 ?        00:00:00 ps -ef
```

PID 2 的 Python 正在執行採集腳本；PID 7 的 ps，其 PPID 是 2，表示它由這個 Python 程序啟動。這就是本課父子程序關係的實際例子。

### 舊文的 `python benchmark.py`

本次也嘗試原文命令，結束碼為 127，stderr 如下：

```text
bash: line 1: python: command not found
```

目前環境沒有 `python` 這個命令，且儲存庫也沒有 `benchmark.py`。因此原文這一行只能當作啟動程式的示意，沒有可補造的 benchmark 成功結果。[錯誤原文](results/20260923/benchmark-example.stderr.txt)。
