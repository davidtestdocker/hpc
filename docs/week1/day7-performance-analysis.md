<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day7 — 系統效能分析流程

[上一課](<day6-disk-io.md>) · [本週目錄](README.md) · [下一週](../week2/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

先記錄症狀、負載與時間，再提出假說、選擇量測並改一個變因。CPU、記憶體、磁碟、網路會互相影響；沒有工作量和環境資訊的數字難以比較。

## 在現在的專案中

本週在自己的 Linux 學習環境做唯讀觀察，不聲稱主叢集當下健康。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def health():
    return {
        "status": "healthy"
    }

# 以 ping 檢查 Redis，連線失敗轉成 HTTP 503。
@app.get("/health/redis")
def redis_health():
    try:
        redis_client.ping()

        return {
            "status": "healthy",
            "redis": "connected"
        }

    except ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Redis unavailable"
        )


# 列出 API 支援的 benchmark 名稱。
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week1/day7-performance-analysis.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 7－Performance Analysis（效能分析）

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

規劃中的 `cpu_monitor.py`、`memory_monitor.py`、`disk_monitor.py`、`system_monitor.py` 尚未保存為獨立檔案。

- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

建立 Performance Engineer 的分析思維。

理解效能分析不是猜測，而是透過資料一步一步排除瓶頸，最後找出真正影響系統效能的原因。

---

# 為什麼需要 Performance Analysis？

假設未來平台執行 Benchmark 後得到：

```
TPS = 20
```

這只能代表：

系統效能不好。

但是：

不知道原因。

真正重要的是回答：

- CPU 是否成為瓶頸？
- Memory 是否不足？
- Disk 是否過慢？
- Network 是否有問題？
- GPU 是否已經滿載？

Performance Engineer 的工作就是找出真正原因，而不是猜測。

---

# Performance Analysis 的流程

未來整個平台都會遵循固定分析流程：

```
Benchmark

↓

Process

↓

CPU

↓

Memory

↓

Disk

↓

Network

↓

GPU

↓

Application

↓

Performance Report
```

每一層都負責排除一種可能性。

---

# 第一層：Process

先確認有哪些 Process 正在執行。

例如：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

確認是否有異常 Process。

---

# 第二層：CPU

查看：

- CPU Usage
- User Time
- System Time
- Idle Time

確認：

CPU 是否真的很忙。

如果 CPU Idle 很高，就代表 CPU 並不是瓶頸。

---

# 第三層：Memory

查看：

```bash
free -h
```

確認：

- Available Memory
- 是否還有足夠 RAM

如果 Available 很高，Memory 通常不是瓶頸。

---

# 第四層：Disk

查看：

```bash
iostat
```

重點觀察：

```
%iowait
```

如果 iowait 很高，代表 CPU 花大量時間等待磁碟。

Disk I/O 很可能就是瓶頸。

---

# 第五層：Network

目前尚未學習。

Week 1 結束後會開始加入。

---

# 第六層：GPU

目前尚未學習。

Week 9 開始加入 GPU 與 vLLM。

---

# 第七層：Application

如果：

- CPU 正常
- Memory 正常
- Disk 正常
- Network 正常
- GPU 正常

才開始懷疑：

- Benchmark Worker
- vLLM
- FastAPI
- Application Logic

---

# Week 1 學習成果

本週建立了 Linux Performance Analysis 的基礎觀念：

- Program
- Process
- Scheduler
- Context Switch
- CPU Utilization
- Memory
- Disk I/O

理解 Linux 如何執行程式，以及如何分析 CPU、Memory、Disk 是否成為系統瓶頸。

---

# 與 HPC AI Performance Engineering Platform 的關聯

Week 2 開始將建立 Monitoring Framework：

```
monitoring/

process_monitor.py
cpu_monitor.py
memory_monitor.py
disk_monitor.py
system_monitor.py
```

這些模組的目的不是單純收集資料，而是提供 Performance Analysis 所需的資訊。

未來平台將自動完成：

```
Benchmark

↓

Collect Metrics

↓

Performance Analysis

↓

Optimization Report
```

這也是整個 HPC AI Performance Engineering Platform 的核心能力。

---

# Week 1 重點整理

本週建立了 Performance Engineer 最重要的分析流程：

```
Program
        │
        ▼
Process
        │
        ▼
CPU
        │
        ▼
Memory
        │
        ▼
Disk
        │
        ▼
Performance Analysis
```

之後所有 Monitoring、Benchmark、Analysis、Optimization 都會建立在這個基礎之上。
