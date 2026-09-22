<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](<../../../learning-guide.md#week1>)及[對應現行入口](<../../../runbooks/ai-hpc-job-troubleshooting.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 5－Memory（記憶體）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day2-Linux-Memory-Performance-Analysis](<../../../week12/Day2-Linux-Memory-Performance-Analysis.md>)。

---

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
