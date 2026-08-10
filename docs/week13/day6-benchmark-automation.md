# Week13 Day6 - Benchmark Automation Framework

## 今天平台增加了什麼？

今天將 PostgreSQL Benchmark 流程從手動操作改造成可重複執行的 Benchmark Runner。

之前執行方式：

```
kubectl exec 進入 Pod

↓

手動輸入 pgbench command

↓

複製 Terminal 結果
```

問題：

- 參數容易輸入錯誤
- 測試流程無法重複
- 結果難以保存與比較

因此建立 Benchmark Script：

```
Benchmark Script

↓

Benchmark Pod

↓

PostgreSQL Service

↓

PostgreSQL Database
```

---

# Framework Structure

目前目錄：

```
benchmark/

└── postgres/

    ├── run_pgbench.sh

    └── results/
```

---

# Benchmark Environment

## Kubernetes

Platform:

```
GKE
```

Namespace:

```
hpc-platform-dev
```

---

## Benchmark Pod

用途：

執行 PostgreSQL Benchmark Client。

包含：

```
pgbench
postgres client tools
```

確認：

```bash
which pgbench
```

結果：

```
/usr/bin/pgbench
```

---

## Target Database

Service:

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

# Step 1 - Create Benchmark Script

建立：

```
benchmark/postgres/run_pgbench.sh
```

功能：

- 執行 PostgreSQL Benchmark
- 接收測試參數
- 保存測試結果


---

# Step 2 - Parameterized Benchmark

Script 支援：

```
./run_pgbench.sh CLIENT THREAD TRANSACTION
```

格式：

```bash
./run_pgbench.sh 10 2 100
```

代表：

|參數|說明|
|-|-|
|10|Concurrent Clients|
|2|Worker Threads|
|100|Transactions per Client|

---

## Example

執行：

```bash
./run_pgbench.sh 10 2 100
```

等同：

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

# Step 3 - Execute Inside Kubernetes Pod

Benchmark Script 不在 Host 執行。

原因：

Host 沒有：

```
pgbench
```

並且無法模擬 Kubernetes Service Network。

因此：

```
Benchmark Pod

        |
        |

postgres-service

        |
        |

postgres-0
```

---

將 Script 複製到 Pod：

```bash
kubectl -n hpc-platform-dev cp \
benchmark/postgres/run_pgbench.sh \
benchmark:/tmp/run_pgbench.sh
```

---

執行：

```bash
kubectl -n hpc-platform-dev exec -it benchmark -- bash
```

---

執行 Benchmark：

```bash
/tmp/run_pgbench.sh 10 2 100
```

---

# Benchmark Result

測試：

```
Clients:
10

Threads:
2

Transactions/client:
100
```

結果：

```
number of transactions actually processed:
1000/1000


number of failed transactions:
0


latency average:
52.029 ms


tps:
192.200688
```

---

# Step 4 - Result Logging

加入 Timestamp Result Log。

每次執行：

```
run_pgbench.sh
```

會建立：

```
results/

└── pgbench_20260809_125240.log
```

內容保存：

- Transaction Result
- Latency
- TPS

---

# Benchmark Framework Flow

完成後流程：

```
User

 |

 |

Benchmark Script

 |

 |

Benchmark Pod

 |

 |

pgbench

 |

 |

PostgreSQL Service

 |

 |

PostgreSQL Database

```

---

# Design Decision

目前 Result Storage 使用 Container Filesystem。

原因：

Week13 目標：

建立 Benchmark Framework。

重點：

- Benchmark execution
- Parameter control
- Result collection


Production 等級保存：

例如：

- Persistent Volume
- Object Storage
- Database Storage

會在 Production Platform 階段處理。

---

# Performance Engineering Insight

Automation 的價值：

從：

```
手動執行測試
```

變成：

```
固定流程 Benchmark Job
```

讓測試結果：

- 可重複
- 可比較
- 可分析

這是 Performance Engineering Workflow 的基礎。

---

# Interview Questions

## Q1

為什麼 Benchmark Client 不直接在 Kubernetes Node 執行？

Answer:

因為 Benchmark Client 應該模擬實際服務環境。

在 Kubernetes 中執行可以包含：

- Service Discovery
- Cluster Network
- Pod Communication

更接近真實工作負載。

---

## Q2

為什麼需要 Benchmark Script，而不是直接執行指令？

Answer:

Script 可以固定測試流程、參數與結果保存方式，使 Benchmark 可以重複執行並進行不同版本比較。

---

# Conclusion

Day6 完成 Benchmark Automation Framework 第一版。

目前平台具備：

- PostgreSQL Benchmark Runner
- Parameterized Testing
- Kubernetes Pod Execution
- Result Logging

下一步：

Day7 將整合 Week13 Benchmark 結果，建立 Benchmark Report。
