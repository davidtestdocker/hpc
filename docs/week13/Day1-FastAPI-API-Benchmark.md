<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day1 — FastAPI benchmark

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-Redis-Benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

測 /health 主要量簡單 HTTP 路徑，測 POST /benchmark 會寫 DB／Redis 並產生工作，負載和副作用完全不同。提交 QPS 不能當作 MPI 完成吞吐。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def create_benchmark(request: BenchmarkRequest):
    logger.info(
        "Received benchmark request: %s",
        request.benchmark
    )

    # uuid4 產生隨機識別碼；str 轉成字串，作為 Redis key 與回應中的 job_id。
    job_id = str(uuid4())

    job = {
    "job_id": job_id,
    "benchmark": request.benchmark,
    "simulate_failure": request.simulate_failure,
    "status": "accepted",
    "result": None,
    "retry_count": 0
    }

    session = SessionLocal()

    db_job = Job(
        job_id=job_id,
        benchmark=job["benchmark"],
        status=job["status"],
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/Day1-FastAPI-API-Benchmark.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day1 - FastAPI API Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [k8s/api-service.yaml](../../k8s/api-service.yaml)

---

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
