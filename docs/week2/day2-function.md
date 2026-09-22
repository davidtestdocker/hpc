<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day2 — 函式與參數

[上一課](<day1-python.md>) · [本週目錄](README.md) · [下一課](<day3-return.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：文內函式示例。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現存 process_monitor.py 是頂層 subprocess 與 print，沒有 collect_process() 封裝；system_monitor.py 也不存在。API／renderer 的函式可作延伸，但不能把它們的結果冒充此 monitor 函式執行。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day2-function.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
def collect_process():
    print("Collect Process")
```

定義這個函式不會印字；呼叫 collect_process() 才會印出 Collect Process。這是文內小例子的語意，不是已有 get_cpu_usage 等完整函式庫。

**仍缺的證據／不能證明的事：** 文內函式未保存獨立檔與 raw log；没有整合監控器驗收。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 2－Function（函式）

## 對應檔案

文中的 `system_monitor.py` 為規劃中的整合模組，目前沒有可連結的實作。

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day6-subprocess](day6-subprocess.md)。

---

## 今日目標

理解 Function 的用途，以及為什麼 Monitoring Framework 必須使用 Function 來設計程式。

---

# 為什麼需要 Function？

如果沒有 Function，相同的程式碼需要一直複製。

例如：

```python
print("Collect Process")
print("Collect Process")
print("Collect Process")
```

當程式越來越大，維護會變得非常困難。

Function 可以將一段程式命名，之後重複呼叫。

---

# Function

建立 Function：

```python
def collect_process():
    print("Collect Process")
```

代表：

建立一個名為 `collect_process` 的功能。

此時 Function 尚未執行。

---

# 呼叫 Function

程式：

```python
collect_process()
```

代表：

呼叫 `collect_process`。

Python Interpreter 會跳到 Function 內部執行程式。

---

# 執行流程

程式：

```python
def collect_process():
    print("Collect Process")

collect_process()
```

執行順序：

1. 建立 Function。
2. 繼續往下執行。
3. 呼叫 Function。
4. 執行 Function 內容。
5. Function 結束。
6. 程式結束。

Function 不會在定義時立即執行。

---

# 今日重點

- Function 是一段有名字、可以重複使用的程式。
- `def` 用來建立 Function。
- 建立 Function 不代表執行。
- 只有呼叫 Function 時才會真正執行。
- 一個 Function 應只負責一件事情。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來 Monitoring Framework 將由許多 Function 組成，例如：

```text
get_processes()

get_cpu_usage()

get_memory_usage()

get_disk_usage()
```

每個 Function 只負責收集一種資訊。

最後由 `system_monitor.py` 統一呼叫，完成整體系統監控。

這種設計可以提升：

- 可讀性
- 可維護性
- 可測試性
- 可擴充性
