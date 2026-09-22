<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-4 — Benchmark framework 子章

[上一課](<day7-3-network-benchmark.md>) · [本週目錄](README.md) · [下一課](<day7-5-benchmark-framework-v2.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

共同 runner 統一參數和保存位置，但各工具仍有不同成功契約。shell pipeline 若只看 tee 的 exit code，可能掩蓋前面工具失敗；pipefail 可避免這種誤判。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[benchmark/run_all.sh](<../../benchmark/run_all.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
run_benchmark() {
    NAME=$1
    COMMAND=$2
    LOG_FILE=$3

    echo ""
    echo "======================================"
    echo "${NAME}"
    echo "======================================"

    # eval 由 Shell 再解析命令字串；2>&1 合併標準錯誤，tee 同時顯示與寫入 log。
    # if 根據管線退出狀態判斷 PASS／FAIL；pipefail 可避免 tee 成功掩蓋 benchmark 失敗。
    if eval "${COMMAND}" 2>&1 | tee "${RESULT_DIR}/${LOG_FILE}"; then
        echo "[PASS] ${NAME}"
    else
        echo "[FAIL] ${NAME}"
        echo ""
        echo "Benchmark stopped because ${NAME} failed."
        exit 1
    fi
}

echo "======================================"
echo " HPC AI Benchmark Framework"
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day7-4-benchmark-framework.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day7-4 - Benchmark Framework Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/cpu/run_stress_ng.sh](../../benchmark/cpu/run_stress_ng.sh)：CPU 壓測
- [benchmark/network/run_iperf3.sh](../../benchmark/network/run_iperf3.sh)：網路吞吐測試
- [benchmark/postgres/run_pgbench.sh](../../benchmark/postgres/run_pgbench.sh)：PostgreSQL 壓測
- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口
- [benchmark/storage/run_fio.sh](../../benchmark/storage/run_fio.sh)：儲存 I/O 壓測

---

## 今天平台增加了什麼？

本次完成 HPC AI Benchmark Framework 第一版。

原本：

每個 Benchmark 都需要手動執行。

例如：

```text
stress-ng

fio

pgbench

iperf3
```

現在：

```text
run_all.sh

↓

CPU Benchmark

↓

Storage Benchmark

↓

PostgreSQL Benchmark

↓

Network Benchmark
```

透過一個入口即可完成所有 Benchmark。

---

# Architecture

```text
               Benchmark Runner

                    │

               run_all.sh

                    │

    ┌────────┬────────┬────────┬────────┐

    │        │        │        │

 CPU      Storage  PostgreSQL Network

    │        │        │        │

stress-ng   fio    pgbench   iperf3
```

Framework：

負責：

- 呼叫各 Benchmark
- 控制 Benchmark 順序
- 建立統一入口

---

# Benchmark Directory

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

目前所有 Benchmark

皆以 Module 管理。

---

# Benchmark Runner

Benchmark Pod：

```text
benchmark
```

用途：

```text
Benchmark Runner
```

負責：

- CPU Benchmark
- Storage Benchmark
- PostgreSQL Benchmark
- Network Benchmark

所有 Benchmark

皆於同一個 Pod 執行。

---

# Benchmark Flow

```text
run_all.sh

↓

CPU Benchmark

↓

Storage Benchmark

↓

PostgreSQL Benchmark

↓

Network Benchmark

↓

Finish
```

Framework

負責：

依照固定順序執行所有 Benchmark。

---

# Why Benchmark Runner?

如果每次：

```text
kubectl exec

↓

執行一個 Tool

↓

離開

↓

再進 Pod

↓

再執行下一個 Tool
```

效率很差。

建立 Benchmark Runner 後：

所有 Benchmark

統一於：

```text
benchmark Pod
```

完成。

---

# Benchmark Image

目前：

使用：

```text
debian:12
```

第一次建立：

需要：

```text
apt install

stress-ng

fio

iperf3

postgresql-client
```

原因：

Container

屬於：

```text
Ephemeral
```

Pod 重建：

所有套件消失。

---

未來 Production：

將建立：

```text
benchmark-runner Image
```

預先安裝：

- stress-ng
- fio
- iperf3
- pgbench

避免：

每次重新安裝。

---

# run_all.sh

目前：

```bash
./run_all.sh
```

即可依序執行：

- CPU
- Storage
- PostgreSQL
- Network

建立統一 Benchmark Entry Point。

---

# Observation

完成：

- Benchmark Runner Pod
- Benchmark Framework
- 統一 Benchmark Script
- Modular Benchmark Design

目前 Framework

已具備：

CPU

Storage

Database

Network

四種 Benchmark。

---

# HPC AI Performance Insight

大型 HPC AI Platform

通常不會：

人工逐一執行 Benchmark。

而會：

```text
Framework

↓

Scheduler

↓

Benchmark

↓

Result

↓

Report
```

目前平台：

已建立：

Framework 雛形。

---

# Interview Questions

## Q1

為什麼需要 Benchmark Framework？

Answer：

避免人工逐一執行 Benchmark。

建立統一入口，

提高自動化程度。

---

## Q2

為什麼使用 Benchmark Runner Pod？

Answer：

所有 Benchmark Tool

集中於同一個 Runtime。

避免：

不同 Pod

造成環境差異。

---

# Completed

Week13 Day7-4 完成：

- 建立 Benchmark Runner
- 建立統一 Benchmark Framework
- 建立 run_all.sh
- 完成 CPU / Storage / PostgreSQL / Network 整合
- 建立 Modular Benchmark Architecture

---

# Next

Week13 Day7-5

Benchmark Framework v2

新增：

- PASS / FAIL
- Summary
- Exit Code
- Fail Fast
