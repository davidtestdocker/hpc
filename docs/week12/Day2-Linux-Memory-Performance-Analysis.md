# Week12 Day2 - Linux Memory Performance Analysis

## 目標

本章節學習 Linux Memory 的運作方式，了解 Memory、Page Cache、Buffer、Swap、OOM 的概念，建立 Linux 記憶體效能分析能力。

完成本章後，可以回答：

- Linux Memory 為什麼總是快滿？
- `used`、`free`、`available` 有什麼差異？
- Page Cache 是什麼？
- Buffer 是什麼？
- Linux 如何回收記憶體？
- OOM 是如何發生的？
- Kubernetes 的 OOMKilled 與 Linux OOM 有什麼關係？

---

# Lab Environment

OS

```bash
Ubuntu 24.04
```

Memory

```text
16GB RAM
```

---

# Step1：使用 free 查看記憶體

## Human Readable

```bash
free -h
```

輸出：

```text
               total        used        free      shared  buff/cache   available
Mem:            15Gi       2.5Gi       8.0Gi        74Mi       5.1Gi        12Gi
Swap:             0B          0B          0B
```

---

## MB

```bash
free -m
```

輸出：

```text
               total        used        free      shared  buff/cache   available
Mem:           15990        2559        8209          74        5221       13032
Swap:              0           0           0
```

---

# free 各欄位說明

## total

系統可使用的總記憶體。

```
15Gi
```

約為：

```
16GB RAM
```

---

## used

目前程式真正使用中的記憶體。

```
2.5Gi
```

注意：

Linux 並不會把 Cache 算在此欄位。

---

## free

完全沒有被使用的記憶體。

```
8Gi
```

---

## buff/cache

Linux 使用空閒 RAM 建立 Cache。

```
5.1Gi
```

包含：

- Page Cache
- Buffer Cache
- Metadata Cache

Linux 會利用這些 Cache 提高 IO 效能。

---

## shared

Shared Memory。

例如：

- /dev/shm
- IPC
- 多 Process 共用記憶體

通常不需要特別關注。

---

## available

最重要的欄位。

```
12Gi
```

代表：

目前可以立即提供給新程式使用的記憶體。

Linux 必要時可以快速回收 Cache，因此：

```
available

>

free
```

---

# Memory 配置

目前系統：

```
16GB RAM
│
├── Program
│      2.5GB
│
├── Page Cache
│      5.1GB
│
└── Free
       8GB
```

因此：

系統目前沒有任何 Memory 壓力。

---

# Linux Memory 觀念

Linux 的理念：

> **空著的 RAM 是浪費。**

因此：

空閒 RAM 不會一直保持 Free。

Linux 會自動建立：

- File Cache
- Metadata Cache
- Buffer Cache

提高整體 IO 效能。

---

# Step2：使用 vmstat

執行：

```bash
vmstat 1 5
```

輸出：

```text
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
```

---

# Procs

## r

Runnable Process。

等待 CPU 執行中的 Process。

目前：

```
r = 3
```

系統共有：

```
4 vCPU
```

表示 CPU 並沒有不足。

若：

```
r >> CPU 數量
```

通常表示 CPU 已成為瓶頸。

---

## b

Blocked Process。

等待 IO 的 Process。

目前：

```
b = 0
```

代表沒有 Process 因等待 Disk IO 而阻塞。

---

# Memory

## free

真正空閒 RAM。

---

## buff

Buffer Cache。

主要保存 Block Device Metadata。

---

## cache

Page Cache。

主要保存檔案內容。

---

# Swap

## swpd

目前使用中的 Swap。

```
0
```

代表：

沒有使用 Swap。

---

## si

Swap In。

從 Swap 搬回 RAM。

---

## so

Swap Out。

從 RAM 搬到 Swap。

---

目前：

```
si = 0

so = 0
```

表示沒有任何 Swap 行為。

---

# IO

## bi

Blocks In。

磁碟讀取。

---

## bo

Blocks Out。

