<!-- current-curriculum: 2026-09-22 -->
# Week15 Day5 — Benchmark engine

[上一課](<Day4-Runtime-Abstraction.md>) · [本週目錄](README.md) · [下一課](<Day6-Performance-Analyzer.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Benchmark engine」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

計時器需要界定區段並處理 CUDA 非同步；warmup 讓初始化成本不混入穩態，重複與交錯降低順序偏差。profiler 會增加負擔，因此另開執行區段。

## 在現在的專案中

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

本課對照：[benchmark/gpu/causal_lm_benchmark.py](<../../benchmark/gpu/causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    避免每步讀 scalar 引入額外同步。計時迴圈會明確 synchronize。
    """
    x, y = batches[number % len(batches)]
    with record_function('train.zero_grad'):
        optimizer.zero_grad(set_to_none=True)
    with record_function('train.forward_loss'), torch.autocast('cuda', dtype=torch.bfloat16):
        logits = model(x)
        loss = torch.nn.functional.cross_entropy(logits.reshape(-1, 256), y.reshape(-1))
    with record_function('train.backward'):
        loss.backward()
    with record_function('train.optimizer'):
        optimizer.step()
    return loss.detach()


def prepare(corpus, batch):
    """每次測量重建相同初始權重和固定語料窗口，只改 batch 的分組大小。"""
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    model = CausalLM().cuda().train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    # 兩組共享相同、有順序的 128 個窗口；batch 16 每步處理兩倍的例子。
    generator = torch.Generator().manual_seed(SEED + 1)
    starts = torch.randint(len(corpus) - SEQ, (128,), generator=generator)
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 找 CUDA synchronize 與 measured steps，說明 corpus 準備及 profiler 為何不算進 throughput；指出這仍不代表等 token budget 的品質比較。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '58,81p' 'benchmark/gpu/causal_lm_benchmark.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week15/Day5-Benchmark-Engine.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
