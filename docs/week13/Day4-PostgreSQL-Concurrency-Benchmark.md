<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day4 — DB concurrency

[上一課](<Day3-PostgreSQL-Benchmark.md>) · [本週目錄](README.md) · [下一課](<day5-resource-monitoring.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

更多 clients 可能提高吞吐，也可能增加鎖等待、連線競爭與尾延遲。連線池大小限制同時查詢數，增加 HTTP worker 不一定讓 DB 更快。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[api/database/connection.py](<../../api/database/connection.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
from sqlalchemy import create_engine

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres-service"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "hpc_platform"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "hpc"
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/Day4-PostgreSQL-Concurrency-Benchmark.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day4 - PostgreSQL Concurrency Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/postgres/run_pgbench.sh](../../benchmark/postgres/run_pgbench.sh)：PostgreSQL 壓測
- [k8s/postgres-service.yaml](../../k8s/postgres-service.yaml)
- [k8s/postgres-statefulset.yaml](../../k8s/postgres-statefulset.yaml)

---

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
