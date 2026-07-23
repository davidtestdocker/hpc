# Week9 Day1 - Terraform Foundation

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
