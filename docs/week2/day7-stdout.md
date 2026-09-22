<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day7 — stdout 與結構化結果

[上一課](<day6-subprocess.md>) · [本週目錄](README.md) · [下一週](../week3/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：示例與歷史輸出分開。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

capture_output=True 捕捉 stdout 和 stderr；text=True 以文字處理輸出。print(result.stdout) 顯示已取得的字串，不負責解析成 list／dict，也沒有後續 Analysis Engine 整合。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<../week3/day6-containerize-monitoring.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
PID COMMAND
1   python3
7   ps
```

本頁原文的 PID COMMAND／1 systemd／2 kthreadd／... 是省略式說明，沒有環境與完整 log；不能當作 container 的實測。上列另引 Week3 的兩列容器記錄，兩者不混為同一次輸出。

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

# Week 2 Day 7－取得 Linux 指令輸出（stdout）

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

理解 Python 如何取得 Linux 指令的輸出，而不是僅執行指令。

---

# 為什麼需要 stdout？

昨天：

```python
subprocess.run(["ps", "-eo", "pid,comm"])
```

只能執行 Linux 指令。

Process List 直接輸出到終端機。

Python 無法繼續處理這些資料。

---

# stdout（Standard Output）

Linux 指令的正常輸出稱為 Standard Output（stdout）。

例如：

```bash
ps -eo pid,comm
```

輸出的 Process List 就是 stdout。

---

# subprocess

程式：

```python
result = subprocess.run(
    ["ps", "-eo", "pid,comm"],
    capture_output=True,
    text=True
)
```

其中：

- `capture_output=True`：將 stdout 保留給 Python。
- `text=True`：將輸出轉換為 Python 字串。

---

# 取得 stdout

程式：

```python
print(result.stdout)
```

Python 就能取得：

```
PID COMMAND
1 systemd
2 kthreadd
...
```

這些資料。

---

# 執行流程

```
Linux
        │
        ▼
ps
        │
        ▼
stdout
        │
        ▼
Python Variable
        │
        ▼
後續分析
```

---

# 今日重點

- Python 不只可以執行 Linux 指令。
- Python 更可以取得 Linux 指令的輸出。
- stdout 是 Monitoring Framework 收集資料的重要來源。
- 後續會將 stdout 解析成 Python 資料結構。

---

# 與 HPC AI Performance Engineering Platform 的關聯

Monitoring Framework 的第一步就是收集 Linux 系統資訊。

流程如下：

```
Linux Command
        │
        ▼
stdout
        │
        ▼
Python
        │
        ▼
List / Dictionary
        │
        ▼
Analysis Engine
        │
        ▼
Performance Report
```

今天完成的是：

Linux 資料正式進入 Python，成為平台可以分析的資料來源。
