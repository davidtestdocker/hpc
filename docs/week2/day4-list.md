<!-- current-curriculum: 2026-09-22 -->
# Week2 Day4 — list 與迴圈

[上一課](<day3-return.md>) · [本週目錄](README.md) · [下一課](<day5-dictionary.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「list 與迴圈」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

list 保存有順序的多筆值；迴圈可逐一處理，而 append 增加新元素。分析效能時同一 batch 的多次結果是一組樣本，不該只拿最佳一次代替全組。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[analysis/causal_lm_report.py](<../../analysis/causal_lm_report.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
            'min_tokens_per_second': min(throughput), 'max_tokens_per_second': max(throughput),
            'throughput_cv_percent': statistics.stdev(throughput) / statistics.fmean(throughput) * 100,
            'mean_step_ms': statistics.fmean(r['mean_step_ms'] for r in selected),
            'max_peak_allocated_mib': max(r['peak_allocated_mib'] for r in selected),
            'initial_loss': [r['initial_loss'] for r in selected],
            'final_loss': [r['final_loss'] for r in selected],
        }
    # throughput 上升可代表收益，但 latency／memory 上升則是同時付出的代價。
    change = {metric: (groups['16'][metric] / groups['8'][metric] - 1) * 100
              for metric in ('mean_tokens_per_second', 'mean_step_ms', 'max_peak_allocated_mib')}
    return {'batches': groups, 'batch8_to_16_change_percent': change}


```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 建立 [100, 110, 90] 並算平均，再對照分析器如何挑出同一 batch 的 runs。問自己資料不足三次時應否仍發布比較。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '29,52p' 'analysis/causal_lm_report.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../tests/test_platform_preflight.py>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week2/day4-list.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
