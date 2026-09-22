<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day1 — Python 變數與資料型別

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-function.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：程式可推導示例，非實機 log。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

檔案實際在 examples/hello.py，原文 repo 根目錄 python3 hello.py 的路徑不對。monitor 目錄樹中其他模組沒有實作。Python 名稱綁定物件；「由上到下逐行執行」只是入門直線流程，函式／分支／迴圈會改變控制流程。

## 程式／設定與來源

本次核對：[examples/hello.py](<../../examples/hello.py>)、[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<../../examples/hello.py>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
cpu_usage = 15

print(cpu_usage)
```

現存 hello.py 的 cpu_usage 是寫死的 15，所以程式語意上的輸出是 15；不是讀到 CPU 使用率 15%。本次未執行該程式。舊文的 Step 1／2／3 是另一段文內示例，不是此檔的輸出。

**仍缺的證據／不能證明的事：** 沒有這份 hello.py 的獨立執行 log 或系統取樣結果；15 只能標為固定值示例。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
