# Week 2 Day 4－List（串列）

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
