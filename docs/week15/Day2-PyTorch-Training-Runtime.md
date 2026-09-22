<!-- current-curriculum: 2026-09-22 -->
# Week15 Day2 — 現行 causal LM 訓練

[上一課](<Day1—PyTorch-GPU-Runtime.md>) · [本週目錄](README.md) · [下一課](<Day3-vLLM-Inference-Runtime.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「現行 causal LM 訓練」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

causal mask 阻止看未來 token，target 是輸入位移一格。每次相同 seed 重建模型，loss finite／下降能檢查訓練運作，但沒有 held-out 評估就不能推成模型泛化品質。

## 在現在的專案中

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

本課對照：[benchmark/gpu/causal_lm_benchmark.py](<../../benchmark/gpu/causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def step(model, optimizer, batches, number):
    """一次訓練更新：清梯度 → BF16 forward／loss → backward → AdamW。

    record_function 為 profiler 標記階段；回傳仍在 GPU 的 detached loss，
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
```

## 閱讀與練習

先把一個 training step 拆成四段：

1. **Forward**：模型從 byte tokens 產生每個位置的 logits。
2. **Loss**：以位移一格的 target 計算 next-byte 預測誤差；causal mask 不允許偷看未來。
3. **Backward**：依 loss 對參數求梯度；這還沒有完成參數更新。
4. **Optimizer step**：AdamW 用梯度與 optimizer state 更新參數；下一步之前也要處理前次梯度。

本次 batch 表示每步的序列數，sequence length=256。batch 8 每步處理 2,048 byte tokens，batch 16 為 4,096；即使每步時間从 18.50 ms 變成 20.39 ms，單位時間處理量仍可能上升。這不能證明品質較好，因為兩組每步看到的 token 數不同，也沒有 held-out 評估。

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 找 prepare、step、causal check，解釋更改後面 token 不應影響前面 logits。用報告中的差為零結果對照程式，而不是自己假設 mask 正確。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '54,77p' 'benchmark/gpu/causal_lm_benchmark.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week15/Day2-PyTorch-Training-Runtime.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
