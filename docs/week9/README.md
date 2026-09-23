# Week9 — Terraform：資源身分與建置生命週期

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week8](../week8/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

HCL 區塊宣告資源及輸入。var 讀輸入、resource 管理生命週期、data 讀既有資源、output 提供結果。module 是可重用組合，不是每個 root 都必須套同一模組。

State 記錄設定與遠端資源的映射；import 將既有資源納入管理，plan 比較期望與現況，apply 改變遠端資源。zero drift 只表示比較無變更，不等於應用程式健康。

現行 root 是 terraform/environments/gpu-sg；既有 dev root 與共享 VPC 不可隨意接管。隔離 rehearsal 必須同時隔離名字與 state，不能只換 cluster_name 就操作主 state。

## 目前環境與實測邊界

### HCL 先看三件事

```hcl
variable "example_count" {
  type    = number
  default = 1
}
```

這段只示範語法，不需要加進現行 root。`variable` 是區塊類型，字串是名稱，`{}` 是內容；`type` 和 `default` 是屬性。其他地方用 `var.example_count` 引用输入。真實的 `google_container_cluster.this.name` 則引用該資源的屬性，讓 Terraform 知道依賴關係。

與 YAML 比較：HCL 用區塊與 `=`，YAML 主要靠縮排和 `:`。兩者都是宣告資料／期望狀態；實際誰執行建立動作，取決於 Terraform provider 或 Kubernetes controller。

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

## 本週材料怎麼讀

- **Day1～Day2：Terraform 與 HCL** — [versions.tf](../../terraform/environments/dev/versions.tf) 看版本條件，[compute variables](../../terraform/modules/compute/variables.tf) 和 [compute main](../../terraform/modules/compute/main.tf) 看輸入如何用在資源宣告。
- **Day3～Day5：state、output、module** — 操作紀錄在各課正文；[compute outputs](../../terraform/modules/compute/outputs.tf) 可對照輸出如何引用資源。課文取消的 destroy、未 apply 的 plan 都保留原本結果。
- **Day6～Day7：網路與環境目錄** — [network module](../../terraform/modules/network/main.tf) 看 VPC／subnet；比較 [dev](../../terraform/environments/dev/main.tf)、[stage](../../terraform/environments/stage/main.tf)、[prod](../../terraform/environments/prod/main.tf) 的 module 呼叫，現在三者並非只有參數不同。
- **Day8：GKE 設定** — [GKE module](../../terraform/modules/gke/main.tf) 對應課文的叢集與 node pool；[gpu-sg root](../../terraform/environments/gpu-sg/main.tf) 是後來主環境的對照。Kubernetes 服務驗收 JSON 無法代替這些 Terraform 設定與生命週期紀錄。

## 每日閱讀順序

- [Day1：Terraform 的作用](<Day1-Terraform.md>)
- [Day2：HCL 與輸入驗證](<Day2-Terraform-Language-Foundation.md>)
- [Day3：State、import 與 lifecycle](<Day3-Terraform-Apply-State-Resource-Lifecycle.md>)
- [Day4：Outputs 與資源引用](<Day4-Terraform-Output-Resource-Reference.md>)
- [Day5：Module 與 root](<Day5-Terraform-Module-Refactor.md>)
- [Day6：VPC 與 subnet](<Day6-Terraform-Network-Module.md>)
- [Day7：多環境與隔離 state](<Day7-Terraform-Multi-Environment.md>)
- [Day8：GKE 到 CPU bootstrap](<Day8-GKE-Cluster-withTerraform.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
