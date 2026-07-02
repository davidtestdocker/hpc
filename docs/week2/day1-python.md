# Week 2 Day 1－Python 與 Monitoring Framework

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
