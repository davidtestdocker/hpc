# Week 1 Day 3－Context Switch（上下文切換）

[上一課](<day2-cpu-scheduler.md>) · [本週目錄](README.md) · [下一課](<day4-cpu-utilization.md>)

## 今日目標

理解 Context Switch 是什麼，以及它為什麼會影響系統效能。

---

# 什麼是 Context Switch？

當 CPU Core 不足以同時執行所有 Process 時，Linux Scheduler 必須在不同 Process 之間切換。

切換前，需要保存目前 Process 的執行狀態。

切換後，需要恢復下一個 Process 的執行狀態。

這個過程稱為 Context Switch。

---

# 為什麼需要 Context Switch？

目前實驗環境：

- CPU Core：4

建立五個高 CPU 使用率 Process：

```bash
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
```

由於 Process 數量超過 CPU Core 數量，Scheduler 必須不停在 Process 之間切換。

---

# 實驗結果

使用：

```bash
top
```

觀察到：

- 五個 `yes` Process 同時存在
- 每個 Process CPU 使用率約 75%～85%

代表 Scheduler 正在公平分配 CPU 時間，而不是讓某一個 Process 長時間獨占 CPU。

---

# Context Switch 的成本

Context Switch 不會執行任何業務邏輯。

它需要：

- 保存目前 Process 狀態
- 載入下一個 Process 狀態
- 恢復執行

因此會消耗 CPU 時間。

Context Switch 越頻繁，可用於真正運算的 CPU 時間就越少。

---

# 今日重點

- Context Switch 是 Linux Scheduler 在 Process 間切換的過程。
- 當 Process 數量超過 CPU Core 數量時，Context Switch 會增加。
- CPU 使用率高，不代表 CPU 都在做有效工作。
- Context Switch 過多會降低整體效能。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

都是 Linux Process。

如果 Compute Node 的 CPU 資源不足，Scheduler 會增加 Context Switch。

Context Switch 增加後，可能造成：

- TPS 下降
- TTFT 增加
- Latency 增加

因此，Performance Engineer 在分析 CPU Bottleneck 時，不能只看 CPU 使用率，還必須考慮 Context Switch 是否過於頻繁。

## 補充：2026-09-23 實際執行與解讀

以下是助理在目前 Linux 工作環境新執行的結果，原有教材與舊觀察保留在上方。這次程序清單受執行沙箱限制；整機 CPU、記憶體與裝置統計的可見範圍不一定與程序清單相同。不能把新結果冒充當年的 VM 紀錄。

各指令的時間、參數與結束碼見 [執行紀錄](results/20260923/execution.json)。

### 五個 `yes` 的實際 CPU 使用率

本次建立五個 stdout 導向 `/dev/null` 的 yes，再以 `top -b -n 2 -d 1` 保存第二次快照：

```text
    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
     18 root      20   0    3208   1884   1764 R  92.0   0.0   0:01.08 yes
     16 root      20   0    3208   1880   1760 R  84.0   0.0   0:01.00 yes
     19 root      20   0    3208   1876   1760 R  67.0   0.0   0:00.74 yes
     17 root      20   0    3208   1876   1760 R  66.0   0.0   0:00.75 yes
     15 root      20   0    3208   1880   1760 R  65.0   0.0   0:00.81 yes
```

[完整輸出](results/20260923/top-5-yes.stdout.txt)。

這次五個程序為 92%、84%、67%、66%、65%，沒有把舊文的 75%～85% 改寫成這次結果。短時間採樣不必平均相等；這些百分比也不是切換次數。

### 補測切換計數：`vmstat 1 2`

```text
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 6  0      0 12100964  68856 3106812    0    0   219   260  624  640  4  2 94  0  0
 6  0      0 12100964  68856 3107008    0    0     0    20 4625 2822 50 50  0  0  0
```

[完整輸出](results/20260923/vmstat-5-yes.stdout.txt)。

`cs` 是每秒上下文切換數。第一列是開機以來的平均，第二列是本次一秒間隔，顯示 2822。它是系統範圍統計，包含其他工作；這次沒有無負載 cs 對照，不能把 2822 全歸因於五個 yes，也不能換算成效能損失。即使工作數量少於 CPU，也可能因等待、喚醒而切換。測量後五個 yes 都已終止。
