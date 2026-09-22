<!-- current-curriculum: 2026-09-22 -->
# Week16 Day1 — 多 GPU 基本概念與單卡限制

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-pytorch-ddp.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「多 GPU 基本概念與單卡限制」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

資料平行每个 rank 通常有自己的模型副本，模型平行把模型拆分；兩者通訊模式不同。time-sharing 不是新裝置，不能把四 shares 當成四個 CUDA device。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[runtime/pytorch/distributed_scaling.py](<../../runtime/pytorch/distributed_scaling.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))

    distributed = world_size > 1

    use_cuda = torch.cuda.is_available()

    if distributed:
        # 條件運算式 A if 條件 else B：GPU 選 NCCL，CPU 選 Gloo。
        backend = "nccl" if use_cuda else "gloo"
        # 初始化分散式通訊群組；torchrun 提供 rank、world size 與 rendezvous 環境。
        dist.init_process_group(backend=backend)

    rank = dist.get_rank() if distributed else 0

    if use_cuda:
        # 把本程序綁到 local_rank 對應的 GPU，避免同節點所有程序使用同一張卡。
        torch.cuda.set_device(local_rank)
        device = torch.device(f"cuda:{local_rank}")
    else:
        device = torch.device("cpu")

    backend = "nccl" if use_cuda else "gloo"

```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 distributed_scaling 的 local_rank 與 set_device，推演在只看得到一張 GPU 時開兩個 GPU ranks 的問題；CPU/Gloo 是流程替代，不是性能替代。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '23,46p' 'runtime/pytorch/distributed_scaling.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/README.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week16/day1-multi-gpu-fundamentals.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
