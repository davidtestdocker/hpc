<!-- current-curriculum: 2026-09-22 -->
# Week9 Day7 — 多環境與隔離 state

[上一課](<Day6-Terraform-Network-Module.md>) · [本週目錄](README.md) · [下一課](<Day8-GKE-Cluster-withTerraform.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「多環境與隔離 state」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

環境差異包含名字、位置、配額與 state；錯用 state 可把主資源當成要改名或刪除。remote state 尚未補齊，不可把隔離本機 state 說成團隊級鎖定流程。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/environments/gpu-sg/README.md](<../../terraform/environments/gpu-sg/README.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

````text
這個 root module 描述主展示叢集、system-pool 與 L4 gpu-pool。它使用獨立 state，不共用歷史 `environments/dev`。2026-09-21 的實測結果見 [Terraform 對齊證據](../../../docs/evidence/terraform-gpu-sg-20260921.md)。

## 管理邊界

- Terraform 管理 GKE cluster 與兩個 node pools。
- `default` VPC／subnet 是共享資源，只以 data source 讀取。
- Kubernetes controllers、queues、platform overlay 與 Secret 由
  [`scripts/bootstrap_cluster.py`](../../../scripts/bootstrap_cluster.py) 處理，不進入 Terraform state。
- 現有叢集不是由本 state 建立；必須先 import，不能直接 apply。

## 離線檢查

```bash
terraform -chdir=terraform/environments/gpu-sg init -backend=false
terraform -chdir=terraform/environments/gpu-sg fmt -check
terraform -chdir=terraform/environments/gpu-sg validate
```

## 匯入現有 hpc-gpu-sg

先建立 repo 外的 state backup 目錄，確認目前 root module 沒有 state，再依序匯入：

```bash
terraform -chdir=terraform/environments/gpu-sg import \
````

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 gpu-sg README 的 rehearsal 說明，列出開始前必核對的 project、cluster_name、state、quota 四項；不執行 destroy。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '3,26p' 'terraform/environments/gpu-sg/README.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/cpu-bootstrap-acceptance-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week9/Day7-Terraform-Multi-Environment.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
