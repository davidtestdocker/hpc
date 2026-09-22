<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day2 — CPU 排程

[上一課](<day1-linux-process.md>) · [本週目錄](README.md) · [下一課](<day3-context-switch.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史教材數值摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

nproc 反映程序可用處理單位，不足以判定實體核心數。兩個 yes 的 CPU 百分比不證明永久固定在兩顆核心；需另外有 per-CPU／placement 資料。單一執行緒最多使用一個邏輯 CPU 的時間，不能泛化成每個多執行緒程序都只能一顆。移除把 worker YAML 當本課結果的錯置對照。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<day2-cpu-scheduler.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
- `yes` 的 CPU 使用率接近 100%
```

同頁另保存 nproc 輸出 4，以及兩個 yes 均接近 100% 的文字觀察。這是當時 GCP Ubuntu VM 的敘述，不是現行 Pod 量測，也不是 helm worker resources 的測試結果。

**仍缺的證據／不能證明的事：** 沒有當時 top 完整原始輸出、CPU topology、精確日期或獨立 log；不補造核心綁定結論。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 2－CPU Scheduler（CPU 排程器）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day1-Linux-CPU-Performance-Analysis](../week12/Day1-Linux-CPU-Performance-Analysis.md)。

---

## 今日目標

理解 Linux Scheduler 如何將 Process 分配到 CPU Core 執行，以及 CPU Core 與 Process 的關係。

---

# 為什麼需要 Scheduler？

CPU Core 的數量有限，但系統中可能同時存在數百個 Process。

Linux Scheduler 的工作就是：

- 決定哪個 Process 先執行
- 決定 Process 執行多久
- 決定下一個要執行哪個 Process

CPU Core 不會自己挑選 Process，而是由 Scheduler 負責分配。

---

# CPU Core 與 Process

目前實驗環境：

- GCP Ubuntu VM
- CPU Core：4

如果同時只有四個 Process：

```
Core0 → Process A
Core1 → Process B
Core2 → Process C
Core3 → Process D
```

每個 Process 都可以直接使用一個 CPU Core。

---

# 實驗一：查看 CPU Core

使用指令：

```bash
nproc
```

輸出：

```
4
```

代表目前 VM 有四個 CPU Core。

---

# 實驗二：建立高 CPU 使用率 Process

執行：

```bash
yes > /dev/null
```

再使用：

```bash
top
```

觀察到：

- 新增一個 Running Process
- `yes` 的 CPU 使用率接近 100%

代表一個 Process 可以吃滿一個 CPU Core。

---

# 實驗三：同時執行兩個 yes

再次執行：

```bash
yes > /dev/null
```

再次觀察 `top`：

可以看到兩個 `yes` Process。

兩個 Process 都接近 100% CPU。

代表 Linux Scheduler 將兩個 Process 分配到不同 CPU Core 執行。

---

# 今日重點

Scheduler 負責將 Process 分配到 CPU Core。

CPU Core 不會自己選擇要執行哪個 Process。

當 CPU Core 足夠時，每個高負載 Process 可以獨占一個 Core。

當 Process 數量超過 CPU Core 數量時，Scheduler 就必須在 Process 之間不停切換。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

本質上都是 Linux Process。

Performance Engineer 必須了解 Scheduler 如何分配 CPU，才能分析：

- CPU 是否成為瓶頸
- Benchmark Worker 是否取得足夠 CPU 資源
- TPS 為何下降
- 是否需要調整 CPU 資源配置
