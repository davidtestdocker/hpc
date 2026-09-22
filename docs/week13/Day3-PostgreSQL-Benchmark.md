<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day3 — PostgreSQL benchmark

[上一課](<Day2-Redis-Benchmark.md>) · [本週目錄](README.md) · [下一課](<Day4-PostgreSQL-Concurrency-Benchmark.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史pgbench結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

TPS限pgbench script/scale/client條件，不能當平台API TPS；初始化專用資料庫是寫入操作，不是read-only。現行腳本以交易數結束，不固定60秒。

## 程式／設定與來源

本次核對：[benchmark/postgres/run_pgbench.sh](<../../benchmark/postgres/run_pgbench.sh>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day3-PostgreSQL-Benchmark.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
48.868 ms
```

10client×100=1000、204.63TPS與48.868ms摘要；沒有完整原始輸出及環境日期。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day3 - PostgreSQL Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/postgres/run_pgbench.sh](../../benchmark/postgres/run_pgbench.sh)：PostgreSQL 壓測
- [k8s/postgres-service.yaml](../../k8s/postgres-service.yaml)
- [k8s/postgres-statefulset.yaml](../../k8s/postgres-statefulset.yaml)

---

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
