<!-- current-curriculum: 2026-09-22 -->
# Week14 Day4 — GKE GPU pool

[上一課](<day3-gpu-monitoring-architecture.md>) · [本週目錄](README.md) · [下一課](<Day5-GPU-Metrics-Monitoring-integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「GKE GPU pool」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

gpu-pool 的機型、driver 設定、taint 和 sharing 構成 GPU node 的配置。max_shared_clients_per_gpu=4 是分享配置，gpu_node_count 和實體卡數才是硬體數量相關欄位。

## 在現在的專案中

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

本課對照：[terraform/environments/gpu-sg/main.tf](<../../terraform/environments/gpu-sg/main.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
    guest_accelerator {
      type  = "nvidia-l4"
      count = 1

      gpu_driver_installation_config {
        gpu_driver_version = "DEFAULT"
      }

      gpu_sharing_config {
        gpu_sharing_strategy       = "TIME_SHARING"
        max_shared_clients_per_gpu = 4
      }
    }

    # GKE 會在同時存在 CPU pool 時自動加入 nvidia.com/gpu=present:NoSchedule，
    # 並透過 effective_taints 回報；重複宣告 taint 會造成無效的匯入後 drift。

    shielded_instance_config {
      enable_integrity_monitoring = true
    }
  }
}
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 Terraform guest_accelerator 和 gpu_sharing_config，說明一張 L4／四個 share 與四張 L4 的差異；不為練習申請第二張 GPU。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '148,169p' 'terraform/environments/gpu-sg/main.tf'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../performance/causal-lm-l4-20260922.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week14/Day4-GKE-GPU-Node-Pool-GPU-Scheduling.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
