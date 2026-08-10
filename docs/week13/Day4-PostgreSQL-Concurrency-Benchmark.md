# Week13 Day4 - PostgreSQL Concurrency Benchmark

# 今天平台增加了什麼？

今天平台新增 **Concurrency Benchmark**。

除了測量 TPS 外，也分析不同併發數（Clients）對 PostgreSQL 的影響，找出資料庫的最佳運作區間（Operating Point）。

---

# Benchmark 指令

## 10 Clients

```bash
pgbench -h postgres-service -U hpc -d pgbench -c 10 -j 2 -t 100
```

## 20 Clients

```bash
pgbench -h postgres-service -U hpc -d pgbench -c 20 -j 2 -t 100
```

## 50 Clients

```bash
pgbench -h postgres-service -U hpc -d pgbench -c 50 -j 4 -t 100
```

## 100 Clients

```bash
pgbench -h postgres-service -U hpc -d pgbench -c 100 -j 8 -t 100
```

---

# Benchmark 結果

| Clients | Threads | TPS | Avg Latency |
|---------:|---------:|----:|------------:|
| 10 | 2 | 204.63 | 48.87 ms |
| 20 | 2 | 189.40 | 105.59 ms |
| 50 | 4 | 164.76 | 303.47 ms |
| 100 | 8 | 150.34 | 665.17 ms |

---

# 結果分析

## TPS

隨著 Clients 增加，TPS 並未提升，反而逐漸下降：

- 10 Clients：204 TPS
- 20 Clients：189 TPS
- 50 Clients：165 TPS
- 100 Clients：150 TPS

代表 PostgreSQL 已進入飽和狀態。

---

## Latency

平均交易延遲：

- 48.87 ms
- 105.59 ms
- 303.47 ms
- 665.17 ms

Clients 增加時，等待時間遠高於吞吐量提升。

---

## 飽和點（Saturation Point）

當 Client 持續增加，但 TPS 不再增加，Latency 卻快速上升時，表示系統已超過最佳運作區間。

---

## 可能瓶頸

- Transaction Lock
- WAL 寫入
- CPU Context Switch
- Shared Buffer Contention
- Connection Overhead

---

## Platform Engineer 重點

Benchmark 不只是追求最高 TPS，而是找出：

- 最佳併發數
- 可接受的 Latency
- 系統飽和點
- 是否需要擴充資源或調整 PostgreSQL 設定

---

# Interview（2題）

## Q1

為什麼增加 Clients 不一定會增加 TPS？

**A：** 因為資料庫會受到 CPU、Lock、WAL、Buffer 等資源限制，超過飽和點後，等待時間增加，TPS 反而下降。

---

## Q2

Latency 與 TPS 哪個更重要？

**A：** 兩者都重要。TPS 代表吞吐量，Latency 代表單筆交易回應速度。高 TPS 若伴隨極高 Latency，實際使用者體驗仍會很差。
