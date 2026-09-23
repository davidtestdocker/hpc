# Week 1 Day 4－CPU Utilization（CPU 使用率）

[上一課](<day3-context-switch.md>) · [本週目錄](README.md) · [下一課](<day5-memory.md>)

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

## 補充：2026-09-23 實際執行與解讀

以下是助理在目前 Linux 工作環境新執行的結果，原有教材與舊觀察保留在上方。這次程序清單受執行沙箱限制；整機 CPU、記憶體與裝置統計的可見範圍不一定與程序清單相同。不能把新結果冒充當年的 VM 紀錄。

各指令的時間、參數與結束碼見 [執行紀錄](results/20260923/execution.json)。

### `top` 摘要：加入負載前後

用 `top -b -n 2 -d 1` 取第二次快照，依序觀察沒有本次 yes 負載、加入一個 yes：

[完整輸出](results/20260923/top-baseline.stdout.txt)：

```text
%Cpu(s):  3.1 us,  1.8 sy,  0.0 ni, 94.1 id,  0.0 wa,  0.0 hi,  0.8 si,  0.3 st
```

[完整輸出](results/20260923/top-1-yes.stdout.txt)：

```text
%Cpu(s): 14.7 us, 14.0 sy,  0.0 ni, 69.6 id,  0.0 wa,  0.0 hi,  1.7 si,  0.0 st
```

us 從 3.1% 變成 14.7%，sy 從 1.8% 變成 14.0%，id 從 94.1% 變成 69.6%。表示兩個採樣區間的整體 CPU 時間分布不同；還有其他系統活動，不能將全部差值歸給 yes。us／sy／id 之外還有其他欄位，三項不必加總為 100%。整機 idle 高也不能排除某個單執行緒已用滿一個 CPU。
