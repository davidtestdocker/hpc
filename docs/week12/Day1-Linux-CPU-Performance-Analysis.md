# Week12 Day1 - Linux CPU Performance Analysis

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
