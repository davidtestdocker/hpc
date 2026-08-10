# Week13 Day2 - Redis Benchmark

# 今天平台增加了什麼？

今天平台新增 **Redis Benchmark 能力**。

以前只能知道：

Redis 有沒有正常運作。

今天開始可以量測：

- Redis 每秒可處理多少 Command
- GET / SET 哪個比較快
- Redis Latency
- Redis Throughput

這是 Platform Engineer 常做的 Redis 效能驗證。

---

# 架構

```

Benchmark Pod
│
redis-benchmark
│
ClusterIP Service
│
Redis Pod

```

---

# Benchmark 指令

```bash
redis-benchmark \
-h redis-service \
-p 6379 \
-n 10000 \
-c 50 \
-t ping,set,get
```

---

# Benchmark 參數

## -h

Redis Host。

```
redis-service
```

---

## -p

Redis Port。

```
6379
```

---

## -n

總共送出的 Command 數。

```
10000
```

---

## -c

同時 Client 數。

```
50
```

代表：

50 個 Client 同時送 Command。

---

## -t

指定測試項目。

本次：

```
PING

SET

GET
```

---

# Benchmark 結果

| Command | Throughput | Avg Latency |
|----------|-----------:|------------:|
| PING | 33670 req/sec | 0.90 ms |
| SET | 26385 req/sec | 1.25 ms |
| GET | 30030 req/sec | 1.06 ms |

---

# Benchmark 指標解析

## Throughput

```
33670 req/sec
```

代表：

Redis 每秒最多可完成：

33670 次 Command。

越高越好。

---

## Average Latency

```
1.06 ms
```

平均每個 Command

完成所需時間。

越低越好。

---

## P50

```
50%

0.94 ms
```

代表：

一半的 Request

都在：

0.94ms

以前完成。

---

## P95

```
95%

1.98 ms
```

95%

Request

都在：

1.98ms

以前完成。

越低代表越穩定。

---

## P99

```
99%

2.72 ms
```

99%

Request

都在：

2.72ms

以前完成。

P99 是業界最常看的延遲指標。

---

## Max

```
38.75 ms
```

最慢的一筆 Request。

通常只代表極少數特殊情況。

不應只看 Max，而應搭配 P95、P99 一起判斷。

---

# 為什麼 GET 比 SET 快？

GET：

```
Memory

↓

回傳資料
```

SET：

```
Memory

↓

修改資料

↓

AOF Persistence

↓

回傳 OK
```

因為需要寫入資料，

SET 通常比 GET 慢。

---

# 今天學到的重要觀念

Redis Benchmark

測的是：

```
Redis Server
```

而不是：

```
FastAPI
```

Redis 使用 RESP Protocol，

沒有 HTTP 與 JSON，

因此 Throughput 遠高於一般 REST API。

---

# Interview（2題）

## Q1

為什麼 Redis GET 通常比 SET 快？

**A：**

GET 只需讀取記憶體並回傳資料；SET 需要修改資料，若啟用 AOF 或其他持久化機制，還需額外寫入，因此通常較慢。

---

## Q2

Benchmark 時為什麼不能只看 Throughput？

**A：**

Throughput 高代表吞吐量大，但若 Latency 很高或 P95、P99 很差，代表使用者仍可能感受到明顯延遲。因此需要同時觀察 Throughput 與 Latency 指標。
