# Week 2 Day 6－subprocess 執行 Linux 指令

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
