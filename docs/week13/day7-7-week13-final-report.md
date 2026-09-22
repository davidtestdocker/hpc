<!-- current-curriculum: 2026-09-22 -->
# Week13 Day7-7 — Week13 整合報告子章

[上一課](<day7-6-result-integration.md>) · [本週目錄](README.md) · [下一課](<day7-benchmark-report.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Week13 整合報告子章」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

報告依序交代問題、控制條件、結果、解釋和限制。一次調校沒有改善也可形成有效結論，前提是方法可靠，而非只挑成功或隱藏代價。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[docs/performance/causal-lm-l4-20260922.md](<../performance/causal-lm-l4-20260922.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
## 未開 profiler 的結果

| Batch | Mean byte tokens/s | Mean step | Throughput CV | Max peak allocated |
|---:|---:|---:|---:|---:|
| 8 | 110,785 | 18.50 ms | 3.21% | 375.02 MiB |
| 16 | 200,841 | 20.39 ms | 0.42% | 532.39 MiB |

Batch 8→16：throughput **+81.29%**、step latency **+10.25%**、peak allocated
memory **+41.96%**。單步工作量加倍，因此 throughput 提升並非每步變快。
本次 batch 8 的三次範圍為 107,240～114,348；batch 16 為 199,914～201,588。
這是單次實驗中的三次重複，沒有跨日／跨機器的統計推廣。

## Profiling 如何解釋這個取捨

分析器只加總 raw trace 的 `cat=kernel, ph=X` 事件，避免 CPU operator、
record_function 與 GPU kernel 被重複加總。以下皆為 **五步 profiling** 的 CUDA
kernel duration sum，不能當 wall time、GPU utilization 或硬體峰值效率。

| Trace 觀察 | Batch 8 | Batch 16 |
|---|---:|---:|
| CUDA kernel events | 1,575 | 1,665 |
| 全部 kernel duration sum | 48.81 ms | 78.04 ms |
| 名稱包含 multi_tensor 的 kernel sum | 21.71 ms | 21.72 ms |
| 名稱包含 GEMM 的 kernel sum | 12.27 ms | 23.84 ms |
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 用現有 causal LM 報告找出吞吐、step time、memory 的相對變化，分開標示觀察與 optimizer 固定成本推論。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '26,49p' 'docs/performance/causal-lm-l4-20260922.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week13/day7-7-week13-final-report.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
