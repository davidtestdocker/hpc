<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day3 — PostgreSQL benchmark

[上一課](<Day2-Redis-Benchmark.md>) · [本週目錄](README.md) · [下一課](<Day4-PostgreSQL-Concurrency-Benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

pgbench 需要專用資料庫與明確初始化步驟，交易數、client 和 thread 是不同設定。初始化或壓測可能改資料與搶資源，不應拿平台 metadata DB 當預設目標。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[benchmark/postgres/run_pgbench.sh](<../../benchmark/postgres/run_pgbench.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
# 效能測試腳本（run_pgbench）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

HOST="postgres-service"
USER="hpc"
DB="pgbench"

CLIENTS=${1:-10}
THREADS=${2:-2}
TRANSACTIONS=${3:-100}

RESULT_DIR="./results"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

RESULT_FILE="${RESULT_DIR}/pgbench_${TIMESTAMP}.log"


# 建立結果目錄；-p 會建立缺少的父目錄，目錄存在時不報錯。
mkdir -p ${RESULT_DIR}
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/Day3-PostgreSQL-Benchmark.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
