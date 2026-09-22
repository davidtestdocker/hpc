<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7 — Benchmark 報告總結

[上一課](<day7-7-week13-final-report.md>) · [本週目錄](README.md) · [下一週](../week14/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：原頁僅索引，補既有結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

原頁只有四個連結，沒有獨立報告正文或新量測；不要算成另一輪實驗。本頁直接接回儲存結果，其餘見7-1～7-7。

## 程式／設定與來源

本次核對：[benchmark/run_all.sh](<../../benchmark/run_all.sh>)、[benchmark/storage/run_fio.sh](<../../benchmark/storage/run_fio.sh>)、[benchmark/network/run_iperf3.sh](<../../benchmark/network/run_iperf3.sh>)

## 已有結果與解讀

來源：[記錄／示例原文](<../../benchmark/storage/results/fio_20260810.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
4512 KiB/s
```

20260810舊Pod/tmp fio：read4512、write4490KiB/s；同節點網路18.8Gbps是另一份摘要，不混成現在服務驗收。

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



## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/cpu/results/cpu_benchmark_20260810.md](../../benchmark/cpu/results/cpu_benchmark_20260810.md)
- [benchmark/network/results/iperf3_20260810.md](../../benchmark/network/results/iperf3_20260810.md)
- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口
- [benchmark/storage/results/fio_20260810.md](../../benchmark/storage/results/fio_20260810.md)

---
