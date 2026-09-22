<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day3 — Context switch

[上一課](<day2-cpu-scheduler.md>) · [本週目錄](README.md) · [下一課](<day4-cpu-utilization.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史教材觀察，缺直接計數。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

沒有 context-switch 計數就不能說已量得切換增加多少或其效能成本；執行緒少於 CPU 時也會因阻塞／喚醒而切換。process_monitor.py 不量 cs，原先對照錯誤，已從現行說明移除。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<day3-context-switch.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
- 每個 Process CPU 使用率約 75%～85%
```

原文描述在可用處理單位為 4 的環境啟動五個 yes。四份 CPU 時間平均分給五個單執行緒程序，約 80% 是合理解釋；這仍只是 top 百分比的觀察。

**仍缺的證據／不能證明的事：** 未保存 vmstat／pidstat 切換計數、前後比較及原始 top capture；75%～85% 不是 context-switch benchmark。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 3－Context Switch（上下文切換）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day1-Linux-CPU-Performance-Analysis](../week12/Day1-Linux-CPU-Performance-Analysis.md)。

---

## 今日目標

理解 Context Switch 是什麼，以及它為什麼會影響系統效能。

---

# 什麼是 Context Switch？

當 CPU Core 不足以同時執行所有 Process 時，Linux Scheduler 必須在不同 Process 之間切換。

切換前，需要保存目前 Process 的執行狀態。

切換後，需要恢復下一個 Process 的執行狀態。

這個過程稱為 Context Switch。

---

# 為什麼需要 Context Switch？

目前實驗環境：

- CPU Core：4

建立五個高 CPU 使用率 Process：

```bash
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
```

由於 Process 數量超過 CPU Core 數量，Scheduler 必須不停在 Process 之間切換。

---

# 實驗結果

使用：

```bash
top
```

觀察到：

- 五個 `yes` Process 同時存在
- 每個 Process CPU 使用率約 75%～85%

代表 Scheduler 正在公平分配 CPU 時間，而不是讓某一個 Process 長時間獨占 CPU。

---

# Context Switch 的成本

Context Switch 不會執行任何業務邏輯。

它需要：

- 保存目前 Process 狀態
- 載入下一個 Process 狀態
- 恢復執行

因此會消耗 CPU 時間。

Context Switch 越頻繁，可用於真正運算的 CPU 時間就越少。

---

# 今日重點

- Context Switch 是 Linux Scheduler 在 Process 間切換的過程。
- 當 Process 數量超過 CPU Core 數量時，Context Switch 會增加。
- CPU 使用率高，不代表 CPU 都在做有效工作。
- Context Switch 過多會降低整體效能。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

都是 Linux Process。

如果 Compute Node 的 CPU 資源不足，Scheduler 會增加 Context Switch。

Context Switch 增加後，可能造成：

- TPS 下降
- TTFT 增加
- Latency 增加

因此，Performance Engineer 在分析 CPU Bottleneck 時，不能只看 CPU 使用率，還必須考慮 Context Switch 是否過於頻繁。
