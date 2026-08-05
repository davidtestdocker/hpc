# Week12 Day7 - Linux System Call Analysis with strace

## 目標

本章節學習使用 Linux `strace` 分析程式與 Linux Kernel 的互動，了解 System Call 的運作方式，並學會利用 `strace` 分析 File I/O、Network I/O 與 Production 問題。

完成本章後，可以回答：

- 什麼是 System Call？
- User Space 與 Kernel Space 有什麼差異？
- 為什麼程式需要透過 Kernel 存取硬體？
- `strace` 在分析什麼？
- 如何分析 File I/O？
- 如何分析 Network I/O？
- 如何 Attach 到正在執行的 Process？
- 如何利用 `strace` 排查 API 效能問題？

---

# 今日學習重點

- Linux System Call
- User Space
- Kernel Space
- strace
- File I/O
- Network I/O
- Process Attach
- Production Debug

---

# Lab Environment

OS

```text
Ubuntu 24.04
```

Environment

```text
Google Cloud Platform VM
```

Tool

```text
strace 5.16
```

---

# 為什麼需要 strace？

Benchmark 可以回答：

```
程式有多快？
```

perf 可以回答：

```
CPU 時間花在哪裡？
```

strace 則回答：

```
程式正在要求 Linux Kernel 做什麼？
```

---

# User Space 與 Kernel Space

Linux 將程式分成：

```
User Space
        │
System Call
        │
Kernel Space
```

一般程式不能直接：

- 存取 SSD
- 存取 Network
- 存取硬體

都必須透過：

```
System Call
```

交由 Linux Kernel 處理。

---

# strace 是什麼？

`strace`

可以攔截程式所有 System Call。

例如：

- open()
- read()
- write()
- connect()
- send()
- recv()

因此可了解：

程式究竟在做什麼。

---

# 第一個 strace

執行：

```bash
strace ls
```

即可觀察：

Linux 如何執行：

```
ls
```

---

# execve()

例如：

```text
execve("/usr/bin/ls", ...)
```

代表：

Linux 啟動：

```
ls
```

幾乎所有 Linux 指令：

- python
- docker
- kubectl
- helm

最後都會透過：

```
execve()
```

啟動。

---

# openat()

例如：

```text
openat(...)
```

代表：

開啟檔案。

例如：

- Config File
- Library
- Database File
- Log File

若：

```
openat()
```

停留很久，

可能代表：

- Disk
- NFS
- PVC
- Filesystem

出現問題。

---

# read()

例如：

```text
read(...)
```

代表：

Kernel

從檔案、

Socket、

Device

讀取資料。

若：

```
read()
```

等待很久，

可能代表：

- Disk I/O
- Network
- Storage

較慢。

---

# write()

例如：

```text
write(...)
```

代表：

將資料寫入：

- Terminal
- File
- Socket

例如：

```
printf()

↓

write()
```

---

# connect()

例如：

```text
connect(...)
```

代表：

建立 TCP Connection。

例如：

FastAPI：

```
↓

Redis

↓

connect()
```

或：

```
↓

PostgreSQL

↓

connect()
```

若：

```
connect()
```

等待很久，

第一個懷疑：

- Redis
- PostgreSQL
- DNS
- Firewall
- Network Policy

---

# send()

例如：

```text
sendto(...)
```

代表：

透過 TCP

傳送資料。

例如：

```
SQL Query

↓

send()
```

---

# recv()

例如：

```text
recvfrom(...)
```

代表：

等待 Server 回應。

例如：

```
PostgreSQL

↓

recv()
```

若：

```
recv()
```

等待很久，

代表：

程式正在等待：

- PostgreSQL
- Redis
- HTTP API
- gRPC

而不是 CPU 運算。

---

# Attach 到執行中的 Process

Production

通常不能重啟服務。

因此：

先找 PID：

```bash
ps -ef
```

再：

```bash
strace -p <PID>
```

即可分析：

已執行中的 Process。

---

# Kubernetes

在 Kubernetes：

先：

```bash
kubectl exec -it <pod> -- sh
```

取得：

PID：

```bash
ps -ef
```

再：

```bash
strace -p <PID>
```

即可分析：

Pod 內部程式。

---

# 過濾 System Call

只看：

File：

```bash
strace -e trace=openat ls
```

只看：

Network：

```bash
strace -e trace=network -p <PID>
```

只看：

read / write：

```bash
strace -e trace=read,write <command>
```

Production

通常都會使用：

```
-e trace
```

避免輸出過多資訊。

---

# Production Debug Flow

```
API 很慢
        │
        ▼
top
        │
CPU 高？
        │
 ┌──────┴──────┐
 │             │
Yes           No
 │             │
 ▼             ▼
perf         strace
               │
               ▼
connect()
recv()
read()
               │
               ▼
Redis？
PostgreSQL？
Disk？
Network？
```

---

# 今日重點

- `strace` 用於分析程式與 Linux Kernel 的互動。
- 所有 File、Network、Process 操作都透過 System Call 完成。
- `openat()` 用於分析 File I/O。
- `connect()` 用於分析 TCP Connection。
- `recv()` 可判斷是否等待外部服務。
- `strace -p` 可分析執行中的 Process。
- `-e trace=` 可快速過濾指定類型的 System Call。

---

# Interview

## Q1：`strace` 與 `perf` 有什麼差異？

**答：**

`perf` 用於分析 CPU 執行時間與 Hotspot；`strace` 用於分析程式呼叫的 System Call，可觀察 File I/O、Network I/O 與 Kernel 互動。

---

## Q2：如果 API 很慢，但 CPU 使用率很低，你會如何排查？

**答：**

先使用 `strace` attach 到執行中的 Process，觀察是否卡在 `connect()`、`recvfrom()` 或 `read()` 等 System Call，再判斷是否為 Redis、PostgreSQL、Disk 或 Network 問題。

---

## Q3：Production 為什麼通常使用 `strace -p <PID>`？

**答：**

因為線上服務通常不能重啟，使用 `strace -p <PID>` 可以直接附加到正在執行的 Process，觀察 System Call，而不影響服務運作。
