<!-- readable-curriculum: 2026-09-22 -->
# Week5 Day4 — 卡住與重啟接續

[上一課](<day3-reliable-worker-state-machine.md>) · [本週目錄](README.md) · [下一課](<day5-retry-strategy-and-deadletter-que.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：有日期的 worker 重啟接續結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

舊步驟只 LMOVE 沒寫 processing_started_at；現行手動 recover-stuck 直接讀此欄位，缺欄位會出錯，不能照舊步驟聲稱可恢復。主模式 AUTOMATIC_WORKER=true 時這個端點回 409。背景 worker 以 120 秒 lease、每 30 秒續期及掃描 job records 接續，並非每 30 秒回收工作；固定 JobSet 名稱與 owner label 用於重試接回。超時本身也不能證明原 worker 已停止。

## 程式／設定與來源

本次核對：[api/main.py](<../../api/main.py>)、[api/worker.py](<../../api/worker.py>)、[api/workloads/dispatcher.py](<../../api/workloads/dispatcher.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<../evidence/automatic-worker-20260922.json>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
"accepted_without_worker": true,
      "completed_in_kubernetes_while_worker_stopped": true,
```

這是 2026-09-22 GKE hpc-gpu-sg／hpc-platform-dev 的已保存自動 worker 驗收，不是 Week5 舊 Compose 的當日重跑。工作 a697300a-b267-4554-bdd5-2c82bb9c9eda 最終 completed、ranks 為 0/1/2、jobset_count=1。worker 停止期間 Kubernetes 已完成工作，恢復後回收結果；不是本次重新執行。

**仍缺的證據／不能證明的事：** 保存結果涵蓋 queued／submitted 重啟案例；沒有驗證每個指令間崩潰、所有 lease 競態或跨儲存原子性。舊 LMOVE 手動步驟缺原始回應，不能稱已按目前程式驗證成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：新版 worker 掃描 Redis job records 並持有 lease；MPI submitted 後自動收集，終態 DB-first。舊手動 queue 操作不是主環境流程。
> **閱讀順序**：先學本文基礎，再讀[Week5 現行對照與檢核](../learning-guide.md#week5)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week5 Day4 - Stuck Job Recovery

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [compose.yaml](../../compose.yaml)：本機服務組合

---

## 今日平台增加什麼

今天的平台新增：

* Recovery Worker
* Recovery Policy
* Timeout Detection
* `retrying` State

平台能力從：

```text
Pending Queue
    ↓
Processing Queue
    ↓
Completed
```

演進成：

```text
Pending Queue
    ↓
Processing Queue
    ↓
Worker Crash
    ↓
Recovery Worker
    ↓
Retrying
    ↓
Pending Queue
```

---

# Platform Problem

Day3 已經解決：

```text
Worker Crash
    ↓
Job 不會 Lost
```

但是：

```text
Job 卡在 processing_queue
```

仍然沒有任何 Worker 會再處理它。

如果沒有 Recovery 機制：

```text
Processing Queue
    ↓
永遠卡住
```

平台就無法自我修復（Self Recovery）。

---

# 今日知識鏈

```text
Processing Queue
    ↓
processing_started_at
    ↓
Timeout Detection
    ↓
Recovery Policy
    ↓
Retrying
```

---

# Hands-on

## 1. 建立 Recovery API

新增：

```text
POST /worker/recover-stuck
```

功能：

* 掃描 `processing_queue`
* 取得 Processing 中的 Job

---

## 2. 加入 Timeout Detection

利用：

```python
processing_started_at
```

計算：

```text
現在時間
    ↓
開始時間
    ↓
Processing Duration
```

設定：

```text
Timeout = 30 秒
```

只有超過 Timeout 才允許 Recovery。

---

## 3. Recovery Policy

符合條件：

```text
status != completed

AND

processing_time > timeout
```

Recovery Worker：

* 從 `processing_queue` 移除
* 放回 `job_queue`
* 更新狀態為 `retrying`

---

# 驗證

建立 Job：

```bash
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{"benchmark":"cpu"}'
```

模擬 Worker Crash：

```redis
LMOVE job_queue processing_queue LEFT RIGHT
```

確認：

```redis
LRANGE processing_queue 0 -1
```

執行 Recovery：

```bash
curl -X POST http://localhost:8000/worker/recover-stuck
```

再次執行 Worker：

```bash
curl -X POST http://localhost:8000/worker/process-next
```

確認：

```bash
curl http://localhost:8000/jobs
```

驗證：

* Job 被成功 Recovery
* Job 回到 `job_queue`
* Worker 可再次完成 Job
* 最終狀態為 `completed`

---

# 平台架構

```text
                 Client
                    │
                    ▼
                 FastAPI
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Redis job_queue    Redis processing_queue
          │                   │
          ▼                   │
        Worker                │
          │                   │
          ├────────Crash──────┘
          │
          ▼
    Recovery Worker
          │
          ▼
      retrying
          │
          ▼
      job_queue
```

---

# 今日重點

* Recovery Worker 負責找回卡住的 Job。
* `processing_started_at` 是 Timeout 判斷的依據。
* Recovery 必須有 Policy，而不是看到 Processing Job 就立即回收。
* `retrying` 比重新改回 `accepted` 更能反映 Job 的生命週期。
* Recovery 是 Reliable Queue 的核心能力之一。

---

# Interview Q&A

## Q1：為什麼 Recovery 不能直接回收所有 Processing Job？

因為 Worker 可能仍在正常執行。

如果沒有 Timeout，就可能造成兩個 Worker 同時處理同一個 Job（Duplicate Processing）。

---

## Q2：為什麼需要 `retrying` 狀態，而不是改回 `accepted`？

`accepted` 代表第一次進入系統。

Recovery 後的 Job 已經執行過一次，因此使用 `retrying` 能更準確表示 Job 的生命週期，也方便後續加入 Retry Count 與 Failed 狀態。

---

# 下一步

Week5 Day5：

實作 Retry Strategy。

新增：

* `retry_count`
* `max_retry`
* `failed`
* Dead Letter Queue（DLQ）

讓平台具備完整的 Job Failure Handling 能力。
