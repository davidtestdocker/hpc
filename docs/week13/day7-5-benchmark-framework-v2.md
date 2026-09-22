<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-5 — Framework v2 子章

[上一課](<day7-4-benchmark-framework.md>) · [本週目錄](README.md) · [下一課](<day7-6-result-integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

逐步框架應分清執行、結果 schema 和分析，不能把整合目錄當作每一種 workload 都已端到端驗證。新 causal LM runner 保存 image／hash／source，是可追溯設計的具體例子。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[scripts/run_causal_lm_benchmark.py](<../../scripts/run_causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
                'sha256': {f: hashlib.sha256((output / f).read_bytes()).hexdigest()
                           for f in artifacts + ['corpus.txt', 'benchmark-source.py']},
                'passed': True}
    # 成功收回證據才清理本次具名 Pod／ConfigMap；不刪節點、PVC 或其他工作。
    print(kubectl(['delete', 'pod', name, '--wait=false']).decode(), flush=True)
    print(kubectl(['delete', 'configmap', name]).decode(), flush=True)
    evidence['cleanup'] = 'temporary Pod deletion requested; ConfigMap deleted; artifacts retained'
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2), flush=True)


if __name__ == '__main__':
    # --execute 是明確的操作開關，因為此程式會建立、執行並清理叢集資源。
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('--execute is required to create and run the temporary GPU Pod')
    run(args.context, args.name, args.output)
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day7-5-benchmark-framework-v2.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
