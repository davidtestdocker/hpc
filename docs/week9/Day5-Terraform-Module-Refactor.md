# Week9 Day5 - Terraform Module Refactor

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
