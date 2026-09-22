<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day3 — State、import 與 lifecycle

[上一課](<Day2-Terraform-Language-Foundation.md>) · [本週目錄](README.md) · [下一課](<Day4-Terraform-Output-Resource-Reference.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day3-Terraform-Apply-State-Resource-Lifecycle.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day3 - Terraform Apply & State

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/main.tf](../../terraform/environments/dev/main.tf)
- [terraform/modules/compute/main.tf](../../terraform/modules/compute/main.tf)

---

## 今日目標

今天正式使用 Terraform 建立第一個 Google Cloud Infrastructure，理解 Terraform 如何透過 `plan`、`apply`、`state` 與 `destroy` 管理整個 Infrastructure Lifecycle，而不是只會撰寫 Terraform HCL。

---

# 今日成果

- 完成第一台由 Terraform 管理的 GCP VM
- 理解 Terraform Resource Address
- 理解 Terraform State 的用途
- 理解 OAuth Scope 與 IAM Role 的差異
- 修正 GCP Service Account 權限問題
- 成功完成第一次 `terraform apply`
- 理解 `terraform destroy` 的工作流程

---

# Terraform Apply

今天第一次成功執行：

```bash
terraform apply
```

Terraform 會依照下列流程建立 Infrastructure：

```
Terraform Code

↓

Terraform Plan

↓

Google Provider

↓

Google Cloud API

↓

Create Infrastructure

↓

Update terraform.tfstate
```

建立完成後：

```
Apply complete!

Resources: 1 added
0 changed
0 destroyed
```

代表 Terraform 已成功管理第一個 Cloud Resource。

---

# Terraform Resource Address

建立 VM：

```hcl
resource "google_compute_instance" "api" {

}
```

其中：

```
google_compute_instance
```

代表 Resource Type。

```
api
```

代表 Terraform Logical Name。

真正建立到 GCP 的 VM 名稱則是：

```
hpc-api-dev
```

Terraform 內部永遠透過：

```
google_compute_instance.api
```

識別這個 Resource。

---

# Terraform State

成功 Apply 後，Terraform 自動建立：

```
terraform.tfstate
```

State 用來記錄：

- Terraform 管理哪些 Resource
- Resource ID
- Resource 屬性
- Infrastructure 目前狀態

透過：

```bash
terraform state list
```

確認目前管理：

```
google_compute_instance.api
```

State 是 Terraform 最重要的核心。

沒有 State，Terraform 就不知道哪些 Infrastructure 是自己建立的。

---

# OAuth Scope 與 IAM

今天實際遇到兩個 GCP 權限問題。

第一個：

```
ACCESS_TOKEN_SCOPE_INSUFFICIENT
```

原因：

VM 沒有：

```
cloud-platform
```

OAuth Scope。

修改 VM Access Scope 後成功解決。

第二個：

```
compute.instances.create
```

原因：

Service Account 沒有 Compute Engine IAM Role。

最後新增：

- Compute Instance Admin (v1)
- Service Account User

Terraform 成功建立 VM。

也理解：

OAuth Scope 與 IAM Role 是兩層不同的權限控制。

---

# Terraform Destroy

今天執行：

```bash
terraform destroy
```

Terraform 並沒有直接刪除 VM。

而是：

先產生 Destroy Plan：

```
Plan:

0 to add

0 to change

1 to destroy
```

等待輸入：

```
yes
```

才會真正刪除 Infrastructure。

今天使用：

```
Ctrl + C
```

取消，因此 VM 仍保留。

---

# 今日重點

Terraform 真正管理的是：

```
Terraform Code

↓

Terraform State

↓

Google Cloud
```

Terraform 並不是直接管理 Cloud。

所有變更都必須透過 State 計算差異後，再決定建立、修改或刪除 Infrastructure。

因此：

Terraform 管理的 Resource 不應直接透過 GCP Console 修改。

正確流程應為：

```
修改 Terraform Code

↓

terraform fmt

↓

terraform validate

↓

terraform plan

↓

terraform apply
```

---

# 驗證

成功建立 VM：

```
hpc-api-dev
```

Terraform：

```bash
terraform state list
```

結果：

```
google_compute_instance.api
```

成功產生：

```
terraform.tfstate

terraform.tfstate.backup
```

Terraform 已正式開始管理此 Infrastructure。

---

# Interview Q&A

## Q1：Terraform 的 Resource Address 是什麼？

Resource Address 是 Terraform 用來唯一識別 Resource 的名稱，由 Resource Type 與 Logical Name 組成，例如：

```
google_compute_instance.api
```

Terraform 會透過 Resource Address 管理、修改與刪除 Infrastructure，而不是依照 GCP 上的 VM 名稱。

---

## Q2：terraform plan 與 terraform apply 有什麼差別？

`terraform plan` 只會比較 Terraform Code、State 與實際 Infrastructure 的差異，產生預計變更內容，不會修改任何資源。

`terraform apply` 則會依照 Plan 呼叫 Cloud API，真正建立、修改或刪除 Infrastructure，並更新 terraform.tfstate。

---

## Q3：Terraform 管理的 VM 要修改規格時，正確流程是什麼？

不應直接到 GCP Console 修改，而是修改 Terraform HCL，依序執行：

```
terraform fmt

↓

terraform validate

↓

terraform plan

↓

terraform apply
```

Production 環境通常還會經過 Git、Pull Request、Code Review 與 CI/CD，確保所有 Infrastructure 變更都可追蹤、可回溯。

---

# 下一步

下一章將學習 Terraform Output 與 State 的進階使用方式，開始讓不同 Resource 之間互相引用，並逐步建立符合企業實務的 Terraform Project Structure。
