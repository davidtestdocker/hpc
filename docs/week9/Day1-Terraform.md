<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day1 — Terraform 的作用

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-Terraform-Language-Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day1-Terraform.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day1 - Terraform Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/.terraform.lock.hcl](../../terraform/environments/dev/.terraform.lock.hcl)
- [terraform/environments/dev/providers.tf](../../terraform/environments/dev/providers.tf)
- [terraform/environments/dev/versions.tf](../../terraform/environments/dev/versions.tf)

---

## 學習目標

正式開始 Infrastructure as Code（IaC）。

理解 Terraform 的定位、Workflow、Provider 機制，建立第一個 Terraform 專案架構，並完成 Terraform 開發環境初始化。

另外完成 GCP VM 第二顆 Data Disk 初始化，建立後續 Infrastructure 與 Benchmark Data 的儲存空間。

---

# 完成成果

✅ Terraform v1.15.8

✅ HashiCorp Official Repository

✅ Terraform Project Structure

✅ Terraform Initialization

✅ Google Provider

✅ Provider Plugin Download

✅ Terraform Lock File

✅ Linux Data Disk

✅ ext4 Filesystem

✅ /data Mount

---

# Terraform 是什麼？

Terraform 是一套 Infrastructure as Code（IaC）工具。

目的不是管理程式，而是管理：

- VM
- VPC
- Firewall
- GKE
- Artifact Registry
- IAM
- Disk

也就是：

```
Infrastructure

↓

Code

↓

Version Control

↓

Automatic Provisioning
```

---

# Terraform Workflow

Terraform 每次工作都遵循固定流程：

```
terraform init

↓

terraform validate

↓

terraform plan

↓

terraform apply

↓

terraform destroy
```

各指令職責：

| Command | 功能 |
|----------|------|
| init | 初始化 Terraform 專案 |
| validate | 驗證 Terraform 語法 |
| plan | 預覽即將修改的 Infrastructure |
| apply | 建立或更新 Infrastructure |
| destroy | 移除 Infrastructure |

---

# Terraform Project Structure

```
terraform/

├── environments/
│   ├── dev/
│   ├── stage/
│   └── prod/
│
├── modules/
│
└── .gitignore
```

環境（Environment）

負責：

```
dev

stage

prod
```

Module

負責：

```
Reusable Infrastructure
```

例如：

- VM
- VPC
- Firewall

未來都會拆成 Module。

---

# Terraform Configuration

目前建立：

```
versions.tf
```

內容：

```
terraform {

  required_version = ">= 1.15.0"

}
```

作用：

限制 Terraform CLI 最低版本。

避免：

```
Developer A

Terraform 1.15

Developer B

Terraform 0.14
```

導致不同結果。

---

建立：

```
providers.tf
```

內容：

```
terraform {

  required_providers {

    google = {

      source = "hashicorp/google"

      version = "~> 7.0"

    }

  }

}

provider "google" {

  project = "YOUR_PROJECT_ID"

  region  = "asia-east1"

  zone    = "asia-east1-a"

}
```

Terraform：

負責管理 Terraform 本身。

Provider：

負責與 Google Cloud API 溝通。

---

# terraform init

第一次：

只有：

```
versions.tf
```

沒有 Provider。

因此：

```
terraform init
```

沒有下載任何內容。

加入：

```
provider "google"
```

後：

再次執行：

```
terraform init
```

Terraform：

下載 Google Provider。

建立：

```
.terraform/

.terraform.lock.hcl
```

---

# .terraform

```
.terraform/

↓

Provider Plugin
```

作用：

存放 Provider。

例如：

```
Google Provider

AWS Provider

Azure Provider
```

等同於：

Python：

```
.venv
```

Node.js：

```
node_modules
```

Git：

```
×

不要提交
```

---

# .terraform.lock.hcl

作用：

鎖定 Provider Version。

例如：

```
hashicorp/google

7.x.x
```

所有人：

```
terraform init
```

都會下載相同版本。

Git：

```
✓

需要提交
```

作用等同：

```
package-lock.json

poetry.lock

go.sum
```

---

# Linux Data Disk

新增：

```
100G Persistent Disk
```

初始化流程：

```
Disk

↓

Partition

↓

Filesystem

↓

Mount

↓

fstab
```

完成：

```
/dev/sdb1

↓

ext4

↓

/data
```

驗證：

```
findmnt /data
```

結果：

```
/data

↓

/dev/sdb1
```

開機後自動掛載。

---

# Git

Terraform：

應加入 Git：

```
versions.tf

providers.tf

.terraform.lock.hcl
```

不應加入 Git：

```
.terraform/

*.tfstate

crash.log
```

因此建立：

```
terraform/.gitignore
```

---

# 驗證

Terraform：

```
terraform version
```

```
Terraform v1.15.8
```

初始化：

```
terraform init
```

成功下載：

```
Google Provider
```

Linux：

```
findmnt /data
```

```
/data

↓

/dev/sdb1
```

---

# 本日重點

1.

Terraform 管理 Infrastructure。

不是管理 Application。

---

2.

Terraform Workflow：

```
init

↓

validate

↓

plan

↓

apply

↓

destroy
```

---

3.

Provider

負責與 Cloud Provider 溝通。

---

4.

`.terraform`

存放 Provider。

不要加入 Git。

---

5.

`.terraform.lock.hcl`

鎖定 Provider Version。

需要加入 Git。

---

6.

新增 Data Disk 時，

Linux 標準流程：

```
Disk

↓

Partition

↓

Filesystem

↓

Mount

↓

fstab
```

---

# Interview Q&A

## Q1

Terraform 的 `terraform init` 做了哪些事情？

Terraform 會初始化工作目錄、下載所需 Provider、建立 `.terraform/` 目錄，以及產生 `.terraform.lock.hcl`，但不會建立任何 Infrastructure。

---

## Q2

`.terraform` 與 `.terraform.lock.hcl` 有什麼差別？

`.terraform/` 存放 Provider Plugin，屬於執行時依賴，不應提交 Git；`.terraform.lock.hcl` 用來鎖定 Provider 版本，確保團隊使用一致版本，因此應提交至 Git。

---

## Q3

Terraform Core 與 Provider 有什麼差別？

Terraform Core 負責解析 `.tf`、規劃執行流程；Provider 則負責呼叫雲端平台 API，例如 Google Cloud、AWS 或 Azure，真正建立或修改 Infrastructure。

---

# 本日總結

今天完成了 Terraform 開發環境初始化，理解 Terraform Core、Provider、Lock File 與 Git 管理方式，同時完成 Linux Data Disk 初始化，建立後續 Terraform、Benchmark 與 Infrastructure 的資料儲存空間。

正式進入 Infrastructure as Code 的第一天。
