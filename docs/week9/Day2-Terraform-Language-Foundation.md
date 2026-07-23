# Week9 Day2 - Terraform Language Foundation

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
