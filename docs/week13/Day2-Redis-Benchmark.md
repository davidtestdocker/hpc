<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day2 — Redis benchmark

[上一課](<Day1-FastAPI-API-Benchmark.md>) · [本週目錄](README.md) · [下一課](<Day3-PostgreSQL-Benchmark.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史redis-benchmark表格。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

這是指定client/資料大小條件下觀測吞吐，不是最大能力。GET比SET快的原因不能只歸AOF，舊Redis YAML未顯式啟用AOF；需當時CONFIG和負載證據。-n對每項測試而非整個清單共用总數。

## 程式／設定與來源

本次核對：[k8s/redis-deployment.yaml](<../../k8s/redis-deployment.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day2-Redis-Benchmark.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
33670
```

PING33670、SET26385、GET30030 req/s為當時摘要；缺raw與持久化設定。

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

# Week13 Day2 - Redis Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/redis-deployment.yaml](../../k8s/redis-deployment.yaml)
- [k8s/redis-service.yaml](../../k8s/redis-service.yaml)

---

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
