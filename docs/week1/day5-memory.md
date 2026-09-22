<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day5 — Memory

[上一課](<day4-cpu-utilization.md>) · [本週目錄](README.md) · [下一課](<day6-disk-io.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

RSS 是實際駐留頁面的度量，VMS 是虛擬位址空間，兩者不等於同一件事。free 很低可能因 page cache；判断壓力要同看 available、swap 和程序需求。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week1/day5-memory.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 5－Memory（記憶體）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day2-Linux-Memory-Performance-Analysis](../week12/Day2-Linux-Memory-Performance-Analysis.md)。

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
