<!-- readable-curriculum: 2026-09-22 -->
# Week12 Day1 — CPU 分析

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-Linux-Memory-Performance-Analysis.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

高 CPU 可能代表有效計算，也可能是 busy loop；低 CPU 可能在等 I/O。先對照工作進度與吞吐，再看 runnable threads、核心配置與容器 throttling。

## 在現在的專案中

歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

本課對照：[benchmark/cpu/run_stress_ng.sh](<../../benchmark/cpu/run_stress_ng.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
stress-ng \
  --cpu ${CPU_WORKERS} \
  --timeout ${TIMEOUT}s \
  --metrics-brief
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week12/Day1-Linux-CPU-Performance-Analysis.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 診斷方法繼續適用；舊 perf／strace／CPU 數據不代表主 MPI 的自動 profiling。
> **閱讀順序**：先學本文基礎，再讀[Week12 現行對照與檢核](../learning-guide.md#week12)及[對應現行入口](../performance/performance-report.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week12 Day1 - Linux CPU Performance Analysis

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[performance-report](../performance/performance-report.md)。

---

## 目標

本章節學習 Linux CPU 效能分析的基本工具，了解 CPU 架構、整體 CPU 使用率、每顆 CPU 負載以及各 Process 的 CPU 使用情況。

完成本章後，可以回答：

- 這台主機有多少 CPU？
- CPU 是否真的滿載？
- 哪一顆 CPU 最忙？
- 哪一個 Process 正在消耗 CPU？
- CPU 高使用率的第一步如何分析？

---

# Lab Environment

OS

```bash
Ubuntu 24.04
```

CPU

```text
AMD EPYC 7B12
```

Virtualization

```text
KVM
```

---

# Step1：確認 CPU 架構

## 查看 CPU 數量

```bash
nproc
```

輸出：

```text
4
```

代表 Linux 可使用 **4 個 Logical CPU（vCPU）**。

---

## 查看 CPU 詳細資訊

```bash
lscpu
```

重要資訊：

```text
CPU(s): 4

Core(s) per socket): 2

Thread(s) per core): 2

Socket(s): 1

NUMA node(s): 1

Model name:
AMD EPYC 7B12
```

### CPU 架構

```
1 Socket
│
├── Core0
│      ├── CPU0
│      └── CPU1
│
└── Core1
       ├── CPU2
       └── CPU3
```

因此：

```
2 Core × 2 Thread = 4 vCPU
```

---

## 查看 CPU 型號

```bash
cat /proc/cpuinfo | grep "model name" | head -1
```

輸出：

```text
model name : AMD EPYC 7B12
```

---

# CPU 基本觀念

Linux 顯示的是 **Logical CPU（vCPU）**。

因此：

```
CPU0
CPU1
CPU2
CPU3
```

代表四個可以被 Linux Scheduler 排程的 CPU。

---

# Step2：使用 top 觀察系統

執行：

```bash
top
```

範例：

```text
top - 14:48:18
load average: 0.18, 0.32, 0.27

Tasks: 283 total

%Cpu(s):
3.7 us
2.2 sy
93.3 id

MiB Mem:
15990 total
8903 free
2579 used
4507 buff/cache
```

---

# Load Average

```
0.18
0.32
0.27
```

分別代表：

- 最近 1 分鐘
- 最近 5 分鐘
- 最近 15 分鐘

CPU 平均等待執行的 Process 數量。

> **不是 CPU 使用率。**

---

## 如何判斷是否過高？

本機共有：

```
4 vCPU
```

因此：

```
Load = 4
```

代表 CPU 幾乎已滿載。

若：

```
Load = 8
```

代表：

```
4 個 Process 正在執行

另外約 4 個 Process 正在等待 CPU
```

---

# CPU 欄位

```
us
```

User Space CPU

例如：

- Python
- Go
- Java

---

```
sy
```

Kernel Space CPU

例如：

- read()
- write()
- socket()
- filesystem

---

```
id
```

Idle

CPU 閒置比例。

---

```
wa
```

IO Wait

CPU 正等待 Disk IO。

---

```
soft
```

Software Interrupt。

通常與 Network Driver 有關。

---

# Memory

```
8903 MB free
```

真正可立即使用的記憶體。

```
4507 MB buff/cache
```

Linux Cache。

Linux 會利用空閒 RAM 做 Cache，提高 IO 效率。

---

# Process

CPU 使用率最高：

```
k3s-server
```

其次：

```
containerd
```

代表目前主要 CPU 消耗來自 Kubernetes Control Plane。

---

# Step3：使用 mpstat 觀察每顆 CPU

安裝：

```bash
sudo apt install -y sysstat
```

執行：

```bash
mpstat -P ALL 1 5
```

參數：

```
-P ALL
```

顯示所有 CPU。

```
1
```

每秒收集一次。

```
5
```

收集五次。

---

## Average

```
CPU0 idle 91.55%

CPU1 idle 92.32%

CPU2 idle 93.29%

CPU3 idle 94.11%
```

表示：

四顆 CPU 都非常閒。

目前負載平均。

---

# mpstat 欄位

```
usr
```

User Space。

---

```
sys
```

Kernel Space。

---

```
soft
```

Software Interrupt。

---

```
iowait
```

等待 Disk IO。

---

```
idle
```

CPU 閒置比例。

---

# 為什麼需要 mpstat？

假設：

```
CPU0 100%

CPU1 2%

CPU2 1%

CPU3 1%
```

代表：

只有一顆 CPU 滿載。

若只看 top：

```
CPU 約 25%
```

容易誤判系統不忙。

因此分析 CPU 時，應優先確認是否只有單一 CPU 成為瓶頸。

---

# Step4：使用 pidstat 找出 CPU 使用者

執行：

```bash
pidstat 1 5
```

用途：

查看每個 Process 的 CPU 使用率。

---

## 重要欄位

```
PID
```

Process ID。

---

```
Command
```

Process 名稱。

---

```
%usr
```

User Space CPU。

---

```
%system
```

Kernel Space CPU。

---

```
%CPU
```

總 CPU 使用率。

---

```
CPU
```

目前被 Scheduler 排程到哪一顆 CPU。

---

## 範例分析

```
PID 453

Command:
k3s-server

%CPU
8.76
```

代表：

目前 CPU 使用率最高的 Process 為 Kubernetes Control Plane。

---

```
PID 678

containerd

2.59%
```

代表：

Container Runtime 持續有少量 CPU 消耗。

---

```
MainThread

1.20%
```

代表：

目前自行開發的平台程式 CPU 使用率很低。

---

# CPU 分析流程

```
使用者反映系統變慢
        │
        ▼
top
        │
CPU 是否偏高？
        │
        ▼
mpstat
        │
是哪一顆 CPU 忙？
        │
        ▼
pidstat
        │
是哪個 Process 消耗 CPU？
        │
        ▼
ps / perf / strace
        │
找出真正瓶頸
```

---

# 本日重點

- 了解 CPU 架構（Socket、Core、Thread、vCPU）
- 學會判讀 Load Average
- 學會使用 top 觀察整體 CPU 狀態
- 學會使用 mpstat 分析每顆 CPU 使用率
- 學會使用 pidstat 找出高 CPU Process
- 建立 Linux CPU 效能分析的基本流程

---

# Interview

## Q1：Load Average 是 CPU 使用率嗎？

**不是。**

Load Average 代表等待 CPU 執行的平均 Process 數量，需要搭配 CPU 數量一起判斷是否過高。

---

## Q2：top、mpstat、pidstat 的差異？

- **top**：查看整體系統 CPU、Memory、Process 狀態。
- **mpstat**：查看每顆 CPU（vCPU）的使用率。
- **pidstat**：查看每個 Process 的 CPU 使用率，找出真正消耗 CPU 的程式。
