# Week 2 Day 3－Return（回傳值）

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
