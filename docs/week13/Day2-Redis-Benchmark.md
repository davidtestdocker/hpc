<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day2 — Redis benchmark

[上一課](<Day1-FastAPI-API-Benchmark.md>) · [本週目錄](README.md) · [下一課](<Day3-PostgreSQL-Benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Redis 單指令延遲、pipeline 吞吐和包含 DB 的整筆提交是不同測試。payload 大小與連線數影響結果；benchmark 不能用破壞既有 key 的方式準備資料。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    with redis_client.pipeline() as pipe:
        pipe.set(f"job:{job_id}", json.dumps(job))
        pipe.rpush('job_queue', job_id)
        pipe.execute()
    return {
        "message": "benchmark request received",
        "job_id": job_id,
        "benchmark": request.benchmark,
        "status": "accepted",
        "next_step": f"Check job status at GET /jobs/{job_id}"
    }

#第八週要改成scan而不是keys方式
# 讀取 job:* 對應的工作；KEYS 會掃描鍵空間，資料量大時有阻塞風險。
@app.get("/jobs")
def get_jobs():

    job_keys = redis_client.keys("job:*")

    jobs = []

    for key in job_keys:
        # loads 把 JSON 字串還原成 Python 字典或清單。
        job = json.loads(
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/Day2-Redis-Benchmark.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
