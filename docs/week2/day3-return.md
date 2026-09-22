<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day3 — return 與例外

[上一課](<day2-function.md>) · [本週目錄](README.md) · [下一課](<day4-list.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：文內 return 示例。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現存 monitor 只印 stdout，沒有回傳 list／dict 給 Analysis Engine 的函式。原來圖中的 Monitor→return→Analysis Engine→Report 是設計方向，不能宣稱已整合。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day3-return.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
def get_cpu():
    return 15
```

get_cpu() 回傳固定整數 15，print(cpu) 才顯示 15；沒有呼叫 CPU 採樣工具。collect_process() 回傳文字的示例同樣不是現有 monitor 的 API。

**仍缺的證據／不能證明的事：** 缺函式版 monitor 實作與端到端報告輸出；示例不作實測證據。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 3－Return（回傳值）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day6-subprocess](day6-subprocess.md)。

---

## 今日目標

理解 Function 如何將資料回傳給其他程式，而不是只輸出到畫面。

---

# print() 與 return 的差異

`print()` 的用途：

- 將資料輸出到終端機
- 方便人閱讀

例如：

```python
print("CPU Usage")
```

畫面會顯示：

```
CPU Usage
```

---

`return` 的用途：

- 將資料回傳給呼叫 Function 的程式
- 提供其他 Function 繼續使用

例如：

```python
def get_cpu():
    return 15
```

並不會輸出任何東西。

只有：

```python
cpu = get_cpu()

print(cpu)
```

才會看到：

```
15
```

---

# 執行流程

程式：

```python
def collect_process():
    return "Collect Process"

result = collect_process()

print(result)
```

流程：

```
建立 Function
        │
        ▼
呼叫 Function
        │
        ▼
return 回傳資料
        │
        ▼
result 接收資料
        │
        ▼
print() 輸出資料
```

---

# 今日重點

- `return` 不會將資料印到畫面。
- `return` 是將資料交給其他程式使用。
- `print()` 是給人閱讀。
- `return` 是給程式使用。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來 Monitoring Framework：

```python
get_processes()

get_cpu_usage()

get_memory_usage()

get_disk_usage()
```

都會使用 `return` 回傳資料。

Analysis Engine 再接收這些資料進行分析。

平台的資料流如下：

```
Monitor
        │
        ▼
return
        │
        ▼
Analysis Engine
        │
        ▼
Report Generator
```

Monitoring Framework 不直接分析資料，而是負責收集並回傳資料。
