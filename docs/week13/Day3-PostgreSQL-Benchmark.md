# Week13 Day3 - PostgreSQL Benchmark

# 今天平台增加了什麼？

今天平台新增 **PostgreSQL Benchmark 能力**。

平台現在可以量測：

- Database TPS
- Transaction Latency
- Concurrent Clients
- Database Transaction Performance

至此平台已具備：

- HTTP Benchmark
- Redis Benchmark
- PostgreSQL Benchmark

三種效能測試能力。

---

# 架構

```
Benchmark Pod
      │
pgbench
      │
postgres-service
      │
PostgreSQL
```

---

# 初始化 Benchmark Database

建立專用 Database：

```sql
CREATE DATABASE pgbench;
```

初始化：

```bash
pgbench -i \
-h postgres-service \
-U hpc \
-d pgbench
```

建立測試資料：

- pgbench_accounts
- pgbench_branches
- pgbench_history
- pgbench_tellers

---

# Benchmark 指令

```bash
pgbench \
-h postgres-service \
-U hpc \
-d pgbench \
-c 10 \
-j 2 \
-t 100
```

---

# Benchmark 參數

## -c

Concurrent Clients。

```
10
```

代表：

10 個 Client 同時送出交易。

---

## -j

Worker Threads。

```
2
```

代表：

pgbench 使用 2 個執行緒處理 Benchmark。

---

## -t

Transactions per Client。

```
100
```

每位 Client 執行 100 次 Transaction。

總交易數：

```
10 × 100 = 1000 Transactions
```

---

# Benchmark 結果

| 指標 | 結果 |
|------|------|
| Clients | 10 |
| Threads | 2 |
| Transactions | 1000 |
| Failed | 0 |
| Average Latency | 48.868 ms |
| TPS | 204.63 |

---

# Benchmark 指標解析

## TPS

Transactions Per Second。

代表：

每秒可完成多少完整資料庫交易。

本次：

```
204 TPS
```

---

## Average Latency

```
48.868 ms
```

完成一筆 Transaction 平均所需時間。

不是單一 SQL，而是整個交易。

---

## Initial Connection Time

```
153 ms
```

第一次建立 PostgreSQL Connection 所需時間。

不計入 TPS。

---

## Failed Transactions

```
0%
```

代表所有 Transaction 均成功完成。

---

# Transaction 與 SQL 的差異

SQL：

```
SELECT
```

只是單一指令。

Transaction：

```
BEGIN

↓

SELECT

↓

UPDATE

↓

INSERT

↓

COMMIT
```

代表一整個交易流程。

因此 PostgreSQL Benchmark 使用 TPS，而非 Requests/sec。

---

# 今天學到的重要觀念

Redis Benchmark：

測量單一 Command。

PostgreSQL Benchmark：

測量完整 Transaction。

兩者不能直接比較 Throughput。

---

# Interview（2題）

## Q1

為什麼 PostgreSQL Benchmark 使用 TPS，而不是 Requests/sec？

**A：**

因為 PostgreSQL 測量的是完整 Transaction（BEGIN → SQL → COMMIT），而非單一 Request 或 SQL。

---

## Q2

`-c` 與 `-j` 有什麼不同？

**A：**

`-c` 是同時連線的 Client 數量；`-j` 是 pgbench 使用的 Worker Thread 數量，用來處理這些 Client 的工作。
