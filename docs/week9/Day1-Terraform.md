<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day1 — Terraform 的作用

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-Terraform-Language-Foundation.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史版本與掛載摘要。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

destroy 不是每次工作必須執行的最後一步；只在確定要移除目標資源時使用。init 還初始化 backend/modules，lock 主要鎖 provider，不等於鎖 CLI、全部 module 與雲端實況。主 root 是 gpu-sg，不是 dev。

## 程式／設定與來源

本次核對：[terraform/environments/dev/versions.tf](<../../terraform/environments/dev/versions.tf>)、[terraform/environments/dev/providers.tf](<../../terraform/environments/dev/providers.tf>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day1-Terraform.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Terraform v1.15.8
```

舊版本與 /data 掛載記載不代表今日環境；沒有 disk UUID／fstab／重開機證據，不應照舊 /dev/sdb 名稱格式化。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
