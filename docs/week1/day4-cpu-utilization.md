# Week 1 Day 4－CPU Utilization（CPU 使用率）

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
