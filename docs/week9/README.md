# Week9 — Terraform：資源身分與建置生命週期

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week8](../week8/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

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

[本週實作／證據入口](<../evidence/cpu-bootstrap-acceptance-20260921.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：Terraform 的作用](<Day1-Terraform.md>)
- [Day2：HCL 與輸入驗證](<Day2-Terraform-Language-Foundation.md>)
- [Day3：State、import 與 lifecycle](<Day3-Terraform-Apply-State-Resource-Lifecycle.md>)
- [Day4：Outputs 與資源引用](<Day4-Terraform-Output-Resource-Reference.md>)
- [Day5：Module 與 root](<Day5-Terraform-Module-Refactor.md>)
- [Day6：VPC 與 subnet](<Day6-Terraform-Network-Module.md>)
- [Day7：多環境與隔離 state](<Day7-Terraform-Multi-Environment.md>)
- [Day8：GKE 到 CPU bootstrap](<Day8-GKE-Cluster-withTerraform.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
