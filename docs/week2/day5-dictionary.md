# Week 2 Day 5－Dictionary（字典）

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
