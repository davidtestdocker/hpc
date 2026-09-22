<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](<../../../learning-guide.md#week13>)及[對應現行入口](<../../../performance/causal-lm-l4-20260922.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day5 - Benchmark Resource Monitoring

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/k8s/benchmark-runner.yaml](<../../../../benchmark/k8s/benchmark-runner.yaml>)
- [benchmark/postgres/run_pgbench.sh](<../../../../benchmark/postgres/run_pgbench.sh>)：PostgreSQL 壓測
- [k8s/postgres-statefulset.yaml](<../../../../k8s/postgres-statefulset.yaml>)

---

## 今天平台增加了什麼？

今天將 Benchmark 與 Kubernetes Resource Monitoring 整合。

前幾天主要觀察：

- TPS
- Throughput
- Latency

但單純看 Benchmark 數據無法判斷瓶頸來源。

因此今天加入 Kubernetes Metrics：

- Pod CPU Usage
- Pod Memory Usage
- Node CPU Usage
- Node Memory Usage

建立：

Benchmark → Resource → Bottleneck Analysis

的效能分析流程。

---

# 實驗環境

## Kubernetes

Platform:

GKE

Namespace:

```
hpc-platform-dev
```

---

## Benchmark Target

PostgreSQL:

```
postgres-service:5432
```

Database:

```
pgbench
```

User:

```
hpc
```

---

# Monitoring Tools

使用 Kubernetes Metrics API：

```bash
kubectl top pods -n hpc-platform-dev

kubectl top nodes
```

觀察：

- Container CPU
- Container Memory
- Node Resource Usage

---

# Benchmark Command

使用 pgbench 進行 PostgreSQL 壓力測試：

```bash
pgbench \
-h postgres-service \
-U hpc \
-d pgbench \
-c 100 \
-j 8 \
-t 1000
```

參數：

| 參數 | 說明 |
|-|-|
| -c 100 | 建立 100 個 concurrent clients |
| -j 8 | 使用 8 個 worker threads |
| -t 1000 | 每個 client 執行 1000 transactions |

總交易量：

```
100 clients × 1000 transactions

= 100,000 transactions
```

---

# Benchmark Result

## pgbench Output

```
number of clients: 100

number of threads: 8

number of transactions actually processed:
100000/100000

failed transactions:
0

latency average:
665.155 ms

tps:
150.340909
```

---

# Resource Observation

## PostgreSQL Pod

壓測前：

```
CPU:
1m

Memory:
59Mi
```

壓測期間：

```
CPU:
603m

Memory:
238Mi
```

---

## Node Resource

Primary Node：

壓測前：

```
CPU:
12%

Memory:
43%
```

壓測期間：

```
CPU:
67%

Memory:
45%
```

---

# Result Analysis

## 1. PostgreSQL CPU 明顯增加

CPU:

```
1m

↓

603m
```

代表 PostgreSQL 確實承受 Benchmark workload。

資料庫不是 idle 狀態。

---

## 2. Memory 不是主要瓶頸

PostgreSQL:

```
59Mi

↓

238Mi
```

雖然增加，但 Node Memory：

```
43%

↓

45%
```

沒有明顯上升。

因此目前沒有 Memory Pressure。

---

## 3. Node CPU 尚未飽和

Node CPU：

```
67%
```

仍未達：

```
90~100%
```

因此目前不是 GKE Node CPU 不足。

---

# Bottleneck Analysis

根據 Day4 Concurrency Benchmark：

| Client | TPS | Latency |
|-|-|-|
|10|204|48ms|
|20|189|105ms|
|50|165|303ms|
|100|150|665ms|

可以看到：

Client 增加後：

- TPS 沒有提升
- Latency 大幅增加

結合 Resource Metrics：

目前較可能瓶頸：

- PostgreSQL transaction synchronization
- Lock contention
- WAL commit latency
- Database internal contention

而非：

- Kubernetes Node CPU
- Memory Capacity

---

# Performance Engineering Insight

Benchmark 不只是取得 TPS。

完整分析流程：

```
Generate Load

↓

Measure Performance

↓

Observe Resource Usage

↓

Identify Bottleneck

↓

Optimize
```

需要同時觀察：

- Application Metrics
- Database Metrics
- Kubernetes Resource Metrics

才能判斷真正瓶頸位置。

---

# Interview Questions

## Q1

為什麼 Benchmark 時不能只看 TPS？

Answer:

TPS 只代表吞吐量，無法表示系統是否接近飽和。
需要搭配 Latency、CPU、Memory 等資訊，才能判斷瓶頸來源。

---

## Q2

如何判斷 CPU 是不是效能瓶頸？

Answer:

如果壓測期間 CPU 長時間接近 90~100%，且 TPS 不再提升、Latency 增加，通常代表 CPU 可能是瓶頸。
如果 CPU 未滿載但 TPS 下降，則需要檢查 Lock、IO、Database synchronization 等因素。

---

# Conclusion

本日完成 Benchmark 與 Kubernetes Resource Monitoring 整合。

目前平台已具備：

- Benchmark execution
- Resource observation
- Performance bottleneck analysis

下一步將進入 Resource Configuration 與 Benchmark Automation。
