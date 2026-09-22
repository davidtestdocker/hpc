<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day4 — list 與迴圈

[上一課](<day3-return.md>) · [本週目錄](README.md) · [下一課](<day5-dictionary.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：文內資料結構示例。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

process_monitor.py 回收的是 stdout 字串，未把它解析為 list[dict]；get_processes() 並不存在。範例中的 PID 8432 不能當作保存的真實程序。

## 程式／設定與來源

本次核對：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day4-list.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
processes = [
    "systemd",
    "bash",
    "python3"
]
```

這個手寫 list 的 index 0 是 systemd，index 2 是 python3；它不是从 ps 動態解析得到的列表。資料結構示例可以直接讀，不需啟動服務。

**仍缺的證據／不能證明的事：** 沒有 parser 程式、動態 list 的測試或原始取樣；只成立資料結構教學。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 4－List（串列）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day6-subprocess](day6-subprocess.md)。

---

## 今日目標

理解為什麼 Monitoring Framework 必須使用 List 儲存 Process，而不是使用大量獨立變數。

---

# 為什麼需要 List？

Linux 系統同時會有許多 Process。

例如：

- systemd
- bash
- python3
- sshd
- codex

因此 Monitoring Framework 不可能只回傳一個 Process。

需要一個可以儲存多筆資料的資料結構。

---

# List

建立 List：

```python
processes = [
    "systemd",
    "bash",
    "python3"
]
```

代表：

建立一個包含多個元素的集合。

---

# Element（元素）

每一筆資料都是一個 Element。

例如：

```
systemd
bash
python3
```

都是 List 的 Element。

---

# Index（索引）

List 的位置從 0 開始。

例如：

```python
processes[0]
```

得到：

```
systemd
```

而：

```python
processes[2]
```

得到：

```
python3
```

---

# 今日重點

- Linux 同時存在許多 Process。
- List 可以儲存多筆資料。
- List 的 Index 從 0 開始。
- Monitoring Framework 將使用 List 表示多個 Process。

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
        "name": "systemd"
    },
    {
        "pid": 8432,
        "name": "python3"
    }
]
```

之後再加入：

- CPU
- Memory
- Status

等資訊。

List 是 Monitoring Framework 第一個核心資料結構。