磁碟寫入。

目前皆非常低。

表示沒有大量磁碟 IO。

---

# System

## in

Interrupt。

每秒硬體中斷數。

來源例如：

- Network
- Disk
- Timer

---

## cs

Context Switch。

CPU 每秒切換 Process 次數。

若異常偏高：

可能代表：

- Thread 過多
- Process 過多
- Scheduler 負擔增加

---

# CPU

```
us
```

User Space。

---

```
sy
```

Kernel。

---

```
id
```

Idle。

---

```
wa
```

IO Wait。

目前：

```
wa = 0
```

表示 CPU 並沒有等待 Disk。

---

# Page Cache

Linux 讀取檔案時：

```
Disk
 │
 ▼
Kernel
 │
 ▼
Page Cache
 │
 ▼
Application
```

第一次：

需要讀取 SSD。

第二次：

直接從 RAM 回傳。

因此速度大幅提升。

Page Cache 快取的是：

- log
- image
- binary
- yaml
- sqlite
- json

等檔案內容。

---

# Buffer

Buffer 主要保存：

- inode
- superblock
- block metadata

現代 Linux 大多將：

```
Buffer + Cache
```

合併顯示為：

```
buff/cache
```

通常不需要刻意區分。

---

# Linux Memory 回收流程

當程式需要更多 Memory 時：

```
New Program
      │
      ▼
Free RAM
      │
      ▼
不足？
      │
      ▼
回收 Page Cache
      │
      ▼
仍不足？
      │
      ▼
使用 Swap（若有）
      │
      ▼
仍不足？
      │
      ▼
OOM Killer
```

因此：

Linux 並不會因為 Cache 很大就立刻發生 OOM。

---

# OOM（Out Of Memory）

當：

- Free Memory 不足
- Cache 已全部回收
- Swap（若存在）也不足

Linux 最後會啟動：

```
OOM Killer
```

直接終止某個 Process。

例如：

```
Killed
```

表示：

程式不是自己退出。

而是 Linux 強制結束。

---

# Kubernetes OOMKilled

若 Deployment：

```yaml
resources:
  limits:
    memory: 512Mi
```

Container 使用：

```
700Mi
```

即使整台 VM 還有很多 RAM，

Container 仍可能因超過 Memory Limit 而被終止。

Pod 狀態：

```
OOMKilled
```

因此：

Linux OOM 與 Kubernetes OOMKilled 並不完全相同。

---

# free 與 vmstat 的差異

| 指令 | 用途 |
|------|------|
| `free` | 查看目前記憶體配置 |
| `vmstat` | 持續觀察 Memory、Swap、IO、CPU、Process 狀態 |

---

# Memory 分析流程

```
Memory 使用率高
        │
        ▼
free
        │
available 是否充足？
        │
        ▼
vmstat
        │
Swap 是否開始使用？
si / so 是否增加？
        │
        ▼
Cache 是否可回收？
        │
        ▼
是否發生 OOM？
        │
        ▼
Linux OOM
或
Kubernetes OOMKilled
```

---

# 本日重點

- 學會使用 `free`
- 學會使用 `vmstat`
- 理解 `available` 比 `free` 更重要
- 理解 Linux 會利用 RAM 建立 Page Cache
- 理解 Buffer 與 Cache 的差異
- 理解 Linux 記憶體回收流程
- 理解 Swap 的用途
- 理解 Linux OOM 與 Kubernetes OOMKilled 的差異

---

# Interview

## Q1：Linux 的記憶體快滿了，是否代表記憶體不足？

**不一定。**

Linux 會主動利用空閒 RAM 建立 Page Cache，因此應優先查看 `available` 是否仍充足，而不是只看 `used`。

---

## Q2：`free` 與 `vmstat` 有什麼差異？

- **free**：查看目前 Memory 配置（total、used、free、available）。
- **vmstat**：持續監控 Process、Memory、Swap、IO、CPU，可用於觀察系統是否開始出現記憶體或 IO 壓力。
