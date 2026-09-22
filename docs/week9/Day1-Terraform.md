<!-- current-curriculum: 2026-09-22 -->
# Week9 Day1 — Terraform 的作用

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-Terraform-Language-Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Terraform 的作用」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

Terraform 管理 GKE cluster／node pools，平台 controller 與 API 部署另由 bootstrap／deploy 處理。IaC 不是把所有 kubectl 命令換個工具名稱，也不自動涵蓋應用健康。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/environments/gpu-sg/main.tf](<../../terraform/environments/gpu-sg/main.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
# default VPC／subnet 是專案共享資源；只以 data source 讀取，避免本環境接管或刪除它們。
data "google_compute_network" "selected" {
  name    = var.network_name
  project = var.project_id
}

data "google_compute_subnetwork" "selected" {
  name    = var.subnetwork_name
  project = var.project_id
  region  = var.region
}

resource "google_container_cluster" "this" {
  name     = var.cluster_name
  project  = var.project_id
  location = var.zone

  # 使用名稱交給 provider 正規化，與既有叢集匯入 state 的表示一致。
  network    = var.network_name
  subnetwork = var.subnetwork_name

  # GKE 建立暫時 default pool 後立即移除；正式 pools 由下方獨立資源管理。
  remove_default_node_pool = true
  initial_node_count       = 1
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 找 main.tf 的 data 與 resource，再對照 bootstrap 入口，畫出叢集建立和應用部署的分界。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '1,24p' 'terraform/environments/gpu-sg/main.tf'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/cpu-bootstrap-acceptance-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week9/Day1-Terraform.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
