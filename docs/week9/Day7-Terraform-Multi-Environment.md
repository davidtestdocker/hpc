<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day7 — 多環境與隔離 state

[上一課](<Day6-Terraform-Network-Module.md>) · [本週目錄](README.md) · [下一課](<Day8-GKE-Cluster-withTerraform.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

環境差異包含名字、位置、配額與 state；錯用 state 可把主資源當成要改名或刪除。remote state 尚未補齊，不可把隔離本機 state 說成團隊級鎖定流程。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/environments/gpu-sg/README.md](<../../terraform/environments/gpu-sg/README.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

````text
這個 root module 描述主展示叢集、system-pool 與 L4 gpu-pool。它使用獨立 state，不共用歷史 `environments/dev`。2026-09-21 的實測結果見 [Terraform 對齊證據](../../../docs/evidence/terraform-gpu-sg-20260921.md)。

## 管理邊界

- Terraform 管理 GKE cluster 與兩個 node pools。
- `default` VPC／subnet 是共享資源，只以 data source 讀取。
- Kubernetes controllers、queues、platform overlay 與 Secret 由
  [`scripts/bootstrap_cluster.py`](../../../scripts/bootstrap_cluster.py) 處理，不進入 Terraform state。
- 現有叢集不是由本 state 建立；必須先 import，不能直接 apply。

## 離線檢查

```bash
terraform -chdir=terraform/environments/gpu-sg init -backend=false
terraform -chdir=terraform/environments/gpu-sg fmt -check
terraform -chdir=terraform/environments/gpu-sg validate
```

## 匯入現有 hpc-gpu-sg

先建立 repo 外的 state backup 目錄，確認目前 root module 沒有 state，再依序匯入：

```bash
terraform -chdir=terraform/environments/gpu-sg import \
````

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day7-Terraform-Multi-Environment.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day7 - Terraform Multi Environment

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/main.tf](../../terraform/environments/dev/main.tf)
- [terraform/environments/dev/outputs.tf](../../terraform/environments/dev/outputs.tf)
- [terraform/environments/dev/providers.tf](../../terraform/environments/dev/providers.tf)
- [terraform/environments/dev/variables.tf](../../terraform/environments/dev/variables.tf)
- [terraform/environments/dev/versions.tf](../../terraform/environments/dev/versions.tf)
- [terraform/environments/prod/main.tf](../../terraform/environments/prod/main.tf)
- [terraform/environments/prod/outputs.tf](../../terraform/environments/prod/outputs.tf)
- [terraform/environments/prod/providers.tf](../../terraform/environments/prod/providers.tf)
- [terraform/environments/prod/variables.tf](../../terraform/environments/prod/variables.tf)
- [terraform/environments/prod/versions.tf](../../terraform/environments/prod/versions.tf)
- [terraform/environments/stage/main.tf](../../terraform/environments/stage/main.tf)
- [terraform/environments/stage/outputs.tf](../../terraform/environments/stage/outputs.tf)
- [terraform/environments/stage/providers.tf](../../terraform/environments/stage/providers.tf)
- [terraform/environments/stage/variables.tf](../../terraform/environments/stage/variables.tf)
- [terraform/environments/stage/versions.tf](../../terraform/environments/stage/versions.tf)

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
