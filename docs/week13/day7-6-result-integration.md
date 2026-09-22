<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-6 — 結果整合子章

[上一課](<day7-5-benchmark-framework-v2.md>) · [本週目錄](README.md) · [下一課](<day7-7-week13-final-report.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

JSON schema 讓分析器能檢查必要欄位；checksum 防止不小心修改原始資料後仍引用舊结論。summary 是衍生結果，不能取代 raw latency 和環境快照。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[analysis/causal_lm_report.py](<../../analysis/causal_lm_report.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def verify_bundle(directory):
    """比對 evidence.json 登錄的 SHA-256，拒絕分析已被改動的原始結果。"""
    evidence = json.loads((directory / 'evidence.json').read_text())
    for name, expected in evidence['sha256'].items():
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Artifact checksum mismatch: {name}')


def summarize_runs(runs):
    """各 batch 至少三次；保留均值、範圍與 CV，計算 8→16 的相對變化。"""
    groups = {}
    for batch in (8, 16):
        selected = [r for r in runs if r['batch_size'] == batch]
        if len(selected) < 3:
            raise ValueError('At least three runs per batch required')
        throughput = [r['tokens_per_second'] for r in selected]
        if not all(math.isfinite(x) and x > 0 for x in throughput):
            raise ValueError('Throughput must be finite and positive')
        # CV = 樣本標準差／均值，表示重複測量波動；不是信賴區間。
        # peak memory 取三次中的最大值；throughput 與 mean step 則各自取平均。
        groups[str(batch)] = {
            'repetitions': len(selected),
            'mean_tokens_per_second': statistics.fmean(throughput),
```

## 已有結果與解讀

### 單 L4 訓練：已保存的實測數據

日期：2026-09-22；環境：GKE hpc-gpu-sg、單 NVIDIA L4、PyTorch 2.12.0+cu126。模型為 13M causal LM、byte tokenizer，不是 pretrained 大模型。20 warmup、40 measured steps，各 batch 三次交錯量測。

| Batch | 次數 | Mean byte tokens/s | Mean step ms | Peak allocated MiB | Throughput CV |
|---:|---:|---:|---:|---:|---:|
| 8 | 3 | 110,785 | 18.50 | 375.02 | 3.21% |
| 16 | 3 | 200,841 | 20.39 | 532.39 | 0.42% |

結果：吞吐 **+81.29%**，每步時間 **+10.25%**，顯存峰值 **+41.96%**。每步工作量加倍，所以不是「每步變快」，也不能推出模型品質更好。

另做的五步 CUDA profiling：batch 8／16 的 multi-tensor kernel 累積時間約 21.71／21.72 ms，GEMM 約 12.27／23.84 ms。這支持每步固定 optimizer 成本被較大 batch 攤薄的推論；kernel 時間總和不是 wall time，也不直接證明 compute-bound 或 memory-bound。

你不需要再跑 GPU：[保存的摘要](<../../benchmark/results/causal-lm-20260922/summary.json>)、[原始逐步數據](<../../benchmark/results/causal-lm-20260922/result.json>)、[完整解讀與限制](<../performance/causal-lm-l4-20260922.md>)已足夠直接閱讀。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day7-6-result-integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day7-6 - Benchmark Result Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/cpu/results/cpu_benchmark_20260810.md](../../benchmark/cpu/results/cpu_benchmark_20260810.md)
- [benchmark/network/results/iperf3_20260810.md](../../benchmark/network/results/iperf3_20260810.md)
- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口
- [benchmark/storage/results/fio_20260810.md](../../benchmark/storage/results/fio_20260810.md)

---

## 今天平台增加了什麼？

本次完成 Benchmark Result Integration。

Benchmark Framework 不再只執行 Benchmark，

而是：

```text
Run Benchmark

↓

Collect Result

↓

Save Result
```

建立每次 Benchmark 專屬 Result Directory。

---

# Architecture

```text
                run_all.sh

                     │

          Create Result Directory

                     │

     results/20260810_071421/

                     │

     ┌──────┬────────┬─────────┬─────────┐

     │      │        │         │

 cpu.log storage.log postgres.log network.log
```

Framework 每次執行：

都建立新的 Benchmark Session。

---

# Why Result Integration?

原本：

```text
Benchmark

↓

Terminal Output

↓

結束
```

所有結果：

重新執行後：

就消失。

現在：

```text
Benchmark

↓

Terminal

+

Log File

↓

永久保存
```

---

# Result Directory

Framework：

自動建立：

```text
results/

└──20260810_071421/
```

每一次 Benchmark：

皆建立：

新的 Timestamp Directory。

避免：

不同 Benchmark Result 被覆蓋。

---

# Result Files

CPU

```text
cpu.log
```

Storage

```text
storage.log
```

PostgreSQL

```text
postgres.log
```

Network

```text
network.log
```

所有 Benchmark

皆獨立保存。

---

# tee

Framework 使用：

```bash
tee
```

原理：

```text
Benchmark Output

        │

        ├──────► Terminal

        │

        └──────► Log File
```

因此：

Benchmark

仍可即時觀看。

同時：

保存完整 Log。

---

# pipefail

Framework 使用：

```bash
set -euo pipefail
```

原因：

目前：

Benchmark：

```text
Command

↓

tee
```

形成：

```text
Pipeline
```

如果：

Benchmark Fail

但：

tee Success

Framework

可能誤判：

PASS。

加入：

```text
pipefail
```

Pipeline

只要任何一個 Command Fail：

Framework 即判定：

FAIL。

---

# Current Result Structure

```text
benchmark/

results/

└──20260810_071421/

    ├──cpu.log

    ├──storage.log

    ├──postgres.log

    └──network.log
```

---

# Verification

本次成功建立：

```text
cpu.log
```

```text
storage.log
```

```text
postgres.log
```

```text
network.log
```

所有 Log

均成功保存。

---

# Platform Engineering Insight

Production Benchmark

通常：

不只需要：

```text
Benchmark Number
```

更需要：

```text
Benchmark History
```

因此：

Benchmark Result

必須：

集中管理。

方便：

- Performance Comparison
- Regression Detection
- Historical Analysis

---

# Interview Questions

## Q1

為什麼 Benchmark 要保存 Log？

Answer：

方便：

- 問題追蹤
- 效能比較
- Regression Analysis
- Benchmark History

而不是只有 Terminal Output。

---

## Q2

tee 有什麼用途？

Answer：

同時：

將 Output：

輸出到：

Terminal

與

Log File。

不用重跑 Benchmark。

---

## Q3

為什麼要使用 pipefail？

Answer：

Pipeline：

只要任何 Command Fail，

Framework 即判定失敗。

避免：

tee 成功，

但 Benchmark 實際失敗。

---

# Completed

Week13 Day7-6 完成：

- Result Integration
- Timestamp Result Directory
- CPU Log
- Storage Log
- PostgreSQL Log
- Network Log
- tee
- pipefail

---

# Next

Week13 Day7-7

Week13 Final Report

完成：

- Benchmark Framework Summary
- Platform Architecture
- Week13 Benchmark Report
- Week13 Interview Review
