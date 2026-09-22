<!-- current-curriculum: 2026-09-22 -->
# Week15 Day6 — Performance analyzer

[上一課](<Day5-Benchmark-Engine.md>) · [本週目錄](README.md) · [下一課](<Day7-AI-Runtime-Platform-v1-Integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Performance analyzer」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

分析器先驗 hash，再分 batch 計算均值、CV、latency、memory，CUDA trace 只累計 kernel 事件。CPU wrapper 和 GPU duration 重複相加會誤導結論。

## 在現在的專案中

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

本課對照：[analysis/causal_lm_report.py](<../../analysis/causal_lm_report.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
    return {'kernel_events': len(kernels), 'summed_kernel_duration_us': total,
            'selected_name_families_us': families,
            'note': 'Sum of kernel durations, not wall time or GPU utilization; profiler overhead applies',
            'top_kernels': [{'name': k, 'count': counts[k], 'duration_us': v,
                             'share_of_summed_kernel_time_percent': v / total * 100}
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 summarize_runs 與 summarize_trace，手算 throughput 相對提升與 step time 代價。解釋 kernel duration sum 為何不是 wall time 或 utilization。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '53,76p' 'analysis/causal_lm_report.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week15/Day6-Performance-Analyzer.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
