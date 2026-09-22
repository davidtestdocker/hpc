<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day5 — Module 與 root

[上一課](<Day4-Terraform-Output-Resource-Reference.md>) · [本週目錄](README.md) · [下一課](<Day6-Terraform-Network-Module.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day5-Terraform-Module-Refactor.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day5 - Terraform Module Refactor

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/main.tf](../../terraform/environments/dev/main.tf)
- [terraform/modules/compute/main.tf](../../terraform/modules/compute/main.tf)
- [terraform/modules/compute/outputs.tf](../../terraform/modules/compute/outputs.tf)
- [terraform/modules/compute/variables.tf](../../terraform/modules/compute/variables.tf)

---

## 今日目標

- 建立第一個 Terraform Module
- 理解 Root Module 與 Child Module
- 將 Compute Instance 重構為 Module
- 完成 State Migration，避免 VM 重建

---

# 今日成果

- 建立 `modules/compute`
- 完成 Module Input（variables）
- 完成 Module Output（outputs）
- Root Module 成功呼叫 Compute Module
- 完成 `terraform state mv`
- `terraform plan` 顯示 **No changes**
- 驗證同一 Module 可重複建立多台 VM

---

# 專案架構

```text
terraform/
├── environments/
│   ├── dev/
│   ├── stage/
│   └── prod/
└── modules/
    └── compute/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

- `environments/dev`：Root Module
- `modules/compute`：Child Module

---

# Root Module

Root Module 負責：

- Environment 設定
- 呼叫 Module
- 管理 Terraform State

```hcl
module "api" {
  source = "../../modules/compute"

  name         = "hpc-api-dev"
  machine_type = "e2-medium"
  zone         = var.zone
  image        = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
  network      = "default"
}
```

---

# Child Module

Child Module 封裝 VM 建立邏輯。

```hcl
resource "google_compute_instance" "this" {
    ...
}
```

所有 Compute VM 共用同一份程式。

---

# Module 資料流

```text
terraform.tfvars
        │
        ▼
Root Module Variable
        │
        ▼
module "api"
        │
        ▼
Child Module Variable
        │
        ▼
google_compute_instance.this
```

Child Module 不會直接讀取 `terraform.tfvars`，所有設定都由 Root Module 傳入。

---

# State Migration

重構前：

```text
google_compute_instance.api
```

重構後：

```text
module.api.google_compute_instance.this
```

為避免 Terraform 誤判需要重建 VM：

```bash
terraform state mv \
'google_compute_instance.api' \
'module.api.google_compute_instance.this'
```

完成後：

```bash
terraform plan
```

結果：

```text
No changes.
```

代表：

- VM 未重建
- State 已完成搬移
- Module Refactor 成功

---

# Module Reuse

新增：

```hcl
module "worker" {
    source = "../../modules/compute"
    ...
}
```

執行：

```bash
terraform plan
```

結果：

```text
module.worker.google_compute_instance.this will be created

Plan: 1 to add, 0 to change, 0 to destroy.
```

證明同一份 Compute Module 可重複建立不同 VM。

本次僅驗證 Plan，未 Apply。

---

# 驗證

```bash
terraform state list
```

結果：

```text
module.api.google_compute_instance.this
```

```bash
terraform plan
```

結果：

```text
No changes.
```

---

# 今日重點

- Module 將 Infrastructure 封裝成可重複使用元件。
- Root Module 負責組合 Module。
- Child Module 負責 Resource 實作。
- Resource Address 改變時，需使用 `terraform state mv` 遷移 State，而不是重新建立 Infrastructure。

---

# Interview Q&A

### Q1：Root Module 與 Child Module 差異？

Root Module 是 Terraform 執行入口，負責組合 Module、管理 Environment 與 State；Child Module 封裝可重複使用的 Infrastructure。

---

### Q2：為什麼 Module Refactor 後 Terraform 會想重建 VM？

因為 Resource Address 從：

```text
google_compute_instance.api
```

變成：

```text
module.api.google_compute_instance.this
```

Terraform 依照 Address 管理 Resource，因此需要搬移 State。

---

### Q3：`terraform state mv` 的用途？

修改 Terraform State 中 Resource 的 Address，使重構後的程式能繼續管理既有 Infrastructure，而不需重建 Resource。

---

# 本日總結

今天完成 Terraform Module 化，成功將 Compute Resource 從 Root Module 重構為 Child Module，並利用 `terraform state mv` 保留既有 VM，不造成任何 Infrastructure 重建，建立了符合企業實務的 Terraform 專案架構。

---

# 下一步

建立真正的 Multi Environment（dev / stage / prod），讓三個環境共用同一份 Compute Module，並使用不同參數管理各自的 Infrastructure。
