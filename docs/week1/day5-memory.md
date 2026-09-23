# Week 1 Day 5－Memory（記憶體）

[上一課](<day4-cpu-utilization.md>) · [本週目錄](README.md) · [下一課](<day6-disk-io.md>)

## 今日目標

理解 Process 與 Memory 的關係，以及如何找出哪一個 Process 正在使用最多記憶體。

---

# Program、Process 與 Memory

程式執行流程：

```

Program（Disk）
        │
        ▼
Process
        │
        ▼
Memory（RAM）
        │
        ▼
CPU

```

CPU 不會直接執行磁碟上的程式，而是先將程式載入記憶體，再開始執行。

每個 Process 都有自己的記憶體空間。

---

# free -h

使用：

```bash
free -h
```

觀察：

```
Mem:          15Gi
Used:       582Mi
Available:   14Gi
```

重點：

- total：實體 RAM 總容量
- used：目前已使用的記憶體
- available：目前仍可提供新程式使用的記憶體

Performance Engineer 主要觀察的是 **available**。

---

# 找出誰使用最多記憶體

使用：

```bash
ps -eo pid,comm,rss --sort=-rss | head
```

欄位：

- PID：Process ID
- COMMAND：Process 名稱
- RSS：目前實際占用的 RAM（KB）

本次觀察：

```
otelopscol
codex
MainThread
```

代表目前這些 Process 使用最多記憶體。

---

# 今日重點

- CPU 執行的是 Memory 中的資料，而不是磁碟上的程式。
- 每個 Process 都有自己的記憶體空間。
- `available` 比 `free` 更能反映目前是否還有足夠記憶體。
- Performance Engineer 需要知道是哪一個 Process 使用記憶體，而不是只看 Memory 百分比。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

都會占用記憶體。

分析 Memory Bottleneck 時，需要確認：

- 哪一個 Process 使用最多 RAM？
- 是否有 Process 持續增加記憶體（Memory Leak）？
- 是否還有足夠 Available Memory 可供新的 Benchmark 或模型使用？

## 補充：2026-09-23 實際執行與解讀

以下是助理在目前 Linux 工作環境新執行的結果，原有教材與舊觀察保留在上方。這次程序清單受執行沙箱限制；整機 CPU、記憶體與裝置統計的可見範圍不一定與程序清單相同。不能把新結果冒充當年的 VM 紀錄。

各指令的時間、參數與結束碼見 [執行紀錄](results/20260923/execution.json)。

### `free -h`

```text
               total        used        free      shared  buff/cache   available
Mem:            15Gi       1.0Gi        11Gi       1.0Mi       3.0Gi        14Gi
Swap:             0B          0B          0B
```

[完整輸出](results/20260923/free-h.stdout.txt)。

本次顯示總量 15Gi、used 1.0Gi、available 14Gi。available 是估計可供新工作使用的量，包含部分可回收空間；這份整機統計不能當作每個程序的配置額度。

### `ps -eo pid,comm,rss --sort=-rss | head`

```text
    PID COMMAND           RSS
      1 codex-linux-san 18572
      2 python3         11300
     23 bash             3308
     24 ps               3128
     25 head             1892
```

[完整輸出](results/20260923/ps-rss-head.stdout.txt)。

這次可見程序中，PID 1 的 RSS 為 18572 KiB，PID 2 為 11300 KiB。RSS 包含共享頁，不等於程序獨占的 RAM；多程序直接加總可能重複計算。一次快照不能判斷記憶體是否持續洩漏。
