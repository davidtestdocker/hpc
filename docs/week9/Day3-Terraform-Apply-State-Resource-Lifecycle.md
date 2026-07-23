# Week9 Day3 - Terraform Apply & State

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
