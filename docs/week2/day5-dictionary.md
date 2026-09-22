<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day5 — dict 與 JSON

[上一課](<day4-list.md>) · [本週目錄](README.md) · [下一課](<day6-subprocess.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：文內 dict 示例。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現行 monitor 不產出 cpu／memory dict，沒有將程序資訊送入 Analysis Engine 的實作。原文「完整資訊」應理解為示例的選定欄位，不是程序所有屬性。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day5-dictionary.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
process = {
    "pid": 1,
    "name": "systemd",
    "memory": 15
}
```

此 dict 是手寫範例；memory=15 沒指定單位，也不是從 RSS 12584 換算。List 裝多筆、dict 裝欄位的概念成立，但資料來源不能憑欄位名稱推定。

**仍缺的證據／不能證明的事：** 缺 memory 單位、動態擷取與分析結果，不能當作系統性能數據。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 5－Dictionary（字典）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day3-job-identity](../week4/day3-job-identity.md)。

---

## 今日目標

理解如何使用 Dictionary 表示一個 Process 的完整資訊，建立 Monitoring Framework 的基本資料模型。

---

# 為什麼需要 Dictionary？

Linux 的一個 Process 不只有名稱。

例如：

```text
PID     COMMAND     RSS
1       systemd     12584
```

一個 Process 至少包含：

- PID
- Name
- Memory

因此需要一個可以描述多個屬性的資料結構。

---

# Dictionary

建立：

```python
process = {
    "pid": 1,
    "name": "systemd",
    "memory": 15
}
```

代表：

一個 Process 的完整資訊。

---

# Key 與 Value

例如：

```python
"pid": 1
```

其中：

- `pid` 是 Key
- `1` 是 Value

Key 表示欄位名稱。

Value 表示實際資料。

---

# List 與 Dictionary 的關係

一個 Process：

```python
{
    "pid": 1,
    "name": "systemd"
}
```

很多 Process：

```python
[
    {
        "pid": 1,
        "name": "systemd"
    },
    {
        "pid": 320,
        "name": "python3"
    }
]
```

List 用來保存很多 Process。

Dictionary 用來表示一個 Process。

---

# 今日重點

- Dictionary 可以描述一筆完整資料。
- Key 表示欄位。
- Value 表示資料。
- Monitoring Framework 會使用 Dictionary 表示一個 Process。
- List 則保存多個 Process。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來：

```python
get_processes()
```

將回傳：

```python
[
    {
        "pid": 1,
        "name": "systemd",
        "cpu": 0.2,
        "memory": 15
    }
]
```

Analysis Engine 將依據：

- PID
- CPU
- Memory

分析：

- CPU Bottleneck
- Memory Bottleneck
- Process 使用情況

Dictionary 是 Monitoring Framework 最核心的資料模型之一。
