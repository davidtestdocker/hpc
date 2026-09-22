<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7 — Benchmark 報告總結

[上一課](<day7-7-week13-final-report.md>) · [本週目錄](README.md) · [下一週](../week14/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

不同模型、tokenizer、硬體與測量範圍不能直接算提升率。9/21 synthetic 與 9/22 causal LM 不是同一基準；有效比較是同次固定條件的 batch 8 與 16。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[analysis/causal_lm_report.py](<../../analysis/causal_lm_report.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    change = {metric: (groups['16'][metric] / groups['8'][metric] - 1) * 100
              for metric in ('mean_tokens_per_second', 'mean_step_ms', 'max_peak_allocated_mib')}
    return {'batches': groups, 'batch8_to_16_change_percent': change}


def summarize_trace(trace):
    """只計 CUDA kernel 的完整 duration 事件，排除 CPU wrapper 的重複歸因。"""
    # Chrome trace 的 ph=X 代表含持續時間的完整事件；dur 單位為微秒。
    kernels = [e for e in trace.get('traceEvents', [])
               if e.get('cat') == 'kernel' and e.get('ph') == 'X' and e.get('dur', 0) > 0]
    if not kernels:
        raise ValueError('Trace has no CUDA kernel duration events')
    totals = defaultdict(float)
    counts = defaultdict(int)
    for event in kernels:
        totals[event['name']] += event['dur']
        counts[event['name']] += 1
    total = sum(totals.values())
    # 這是依名稱選出的 kernel 群組，不是完整且互斥的硬體瓶頸分類。
    # duration 相加不是 wall time，也不能直接當 GPU 使用率。
    families = {
        'multi_tensor_named_kernels': sum(v for k, v in totals.items() if 'multi_tensor' in k),
        'gemm_named_kernels': sum(v for k, v in totals.items() if 'gemm' in k.lower()),
    }
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day7-benchmark-report.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
