<!-- current-curriculum: 2026-09-22 -->
# Week9 Day2 — HCL 與輸入驗證

[上一課](<Day1-Terraform.md>) · [本週目錄](README.md) · [下一課](<Day3-Terraform-Apply-State-Resource-Lifecycle.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「HCL 與輸入驗證」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

variable 的 type 和 validation 限制輸入，default 不表示適用所有環境。GPU node_count 設零可做 CPU-only rehearsal，但資源設計與驗收範圍也隨之不同。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/environments/gpu-sg/variables.tf](<../../terraform/environments/gpu-sg/variables.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
variable "gpu_node_count" {
  description = "Fixed number of L4 nodes; keep zero only for a CPU-only rehearsal"
  type        = number
  default     = 1

  validation {
    condition     = var.gpu_node_count >= 0
    error_message = "gpu_node_count cannot be negative."
  }
}

variable "gpu_spot" {
  description = "Use Spot VMs for an isolated GPU rehearsal; keep false for the main environment"
  type        = bool
  default     = false
}

# 主環境預設保護；不得為了照跑歷史 destroy 指令而關閉。
variable "deletion_protection" {
  description = "Protect the cluster from accidental Terraform deletion"
  type        = bool
  default     = true
}

```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 variables.tf 的 system_node_count、gpu_node_count、enable_network_policy，列出預設值與變更含義；不直接修改主環境 tfvars。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '50,73p' 'terraform/environments/gpu-sg/variables.tf'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/cpu-bootstrap-acceptance-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week9/Day2-Terraform-Language-Foundation.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
