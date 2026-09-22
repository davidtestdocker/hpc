<!-- current-curriculum: 2026-09-22 -->
# Week9 Day3 — State、import 與 lifecycle

[上一課](<Day2-Terraform-Language-Foundation.md>) · [本週目錄](README.md) · [下一課](<Day4-Terraform-Output-Resource-Reference.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「State、import 與 lifecycle」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

import 是納入既有資源身分，不是複製一份 cluster。ForceNew 欄位差異可能引發重建，ignore_changes 是有意忽略部分漂移，不能當全面安全保證。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/environments/gpu-sg/main.tf](<../../terraform/environments/gpu-sg/main.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
  lifecycle {
    # 匯入時 API 會回報 initial_node_count=0；它只用於建立暫時的 default pool。
    # 忽略這個 ForceNew 欄位可避免 Terraform 誤判整個現有叢集需要重建。
    ignore_changes = [initial_node_count, min_master_version, remove_default_node_pool]
  }
}

locals {
  # 與現有 GKE Standard node pools 相同的最小 OAuth scopes。
  node_oauth_scopes = [
    "https://www.googleapis.com/auth/devstorage.read_only",
    "https://www.googleapis.com/auth/logging.write",
    "https://www.googleapis.com/auth/monitoring",
    "https://www.googleapis.com/auth/service.management.readonly",
    "https://www.googleapis.com/auth/servicecontrol",
    "https://www.googleapis.com/auth/trace.append",
  ]
}

resource "google_container_node_pool" "system" {
  name     = "system-pool"
  project  = var.project_id
  location = var.zone
  cluster  = google_container_cluster.this.name
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 找 lifecycle 的 ignore_changes 與 deletion_protection；說明 plan 出現 replace 時應停下檢查，而不是直接 apply。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '63,86p' 'terraform/environments/gpu-sg/main.tf'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/cpu-bootstrap-acceptance-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week9/Day3-Terraform-Apply-State-Resource-Lifecycle.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
