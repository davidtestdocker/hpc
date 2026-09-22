<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day1 — 程序與 PID

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-cpu-scheduler.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

同一份 Python 程式可以啟動多個程序，各有自己的 PID。API 與 worker 即使用同一 image，也因啟動命令不同而執行不同角色；程序存在不等於它已完成工作。

## 在現在的專案中

本週在自己的 Linux 學習環境做唯讀觀察，不聲稱主叢集當下健康。

本課對照：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
result = subprocess.run(
    ["ps", "-eo", "pid,comm"],
    capture_output=True,
    text=True,
    check=False
)

print(result.stdout)
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week1/day1-linux-process.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
