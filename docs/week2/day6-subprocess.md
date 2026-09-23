<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day6 — subprocess

[上一課](<day5-dictionary.md>) · [本週目錄](README.md) · [下一課](<day7-stdout.md>) · [全程導讀](../learning-guide.md)

## process_monitor.py 從哪裡來？

這是儲存庫已存在的 Python 教學小程式，不是 Linux 內建工具。Git 最早在 `d487524`（2026-07-02，`Initial commit`）加入 `monitoring/process_monitor.py`，當時就有 `subprocess.run`、擷取 stdout 和 `print`。`a35ce50`（2026-07-24）補上 `check=False`；`67b0725`（2026-09-21）加入註解。Git 紀錄只能確認它何時進入版本控制，不能推定實際撰寫日期。

課程中的位置是：Week1 先用 Linux 的 `ps` 看程序，本課再把這個指令寫進 Python，Day7 解釋如何接收輸出。這個檔案的目的，就是示範「Python 呼叫外部指令」。

### 檔案內容與執行方式

檔案位於儲存庫根目錄下的 [monitoring/process_monitor.py](../../monitoring/process_monitor.py)。現有可執行程式碼如下；檔案已存在，不需要另建一份：

```python
import subprocess

result = subprocess.run(
    ["ps", "-eo", "pid,comm"],
    capture_output=True,
    text=True,
    check=False
)

print(result.stdout)
```

從儲存庫根目錄執行：

```bash
python3 monitoring/process_monitor.py
```

Python 啟動 `ps -eo pid,comm`，等它結束後把文字放進 `result.stdout`，再印到終端機。程式只查詢一次。

### 實際執行結果（2026-09-23）

以下是在目前助理的 Linux 工作環境執行上述檔案後保存的完整 stdout；不是舊 GCP VM，也不是 Week3 的 Docker 容器：

```text
    PID COMMAND
      1 codex-linux-san
      2 bash
      7 python3
      8 python3
      9 ps
```

第一列是欄位名稱。`PID` 是程序編號，`COMMAND` 是程序名稱；例如最後一列表示查詢當下 PID 9 的程序是 `ps`。Python 程式呼叫的 `ps` 本身也是程序，所以會出現在清單裡。不同環境、不同時間的 PID 和程序數量會變。

可直接看 [完整 stdout 檔](results/process-monitor-20260923.stdout.txt)、[stderr 檔](results/process-monitor-20260923.stderr.txt) 和 [執行紀錄](results/process-monitor-20260923.json)。本次 Python 結束碼為 0、stderr 為空，並確實產生上面的程序表；程式本身沒有檢查子程序的 returncode。

這份結果只展示程序編號與名稱，沒有 CPU、記憶體、PPID 或持續採樣。下方舊實作使用未擷取 stdout 的簡化版本；上面才是目前檔案的內容與本次輸出。

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史教材輸出（跨頁接回）。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

Week2 的舊程式讓 child stdout 直接繼承終端機；現行檔已使用 capture_output=True、text=True，再 print(result.stdout)。兩者輸出形狀可相近，但捕捉方式不同，不能稱程式完全相同。現行程式只呼叫 ps -eo pid,comm、擷取字串並印出；沒有 PPID、CPU、RSS、狀態、JSON 或長駐採樣。check=False 且未檢查 returncode，不能僅依 Python 結束就判定 ps 成功。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<../week3/day6-containerize-monitoring.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
PID COMMAND
1   python3
7   ps
```

Week2 Day6 本頁只有「可以看到相同結果」的文字，沒有實際 PID 清單。已接回 Week3 Day6 保存的容器輸出；這是另一課的歷史案例，並非證明 Week2 當天跑過相同 PID。

**仍缺的證據／不能證明的事：** 舊文未記錄此執行的精確日期、映像 digest 或独立原始 log；只能稱為舊教材保存的容器輸出，不能稱本次重跑或最新映像驗收。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 6－subprocess 執行 Linux 指令

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

理解 Python 如何透過 `subprocess` 執行 Linux 指令，開始將 Python 與 Linux 系統資訊連接起來。

---

# 為什麼需要 subprocess？

Monitoring Framework 不能依賴人工輸入指令。

例如：

```bash
ps -eo pid,comm
```

這個指令可以列出目前 Linux 上的 Process。

但是平台需要自動執行這些指令，並將結果提供給後續分析使用。

因此需要 Python 主動執行 Linux 指令。

---

# subprocess

`subprocess` 是 Python 用來建立新 Process 並執行外部指令的模組。

例如：

```python
import subprocess

subprocess.run(["ps", "-eo", "pid,comm"])
```

這段程式會讓 Python 執行：

```bash
ps -eo pid,comm
```

---

# 執行流程

```text
Python Process
        │
        ▼
subprocess
        │
        ▼
建立新的 Process
        │
        ▼
執行 ps
        │
        ▼
輸出 Linux Process List
```

---

# 今日實作

程式：

```python
import subprocess

subprocess.run(["ps", "-eo", "pid,comm"])
```

執行：

```bash
python3 monitoring/process_monitor.py
```

可以看到與手動執行以下指令相同的結果：

```bash
ps -eo pid,comm
```

---

# 今日重點

- Python 可以透過 `subprocess` 執行 Linux 指令。
- `subprocess.run()` 會建立新的 Process。
- 目前 `ps` 的輸出仍然只是顯示在終端機。
- 下一步需要將輸出存進 Python 變數，才能提供 Analysis Engine 使用。

---

# 與 HPC AI Performance Engineering Platform 的關聯

Monitoring Framework 的目標是自動收集系統資料。

流程會從：

```text
Linux
        │
        ▼
ps / top / free / iostat
        │
        ▼
Python subprocess
        │
        ▼
Python Data Structure
        │
        ▼
Analysis Engine
        │
        ▼
Performance Report
```

今天完成的是第一步：

```text
Python 可以主動執行 Linux 指令
```

這是後續自動化 Process Monitoring、CPU Monitoring、Memory Monitoring 的基礎。
