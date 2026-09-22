<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day2 — HCL 與輸入驗證

[上一課](<Day1-Terraform.md>) · [本週目錄](README.md) · [下一課](<Day3-Terraform-Apply-State-Resource-Lifecycle.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

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

## 已有結果與解讀

### CPU 叢集重建：已保存的驗收結果

日期：2026-09-21。環境：隔離 CPU-only GKE 重建驗收；不是主環境的多 GPU 實驗。該次叢集已清理，讀這份結果不需要重新建立。

```json
{
  "recorded_at": "2026-09-21",
  "scope": "fresh CPU-only GKE bootstrap and platform acceptance; excludes GPU and MPI execution",
  "result": "pass",
  "terraform": {
    "apply": "3 added",
    "post_apply_plan": "No changes",
    "destroy": "3 destroyed",
    "state_resources_after_destroy": 0,
    "cluster_lookup_after_destroy": "404 Not Found"
  },
  "controllers": {
    "jobset": "v0.12.0 Ready on system-pool with 100m CPU request",
    "kueue": "v0.19.2 Ready on system-pool with Recreate deployment strategy"
  },
  "platform": {
    "api": "Running on system-pool; /health healthy",
    "redis": "Running on system-pool; connected; PVC Bound",
    "postgres": "Running on system-pool; jobs table query succeeded; PVC Bound",
    "overlay_diff_after_apply": "empty"
  },
  "security": {
    "postgres_secret": "created from external env file; value not captured",
    "mpi_ssh_key": "generated in temporary directory; value not captured",
    "api_service_account_create_jobsets": "yes",
    "api_service_account_delete_pods": "no"
  },
  "limitations": [
    "gpu-pool had zero nodes because project-wide GPU quota was exhausted",
    "no MPI workload was submitted in this CPU-only rehearsal",
    "database initialization used create_all rather than schema migration"
  ]
}
```

解讀：Terraform 建立 3 個資源、無 drift，JobSet／Kueue controllers 和 API／Redis／DB 驗收成功；create JobSet 權限允許，delete Pod 權限拒絕。最後 destroy 3、state 空、cluster 查詢 404，證明當次隔離叢集已刪除。**不包含 GPU 或 MPI 執行驗收**，也不是所有雲端資源的停費證明。

來源：[原始 CPU bootstrap JSON](<../evidence/cpu-bootstrap-acceptance-20260921.json>)。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day2-Terraform-Language-Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day2 - Terraform Language Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/main.tf](../../terraform/environments/dev/main.tf)
- [terraform/environments/dev/variables.tf](../../terraform/environments/dev/variables.tf)
- [terraform/modules/compute/main.tf](../../terraform/modules/compute/main.tf)
- [terraform/modules/compute/outputs.tf](../../terraform/modules/compute/outputs.tf)
- [terraform/modules/compute/variables.tf](../../terraform/modules/compute/variables.tf)

---

## 學習目標

理解 Terraform Language 的核心概念。

今天重點不是建立 VM，而是理解 Terraform 如何透過 Resource、Variable、Plan 與 State 管理 Infrastructure。

---

# 完成成果

✅ Resource

✅ Google Compute Instance

✅ Variable

✅ terraform.tfvars

✅ Terraform Plan

✅ Terraform State（Concept）

---

# Terraform Resource

Terraform 所有 Infrastructure 都以 Resource 為核心。

例如：

```hcl
resource "google_compute_instance" "api" {

}
```

Resource 由三個部分組成：

```
resource

↓

google_compute_instance

↓

api
```

resource

代表：

建立 Infrastructure。

google_compute_instance

代表：

Google Cloud VM Resource。

api

代表：

Terraform Logical Name。

注意：

```
api
```

不是 GCP VM 名稱。

真正 VM 名稱：

```
name = "hpc-api-dev"
```

---

# Resource Schema

建立 VM 時，

Terraform Provider 定義了 Resource Schema。

例如：

```
name

machine_type

boot_disk

network_interface
```

都是必要欄位。

如果缺少：

```
terraform validate
```

會失敗。

因此：

Terraform 不只檢查：

```
Syntax
```

也會檢查：

