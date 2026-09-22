<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-5 — Framework v2 子章

[上一課](<day7-4-benchmark-framework.md>) · [本週目錄](README.md) · [下一課](<day7-6-result-integration.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史PASS文字，現存失敗傳遞缺口。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

外層pipefail無法修正子腳本已被tee掩蓋的錯誤；PG腳本未設pipefail，所以不能說所有FAIL都攔下。exit0也不驗證throughput達標或無部分交易失敗。

## 程式／設定與來源

本次核對：[benchmark/run_all.sh](<../../benchmark/run_all.sh>)、[benchmark/postgres/run_pgbench.sh](<../../benchmark/postgres/run_pgbench.sh>)

## 已有結果與解讀

來源：[記錄／示例原文](<day7-5-benchmark-framework-v2.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
[PASS] PostgreSQL Benchmark
```

保存PASS摘要，但有效性受子腳本缺口限制；不把歷史PASS改寫成失敗，也不保證數據一定有效。

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

# Week13 Day7-5 - Benchmark Framework v2

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/cpu/run_stress_ng.sh](../../benchmark/cpu/run_stress_ng.sh)：CPU 壓測
- [benchmark/network/run_iperf3.sh](../../benchmark/network/run_iperf3.sh)：網路吞吐測試
- [benchmark/postgres/run_pgbench.sh](../../benchmark/postgres/run_pgbench.sh)：PostgreSQL 壓測
- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口
- [benchmark/storage/run_fio.sh](../../benchmark/storage/run_fio.sh)：儲存 I/O 壓測

---

## 今天平台增加了什麼？

本次將 Benchmark Framework 從單純依序執行，
升級成具有執行狀態判斷的 Framework v2。

新增：

- PASS / FAIL
- Fail Fast
- Exit Code
- Benchmark Summary

讓 Framework 可以判斷每個 Benchmark 是否成功。


---

# Architecture

```text
                   run_all.sh

                       │

        ┌──────────────┼──────────────┐

        │              │              │

      CPU           Storage       PostgreSQL

        │              │              │

   stress-ng           fio          pgbench

        │              │              │

      PASS           PASS           PASS

                       │

                    Network

                       │

                    iperf3

                       │

                     PASS

                       │

                       ▼

                Benchmark Summary
```

---

# Why Framework v2?

原本 Framework v1：

```text
CPU

↓

Storage

↓

PostgreSQL

↓

Network

↓

Completed
```

問題：

如果 PostgreSQL Benchmark 失敗：

```text
PostgreSQL FAIL
```

Framework 仍可能繼續執行：

```text
Network
```

甚至最後仍顯示：

```text
Benchmark Completed
```

這會造成錯誤的測試結果。


---

# Framework v2

現在改成：

```text
Execute Benchmark

↓

Check Exit Code

↓

PASS / FAIL
```

如果 Benchmark 成功：

```text
Exit Code = 0

↓

PASS
```

如果失敗：

```text
Exit Code != 0

↓

FAIL

↓

Stop
```

---

# run_benchmark Function

Framework 建立：

```bash
run_benchmark() {
    NAME=$1
    COMMAND=$2

    echo ""
    echo "======================================"
    echo "${NAME}"
    echo "======================================"

    if eval "${COMMAND}"; then
        echo "[PASS] ${NAME}"
    else
        echo "[FAIL] ${NAME}"
        echo ""
        echo "Benchmark stopped because ${NAME} failed."
        exit 1
    fi
}
```

---

# NAME

第一個參數：

```text
Benchmark Name
```

例如：

```text
CPU Benchmark
```

---

# COMMAND

第二個參數：

```text
Benchmark Command
```

例如：

```bash
bash cpu/run_stress_ng.sh 2 30
```

---

# Exit Code

Linux command 執行完成後會產生：

```text
Exit Code
```

成功：

```text
0
```

失敗：

```text
非 0
```

Framework 使用：

```bash
if eval "${COMMAND}"
```

判斷 Benchmark 是否成功。


---

# Fail Fast

如果其中一個 Benchmark 失敗：

```bash
exit 1
```

Framework 立即停止。

例如：

```text
CPU
PASS

↓

Storage
PASS

↓

PostgreSQL
FAIL

↓

STOP
```

Network 不再繼續執行。

這種設計稱為：

```text
Fail Fast
```

---

# Benchmark Modules

目前 Framework 包含：

```text
CPU Benchmark
```

Tool：

```text
stress-ng
```

---

```text
Storage Benchmark
```

Tool：

```text
fio
```

---

```text
PostgreSQL Benchmark
```

Tool：

```text
pgbench
```

---

```text
Network Benchmark
```

Tool：

```text
iperf3
```

---

# Execution

在 Benchmark Runner Pod：

```bash
cd /tmp/benchmark
```

執行：

```bash
./run_all.sh
```

---

# Successful Result

本次 Framework 執行結果：

```text
[PASS] CPU Benchmark

[PASS] Storage Benchmark

[PASS] PostgreSQL Benchmark

[PASS] Network Benchmark
```

最後：

```text
======================================
 Benchmark Summary
======================================

CPU          PASS
Storage      PASS
PostgreSQL   PASS
Network      PASS

All benchmarks completed successfully.
```

---

# Benchmark Flow

```text
run_all.sh

↓

CPU Benchmark

↓

Check Exit Code

↓

PASS

↓

Storage Benchmark

↓

Check Exit Code

↓

PASS

↓

PostgreSQL Benchmark

↓

Check Exit Code

↓

PASS

↓

Network Benchmark

↓

Check Exit Code

↓

PASS

↓

Summary
```

---

# Why PASS / FAIL Matters

Performance Benchmark 不只是：

```text
取得數字
```

還必須確定：

```text
Benchmark 是否真的成功
```

例如：

PostgreSQL 曾發生：

```text
password authentication failed
```

如果沒有狀態判斷：

Framework 可能：

```text
產生錯誤 Report
```

加入 PASS / FAIL 後：

Framework 可以阻止無效 Benchmark Result。


---

# Platform Engineering Insight

Benchmark Framework 與一般 shell script 的差別：

一般 Script：

```text
Command A

Command B

Command C
```

Framework：

```text
Execute

↓

Validate

↓

Handle Error

↓

Collect Status

↓

Generate Summary
```

因此 Framework 不只是執行工具，

還需要：

- Execution Control
- Error Handling
- Status Management
- Result Management


---

# Current Framework

```text
benchmark/

├── cpu/
│   └── run_stress_ng.sh
│
├── storage/
│   └── run_fio.sh
│
├── postgres/
│   └── run_pgbench.sh
│
├── network/
│   └── run_iperf3.sh
│
├── k8s/
│
└── run_all.sh
```

---

# Interview Questions

## Q1

為什麼 Benchmark Framework 需要 Fail Fast？

Answer：

如果 Benchmark 中途失敗，

後續結果可能失去可信度。

Fail Fast 可以：

立即停止流程，

避免產生錯誤 Benchmark Report。


---

## Q2

Linux Exit Code 有什麼用途？

Answer：

Exit Code 用來表示 command 執行狀態。

```text
0
```

代表成功。

非 0：

代表失敗。

Automation Framework 可以透過 Exit Code：

判斷：

PASS / FAIL。


---

# Completed

Week13 Day7-5 完成：

- Benchmark Framework v2
- PASS / FAIL
- Exit Code Validation
- Fail Fast
- Benchmark Summary
- 四個 Benchmark Module 全部成功執行


---

# Next

Week13 Day7-6

Benchmark Result Integration

目標：

將：

```text
CPU
Storage
PostgreSQL
Network
```

的 Result

集中保存與整理，

讓 Framework 不只：

```text
Run Benchmark
```

還可以：

```text
Collect Result
```
