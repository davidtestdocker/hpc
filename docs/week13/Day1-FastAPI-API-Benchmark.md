# Week13 Day1 - FastAPI API Benchmark

# 今天平台增加了什麼？

今天平台新增了 **API Benchmark 能力**。

以前只能知道 API 有沒有正常運作：

```
curl /
```

現在可以知道：

- API 每秒可以處理多少 Request（RPS）
- 平均延遲（Latency）
- 是否有 Request 失敗
- API 在不同併發數下的效能

這是 Platform Engineer 常做的效能驗證工作。

---

# 架構

```
Benchmark Pod
        │
ApacheBench (ab)
        │
ClusterIP Service
        │
FastAPI Pod
```

> Benchmark Pod 為 Kubernetes 內部的測試 Client，不經過 `kubectl port-forward`。

---

# 建立 Benchmark Pod

```bash
kubectl -n hpc-platform-dev run benchmark \
  --image=debian:12 \
  --restart=Never \
  -it -- bash
```

說明：

- 建立一個臨時 Benchmark Pod
- 進入 Pod 內執行 Benchmark
- 模擬 Kubernetes 內部 Client

---

# 安裝 ApacheBench

```bash
apt update
apt install -y apache2-utils
```

確認：

```bash
ab -V
```

---

# 驗證 API

```bash
curl http://api-service:8000/
```

應回傳：

```json
{
  "message":"HPC API DEV",
  "status":"running"
}
```

---

# 執行 Benchmark

```bash
ab -n 1000 -c 10 http://api-service:8000/
```

## 參數說明

### -n 1000

代表：

總共送出 **1000 次 HTTP Request**。

不是 1000 個使用者，而是：

```
GET /
GET /
GET /
...
共1000次
```

---

### -c 10

代表：

同一時間最多有 **10 個 Request** 同時進行。

流程：

```
Request1
Request2
...
Request10

↓

完成一個

↓

補一個新的

↓

一直保持10個

↓

直到1000個完成
```

---

# Benchmark 結果

```
Requests per second : 126.43 req/sec
Failed requests     : 0
Time taken          : 7.910 sec
Time per request    : 79 ms
Longest Request     : 120 ms
```

---

# Benchmark 指標解析

## Requests per second (RPS)

```
126.43 req/sec
```

意思：

API 平均每秒可處理約 **126 個 Request**。

計算方式：

```
1000 Request
──────────────
7.910 秒

≈126.43 RPS
```

RPS 越高越好。

---

## Failed Requests

```
0
```

表示：

1000 個 Request 全部成功。

沒有：

- Timeout
- Connection Error
- HTTP Error

越接近 0 越好。

---

## Time Taken

```
7.910 秒
```

完成全部 1000 次 Request 所花費的總時間。

越短越好。

---

## Time per Request

```
79 ms
```

平均一個 Request 從送出到收到回應所需時間。

越低越好。

---

## Connection Time

```
Connect
```

建立 TCP Connection 花費時間。

Kubernetes Cluster 內通常非常低。

---

## Processing

```
79 ms
```

API 真正處理 Request 的時間。

如果很高：

通常表示：

- 程式慢
- Database 慢
- Redis 慢

---

## Waiting

Server 開始回傳 Response 前等待的時間。

可視為 Server 回應速度。

---

## Percentile

例如：

```
95%
100 ms
```

代表：

95% 的 Request

都在：

100 ms

以前完成。

這是觀察 API 穩定度的重要指標。

---

# 今天的重要觀念

不要使用：

```
ab
↓

kubectl port-forward
↓

API
```

因為測到的是：

```
Port Forward + API
```

不是 API 真正效能。

應使用：

```
Benchmark Pod
↓

ClusterIP Service
↓

API
```

才符合 Kubernetes 正式環境。

---

# Interview（2題）

## Q1

什麼是 RPS（Requests per Second）？

**A：**

代表 API 每秒可以處理多少個 HTTP Request，是衡量 API 吞吐量的重要指標。

---

## Q2

為什麼 Benchmark 不建議使用 `kubectl port-forward`？

**A：**

因為 `kubectl port-forward` 是開發與除錯工具，本身會增加額外轉發成本，測到的是 Port Forward 的效能，而不是 Kubernetes Service 與 Pod 的真實效能。