```
Provider Schema
```

---

# Terraform Variable

Provider：

```
project = var.project_id
```

Variable：

```
variable "project_id"
```

作用：

讓程式不要寫死。

例如：

不要：

```
project = "project-xxxx"
```

而是：

```
project = var.project_id
```

不同環境：

```
dev

stage

prod
```

只需提供不同 Variable。

程式完全不用修改。

---

# terraform.tfvars

建立：

```
terraform.tfvars
```

內容：

```hcl
project_id = "project-4b82f780-0a12-4087-b94"
```

Terraform：

執行：

```
terraform plan
```

時：

自動載入：

```
terraform.tfvars
```

因此：

不用每次：

```
Enter a value:
```

手動輸入。

---

# Terraform Workflow

目前流程：

```
main.tf

↓

variables.tf

↓

terraform.tfvars

↓

terraform plan
```

Variable：

由：

```
terraform.tfvars
```

提供。

---

# Terraform Plan

今天第一次執行：

```
terraform plan
```

得到：

```
Plan:

1 to add

0 to change

0 to destroy
```

代表：

Terraform 預計：

建立：

```
1 VM
```

注意：

Plan：

不會建立任何 Resource。

只是：

模擬：

```
如果 Apply

將會做什麼。
```

---

# Terraform State

Terraform 最重要概念：

```
terraform.tfstate
```

State：

就是：

Terraform 的記憶。

Terraform：

不是直接比較：

```
Code

↓

Cloud
```

真正流程：

```
Code

↓

State

↓

Cloud

↓

Diff
```

State：

記錄：

- Resource
- Resource ID
- Attributes
- Dependency

如果：

State 遺失。

Terraform：

不知道：

哪些 Infrastructure 是自己建立。

---

# Local State

目前：

```
terraform.tfstate
```

會存在：

```
terraform/environments/dev
```

稱為：

```
Local State
```

企業：

通常改用：

```
Remote State
```

例如：

- GCS
- S3
- Azure Blob

避免多人協作造成 State 衝突。

---

# Terraform Project Structure

目前：

```
terraform/

├── environments/
│   └── dev/
│       ├── versions.tf
│       ├── providers.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── main.tf
│
├── modules/
│
└── .gitignore
```

Terraform：

會自動讀取：

```
所有 *.tf
```

並合併成：

一個 Terraform Project。

---

# 驗證

Terraform：

```
terraform validate
```

結果：

```
Success! The configuration is valid.
```

Terraform：

```
terraform plan
```

結果：

```
Plan:

1 to add

0 to change

0 to destroy
```

Variable：

```
terraform.tfvars
```

成功自動載入。

---

# 本日重點

1.

Terraform Resource

描述 Infrastructure。

---

2.

Variable

避免寫死設定。

---

3.

terraform.tfvars

提供 Environment Configuration。

---

4.

Plan

只做預覽。

不修改 Infrastructure。

---

5.

State

是 Terraform 最重要的資料。

沒有 State，

Terraform 就不知道目前 Infrastructure 狀態。

---

# Interview Q&A

## Q1

Terraform 的 Resource 是什麼？

Resource 是 Terraform 描述 Infrastructure 的基本單位，例如 VM、Network、Firewall、Disk 等都屬於 Resource。

---

## Q2

Variable 與 terraform.tfvars 有什麼差別？

Variable 用來宣告輸入介面；terraform.tfvars 則提供實際值，讓不同環境能使用相同 Terraform 程式。

---

## Q3

terraform plan 做了什麼？

Terraform 會比較 Code、State 與實際 Infrastructure，計算即將新增、修改或刪除哪些 Resource，但不會真正執行任何變更。

---

## Q4

Terraform State 是什麼？

State 是 Terraform 的記憶，記錄 Terraform 建立與管理的 Infrastructure 狀態，供後續 Plan、Apply、Destroy 比對使用。

---

# 本日總結

今天完成 Terraform Language Foundation，理解 Resource、Variable、terraform.tfvars、Plan 與 State 的角色，建立了 Terraform 最重要的核心觀念，為後續建立真正的 GCP Infrastructure 做好準備。
