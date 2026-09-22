<!-- current-curriculum: 2026-09-22 -->
# Week14 Day6 — Dashboard 與實驗驗證

[上一課](<Day5-GPU-Metrics-Monitoring-integration.md>) · [本週目錄](README.md) · [下一週](../week15/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Dashboard 與實驗驗證」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

圖表能輔助看趨勢，但控制條件、raw result 和 trace 才支撐具體性能結論。9/22 取樣包含 setup／warmup／profile，不應直接對整段算平均後當每組 batch 指標。

## 在現在的專案中

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

本課對照：[docs/performance/causal-lm-l4-20260922.md](<../performance/causal-lm-l4-20260922.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
## 限制

單張 L4 採 time-sharing；本次請求一個 share，不保證硬體隔離。啟動前 `nvidia-smi`
沒有其他 compute process，仍不能把共享設定描述為獨占 GPU。telemetry 是低頻採樣，
包含 setup／warmup／profile／trace export，不能把全程平均當作各 batch 的 GPU 使用率。
記憶體數字是 PyTorch peak allocated，與 reserved 或 nvidia-smi memory used 不同。

這是 13M 小型語言模型的受控訓練實驗，無 held-out dataset、生成品質、pretrained
LLM、multi-GPU scaling 或 RDMA 結論；也尚未接入 MPI API 的 benchmark dispatcher。
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 causal LM 報告限制段，區分 allocated、reserved、nvidia-smi used；回答圖表上 GPU 忙為何不代表模型吞吐已最優。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '73,81p' 'docs/performance/causal-lm-l4-20260922.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../performance/causal-lm-l4-20260922.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week14/Day6-gpu-dashboard-establish-and-gpuworkload-verification.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
