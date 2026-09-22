<!-- current-curriculum: 2026-09-22 -->
# Week9 Day5 — Module 與 root

[上一課](<Day4-Terraform-Output-Resource-Reference.md>) · [本週目錄](README.md) · [下一課](<Day6-Terraform-Network-Module.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Module 與 root」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

module 抽象可重用設定，root 組合環境配置與 provider。本 repo 舊 dev 用共用 modules，現行 gpu-sg 直接描述已匯入資源，兩者不可當作同一 state 的不同名字。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/modules/gke/main.tf](<../../terraform/modules/gke/main.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
resource "google_container_cluster" "this" {

  name     = var.cluster_name
  location = var.zone

  project = var.project_id

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false

  initial_node_count = 1

  remove_default_node_pool = true
}

# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
resource "google_container_node_pool" "primary" {

  name     = "primary-pool"
  project  = var.project_id
  location = var.zone

```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 比較舊 modules/gke 和新 gpu-sg/main.tf 的 pool 名稱與資源地址；解釋重構地址為何需要 state 遷移規劃。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '10,33p' 'terraform/modules/gke/main.tf'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/cpu-bootstrap-acceptance-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week9/Day5-Terraform-Module-Refactor.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
