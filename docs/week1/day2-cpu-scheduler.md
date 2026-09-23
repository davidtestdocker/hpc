# Week 1 Day 2－CPU Scheduler（CPU 排程器）

[上一課](<day1-linux-process.md>) · [本週目錄](README.md) · [下一課](<day3-context-switch.md>)

## 今日目標

理解 Linux Scheduler 如何將 Process 分配到 CPU Core 執行，以及 CPU Core 與 Process 的關係。

---

# 為什麼需要 Scheduler？

CPU Core 的數量有限，但系統中可能同時存在數百個 Process。

Linux Scheduler 的工作就是：

- 決定哪個 Process 先執行
- 決定 Process 執行多久
- 決定下一個要執行哪個 Process

CPU Core 不會自己挑選 Process，而是由 Scheduler 負責分配。

---

# CPU Core 與 Process

目前實驗環境：

- GCP Ubuntu VM
- CPU Core：4

如果同時只有四個 Process：

```
Core0 → Process A
Core1 → Process B
Core2 → Process C
Core3 → Process D
```

每個 Process 都可以直接使用一個 CPU Core。

---

# 實驗一：查看 CPU Core

使用指令：

```bash
nproc
```

輸出：

```
4
```

代表目前 VM 有四個 CPU Core。

---

# 實驗二：建立高 CPU 使用率 Process

執行：

```bash
yes > /dev/null
```

再使用：

```bash
top
```

觀察到：

- 新增一個 Running Process
- `yes` 的 CPU 使用率接近 100%

代表一個 Process 可以吃滿一個 CPU Core。

---

# 實驗三：同時執行兩個 yes

再次執行：

```bash
yes > /dev/null
```

再次觀察 `top`：

可以看到兩個 `yes` Process。

兩個 Process 都接近 100% CPU。

代表 Linux Scheduler 將兩個 Process 分配到不同 CPU Core 執行。

---

# 今日重點

Scheduler 負責將 Process 分配到 CPU Core。

CPU Core 不會自己選擇要執行哪個 Process。

當 CPU Core 足夠時，每個高負載 Process 可以獨占一個 Core。

當 Process 數量超過 CPU Core 數量時，Scheduler 就必須在 Process 之間不停切換。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

本質上都是 Linux Process。

Performance Engineer 必須了解 Scheduler 如何分配 CPU，才能分析：

- CPU 是否成為瓶頸
- Benchmark Worker 是否取得足夠 CPU 資源
- TPS 為何下降
- 是否需要調整 CPU 資源配置

## 補充：2026-09-23 實際執行與解讀

以下是助理在目前 Linux 工作環境新執行的結果，原有教材與舊觀察保留在上方。這次程序清單受執行沙箱限制；整機 CPU、記憶體與裝置統計的可見範圍不一定與程序清單相同。不能把新結果冒充當年的 VM 紀錄。

各指令的時間、參數與結束碼見 [執行紀錄](results/20260923/execution.json)。

### `nproc`

```text
4
```

本次可用處理單位為 4；這不等於已確認有四個實體核心。[完整輸出](results/20260923/nproc.stdout.txt)。

### `yes > /dev/null` 與 `top`

為保存非互動輸出，本次使用 `top -b -n 2 -d 1`：取兩次快照、間隔一秒，下面取第二次的欄位標題與 yes 列。`yes` 的輸出導向 `/dev/null`，所以本來就不會留下文字；要觀察的是 CPU 使用率。

**1 個 yes：**

```text
    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
     10 root      20   0    3208   1876   1760 R 100.0   0.0   0:01.15 yes
```

[完整輸出](results/20260923/top-1-yes.stdout.txt)。

**2 個 yes：**

```text
    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
     12 root      20   0    3208   1876   1760 R 100.0   0.0   0:01.15 yes
     13 root      20   0    3208   1884   1764 R 100.0   0.0   0:01.15 yes
```

[完整輸出](results/20260923/top-2-yes.stdout.txt)。

本次一個 yes 顯示 100.0%，兩個 yes 各 100.0%，對應每個單執行緒工作約取得一份 CPU 時間。這不證明核心固定綁定。Linux 排程的是執行緒，多執行緒程序不受「一個程序只能用一顆核心」的限制。各組觀察完成後，本次建立的 yes 都已終止並回收。
