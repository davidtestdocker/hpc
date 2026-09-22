<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](<../../../learning-guide.md#week9>)及[對應現行入口](<../../../runbooks/platform-bootstrap.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day7 - Terraform Multi Environment

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/main.tf](<../../../../terraform/environments/dev/main.tf>)
- [terraform/environments/dev/outputs.tf](<../../../../terraform/environments/dev/outputs.tf>)
- [terraform/environments/dev/providers.tf](<../../../../terraform/environments/dev/providers.tf>)
- [terraform/environments/dev/variables.tf](<../../../../terraform/environments/dev/variables.tf>)
- [terraform/environments/dev/versions.tf](<../../../../terraform/environments/dev/versions.tf>)
- [terraform/environments/prod/main.tf](<../../../../terraform/environments/prod/main.tf>)
- [terraform/environments/prod/outputs.tf](<../../../../terraform/environments/prod/outputs.tf>)
- [terraform/environments/prod/providers.tf](<../../../../terraform/environments/prod/providers.tf>)
- [terraform/environments/prod/variables.tf](<../../../../terraform/environments/prod/variables.tf>)
- [terraform/environments/prod/versions.tf](<../../../../terraform/environments/prod/versions.tf>)
- [terraform/environments/stage/main.tf](<../../../../terraform/environments/stage/main.tf>)
- [terraform/environments/stage/outputs.tf](<../../../../terraform/environments/stage/outputs.tf>)
- [terraform/environments/stage/providers.tf](<../../../../terraform/environments/stage/providers.tf>)
- [terraform/environments/stage/variables.tf](<../../../../terraform/environments/stage/variables.tf>)
- [terraform/environments/stage/versions.tf](<../../../../terraform/environments/stage/versions.tf>)

---

## 今日目標

- 完成 Terraform Multi Environment
- 建立 dev / stage / prod 環境
- 完成 Infrastructure Module 重用
- 完成 Terraform Sandbox 驗證
- 清除 Sandbox Infrastructure

---

# 今日成果

- 建立 dev / stage / prod 三套 Environment
- 共用 Compute Module
- 共用 Network Module
- 共用 Firewall Module
- 使用 terraform.tfvars 管理不同環境
- 完成 Multi Environment 驗證
- 完成 Terraform Sandbox Destroy

---

# 專案架構

```text
terraform/
├── environments/
│   ├── dev/
│   ├── stage/
│   └── prod/
│
└── modules/
    ├── compute/
    ├── network/
    └── firewall/
```

---

# Multi Environment

所有 Environment 共用：

- providers.tf
- versions.tf
- modules

不同的只有：

```text
terraform.tfvars
```

例如：

```text
dev
environment = dev

stage
environment = stage

prod
environment = prod
```

Infrastructure Code 不需要修改。

---

# Module 重用

同一個 Compute Module：

```text
modules/compute
```

可以建立：

```text
hpc-api-dev
hpc-api-stage
hpc-api-prod
```

完全不需修改 Module。

只需要：

```text
terraform.tfvars
```

提供不同參數。

---

# String Interpolation

Resource Name：

```text
hpc-${var.environment}-vpc
```

依照 Environment 自動產生：

```text
Dev

↓

hpc-dev-vpc

Stage

↓

hpc-stage-vpc

Prod

↓

hpc-prod-vpc
```

避免重複維護多份 Terraform Code。

---

# Terraform Sandbox

Week9 建立的 Infrastructure 僅用於：

- Compute Module 驗證
- Network Module 驗證
- Firewall Module 驗證
- Multi Environment 驗證

完成後：

```bash
terraform destroy
```

全部移除。

Sandbox 不保留至正式專案。

---

# 為什麼要 Destroy？

Sandbox VM：

```text
hpc-api-dev
```

不承擔任何正式服務。

持續保留只會增加 GCP 成本。

正式 Infrastructure 將於後續建立：

```text
hpc-control-plane
hpc-worker-01
```

一路使用到專案完成。

---

# 驗證

```bash
terraform fmt -recursive

terraform validate

terraform plan
```

三個 Environment：

- dev
- stage
- prod

皆驗證成功。

最後：

```bash
terraform destroy
```

成功移除 Sandbox Infrastructure。

---

# Week9 完成成果

完成 Terraform Foundation：

- Provider
- Variables
- Outputs
- State
- Compute Module
- Network Module
- Firewall Module
- Module Output
- Resource Reference
- Multi Environment
- Sandbox Lifecycle

---

# Interview Q&A

### Q1：Terraform Module 的主要目的？

將 Infrastructure 封裝成可重複使用元件，提高重用性、降低重複程式碼，並統一管理不同環境。

---

### Q2：為什麼要使用 dev / stage / prod？

三個環境共用同一份 Terraform Code，只透過不同 `terraform.tfvars` 管理不同設定，避免維護多份 Infrastructure。

---

### Q3：為什麼 Week9 最後要 `terraform destroy`？

Week9 建立的是 Terraform Sandbox，用來驗證 Module 與 Infrastructure。正式專案將重新建立真正使用的 Kubernetes 節點，因此 Sandbox 應拆除以降低成本。

---

# 本週總結

完成 Terraform Foundation，具備企業常見的 Module 化架構與 Multi Environment 管理能力，能透過同一套 Infrastructure Code 部署不同環境，並理解 State、Module、Output 與 Resource Reference 的關係。Week9 完成後，Terraform 已具備支撐後續 Kubernetes、CI/CD 與 GitOps 的基礎。
