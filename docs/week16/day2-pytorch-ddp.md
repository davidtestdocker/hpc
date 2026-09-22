<!-- current-curriculum: 2026-09-22 -->
# Week16 Day2 — CPU／Gloo DDP

[上一課](<day1-multi-gpu-fundamentals.md>) · [本週目錄](README.md) · [下一課](<day3-nccl-fundamentals.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「CPU／Gloo DDP」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

torchrun 提供 rank 等環境變數，init_process_group 建立群組，DistributedSampler 分資料。DDP 同步梯度不會替你自動正確切資料或定義公平比較。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[runtime/pytorch/ddp_test.py](<../../runtime/pytorch/ddp_test.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    dist.init_process_group(backend="gloo")

    # torchrun automatically provides these distributed environment values.
    # rank 是全群組程序編號，world_size 是程序總數，local_rank 是本節點內編號。
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    local_rank = int(os.environ["LOCAL_RANK"])

    # Create a simple model.
    # Each DDP worker owns its own model replica.
    # 線性層把輸入特徵轉為指定輸出維度，包含可訓練權重與偏差。
    model = torch.nn.Linear(4, 1)

    # Wrap the model with DistributedDataParallel.
    # DDP automatically synchronizes gradients during backward().
    # DDP 包装本機模型副本，初始化時同步參數，backward 時同步梯度。
    model = DDP(model)

    # Create local input data for this worker.
    # Different workers may process different data,
    # so their local loss values do not need to be identical.
    # randn 產生標準常態隨機張量；此處每個 worker 各自產生 8 筆、每筆 4 個特徵。
    x = torch.randn(8, 4)
    y = torch.randn(8, 1)
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 DDP 測試的 backend 與參數同步檢查，說明 checksum 一致能證明什麼、不能證明什麼；本課不在 L4 主環境啟動假多卡。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '15,38p' 'runtime/pytorch/ddp_test.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/README.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week16/day2-pytorch-ddp.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
