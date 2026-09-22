<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day4 — CPU utilization

[上一課](<day3-context-switch.md>) · [本週目錄](README.md) · [下一課](<day5-memory.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

程序 CPU 使用率必須交代採樣期間及多核心計算方式。節點很忙可能來自其他工作；低 GPU 使用率也可能是 CPU 前處理供給不足，不能只依一張使用率圖定位。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week1/day4-cpu-utilization.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 4－CPU Utilization（CPU 使用率）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day1-Linux-CPU-Performance-Analysis](../week12/Day1-Linux-CPU-Performance-Analysis.md)。

---

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
