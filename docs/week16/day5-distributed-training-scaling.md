<!-- current-curriculum: 2026-09-22 -->
# Week16 Day5 — Distributed scaling

[上一課](<day4-nccl-communication-benchmark.md>) · [本週目錄](README.md) · [下一週](../week17/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Distributed scaling」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

總 batch 與每 rank batch 關係會改變運算量；同機 CPU workers 共享核心與記憶體，增加 workers 可能更慢。profiler 可找同步開銷，但控制條件先要成立。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[runtime/pytorch/distributed_scaling.py](<../../runtime/pytorch/distributed_scaling.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
from torch.utils.data.distributed import DistributedSampler


# 程式主要流程；檔案直接執行時由最下方入口呼叫。
def main():
    # torchrun provides distributed environment variables.
    # os.environ.get 讀取 torchrun 提供的環境變數；int 把字串轉成整數。
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
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 distributed_scaling 的 sampler、batch_size、world_size，說明比較 1→2 workers 必須固定哪些條件；不要拿此 CPU 結果推估多 GPU 效率。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '16,39p' 'runtime/pytorch/distributed_scaling.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/README.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week16/day5-distributed-training-scaling.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
