# Week 2 Day 2－Function（函式）

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
