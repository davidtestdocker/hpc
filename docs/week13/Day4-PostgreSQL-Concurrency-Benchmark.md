<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day4 — DB concurrency

[上一課](<Day3-PostgreSQL-Benchmark.md>) · [本週目錄](README.md) · [下一課](<day5-resource-monitoring.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史併發比較。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

同時改client、threads與總交易數，不能當純單變因比較。表中50client的303.47ms與164.76TPS關係大致相符；最佳點只限已測點，缺低於10client和重複量測。

## 程式／設定與來源

本次核對：[benchmark/postgres/run_pgbench.sh](<../../benchmark/postgres/run_pgbench.sh>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day4-PostgreSQL-Concurrency-Benchmark.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
150.34
```

10→100client：204.63→150.34TPS、48.87→665.17ms，僅支持此條件下增併發未改善，瓶頸仍是候選。

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
