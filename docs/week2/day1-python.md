<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day1 — Python 變數與資料型別

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-function.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

job_id 是字串，retry_count 是整數，job 是 dict。型別決定能做的操作，例如字串加字串是串接；從環境變數讀到的數字要轉型後才能當秒數使用。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    job = {
    "job_id": job_id,
    "benchmark": request.benchmark,
    "simulate_failure": request.simulate_failure,
    "status": "accepted",
    "result": None,
    "retry_count": 0
    }

    session = SessionLocal()

    db_job = Job(
        job_id=job_id,
        benchmark=job["benchmark"],
        status=job["status"],
        retry_count=job["retry_count"],
        created_at=datetime.now(timezone.utc)
    )

    # add 將 ORM 物件加入本次 Session，等待 flush／commit 寫入。
    try:
        session.add(db_job)
        session.commit()
    finally:
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week2/day1-python.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 1－Python 與 Monitoring Framework

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

目前保存的是 hello 與 process monitor 範例；目錄樹中的其他 monitor 模組尚未保存。

- [examples/hello.py](../../examples/hello.py)：Python 入門範例
- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

建立 Monitoring Framework 的第一支 Python 程式，理解 Python 在整個平台中的角色。

---

# 為什麼使用 Python？

Monitoring Framework 需要自動完成：

```
收集 CPU
        │
        ▼
收集 Memory
        │
        ▼
收集 Disk
        │
        ▼
整理成 JSON
        │
        ▼
提供 Analysis Engine 使用
```

Python 適合：

- 系統監控
- 自動化
- 資料處理
- JSON 輸出

因此本專案選擇 Python 作為 Monitoring Framework 的開發語言。

---

# Python Interpreter

執行：

```bash
python3 hello.py
```

真正執行的是：

```
python3
```

`hello.py` 是提供給 Python Interpreter 讀取的程式碼。

執行流程：

```
Linux
        │
        ▼
python3
        │
        ▼
建立 Process
        │
        ▼
讀取 hello.py
        │
        ▼
逐行執行
```

因此 Linux 建立的 Process 是 `python3`。

---

# Python 是由上往下執行

程式：

```python
print("Step 1")
print("Step 2")
print("Step 3")
```

執行結果：

```
Step 1
Step 2
Step 3
```

Python Interpreter 會依照程式由上往下逐行執行。

---

# Variable（變數）

程式：

```python
cpu_usage = 15
```

代表：

建立一個名為 `cpu_usage` 的變數，並將數值 `15` 儲存在其中。

變數可以理解為：

- 一塊有名字的記憶體
- 用來保存程式執行期間的資料

---

# print()

程式：

```python
cpu_usage = 15

print(cpu_usage)
```

輸出：

```
15
```

`print(cpu_usage)` 會輸出變數目前儲存的值。

如果寫成：

```python
print("cpu_usage")
```

則輸出的是字串 `cpu_usage`，而不是變數的內容。

---

# 今日重點

- Python 是 Monitoring Framework 的開發工具，而不是學習目的。
- Linux 執行的是 `python3`，不是 `.py` 檔案本身。
- Python Interpreter 會由上往下逐行執行程式。
- 變數用來保存程式執行期間的資料。
- `print()` 可以輸出變數中的值。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來 Monitoring Framework 將建立：

```
monitoring/
├── process_monitor.py
├── cpu_monitor.py
├── memory_monitor.py
├── disk_monitor.py
└── system_monitor.py
```

每個 Monitor 都會使用變數保存收集到的資訊，例如：

```python
cpu_usage = 23.5
memory_usage = 41.8
disk_usage = 12.1
```

最後整理成 JSON，提供後續的 Analysis Engine 與 Benchmark Report 使用。
