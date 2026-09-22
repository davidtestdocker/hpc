<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day6 — VPC 與 subnet

[上一課](<Day5-Terraform-Module-Refactor.md>) · [本週目錄](README.md) · [下一課](<Day7-Terraform-Multi-Environment.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

network/subnetwork data source 讀共享網路，避免讓此 demo root 擁有並刪除共享資源。VPC、subnet、Pod IP ranges 是不同層；private/public 路由不能只從名字猜。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/environments/gpu-sg/main.tf](<../../terraform/environments/gpu-sg/main.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
  networking_mode = "VPC_NATIVE"

  # 空 block 讓 GKE 在既有 subnet 上配置 alias IP ranges。
  # 匯入現有 hpc-gpu-sg 時，provider 會從 state 保留實際 range 名稱。
  ip_allocation_policy {}

  # 對應現有叢集：Shielded Nodes、NodeLocal DNS 與 PD CSI driver。
  enable_shielded_nodes = true

  addons_config {
    dns_cache_config {
      enabled = true
    }

    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    network_policy_config {
      disabled = !var.enable_network_policy
    }

    node_readiness_config {
      enabled = false
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day6-Terraform-Network-Module.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day6 - Terraform Network Module

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/main.tf](../../terraform/environments/dev/main.tf)
- [terraform/modules/firewall/main.tf](../../terraform/modules/firewall/main.tf)
- [terraform/modules/firewall/outputs.tf](../../terraform/modules/firewall/outputs.tf)
- [terraform/modules/firewall/variables.tf](../../terraform/modules/firewall/variables.tf)
- [terraform/modules/network/main.tf](../../terraform/modules/network/main.tf)
- [terraform/modules/network/outputs.tf](../../terraform/modules/network/outputs.tf)
- [terraform/modules/network/variables.tf](../../terraform/modules/network/variables.tf)

---

## 今日目標

- 建立 Network Module
- 建立 Firewall Module
- 建立自訂 VPC 與 Subnet
- 理解 Module Output 串接
- 完成 Compute 與 Network Module 整合

---

# 今日成果

- 建立 `modules/network`
- 建立 `modules/firewall`
- 建立自訂 VPC
- 建立自訂 Subnet
- 建立 Firewall Rule
- Compute Module 成功引用 Network Module Output
- 完成 Infrastructure Module 串接

---

# 專案架構

```text
terraform/
├── environments/
│   ├── dev/
│   ├── stage/
│   └── prod/
└── modules/
    ├── compute/
    ├── network/
    └── firewall/
```

---

# Network Module

建立企業常用的 Custom VPC。

Terraform：

```text
Root Module
        │
        ▼
Network Module
        │
        ├── VPC
        └── Subnet
```

不再使用 GCP 預設 `default` Network。

---

# Firewall Module

建立獨立 Firewall Module。

目前開放：

- TCP 22（SSH）
- TCP 8000（API）

Firewall 與 Compute 完全解耦，可獨立維護。

---

# Module Output

Network Module 對外提供：

```text
network_id
network_self_link
subnet_id
subnet_self_link
```

Compute Module 不直接存取：

```text
google_compute_network.this.id
```

而是透過：

```text
module.network.network_id
```

取得 Network 資訊。

---

# Module 串接

資料流：

```text
terraform.tfvars
        │
        ▼
Root Module
        │
        ▼
Network Module
        │
        ▼
Output
        │
        ▼
Compute Module
        │
        ▼
google_compute_instance
```

Module 之間只透過 Output 傳遞資料，不直接存取彼此 Resource。

---

# Output 的用途

Output 並不只是：

```bash
terraform output
```

顯示資訊。

真正用途：

```text
Module Return Value
```

提供其他 Module 使用。

可理解成：

```text
variables.tf

↓

Function Parameter

main.tf

↓

Function Body

outputs.tf

↓

Return
```

---

# 驗證

```bash
terraform fmt -recursive

terraform validate

terraform plan
```

Plan：

```text
Network
Subnet
Firewall
```

均建立成功。

---

# 今日重點

- Module 是 Terraform 的可重複使用元件。
- Output 是 Module 對外公開的介面（API）。
- Compute 不應直接依賴 Network Resource，而應依賴 Network Module Output。
- VPC、Subnet、Firewall 應獨立封裝成 Module，提高可維護性。

---

# Interview Q&A

### Q1：Terraform Output 的主要用途是什麼？

Output 不只是提供 `terraform output` 查詢，更重要的是作為 Module 的回傳值，使其他 Module 能透過 `module.xxx.output_name` 取得資料。

---

### Q2：為什麼 Compute 不直接引用 `google_compute_network.this.id`？

因為 Resource 被封裝在 Network Module 內部，外部應透過 Output 存取，降低 Module 間耦合，提高重用性。

---

### Q3：企業為什麼會建立自己的 VPC，而不是使用 default？

為了隔離不同環境（dev、stage、prod）、自行管理 Firewall、Subnet 與未來 Kubernetes、GPU、Storage 等 Infrastructure，企業通常採用 Custom VPC。

---

# 本日總結

今天完成 Terraform Network Layer，建立可重複使用的 Network 與 Firewall Module，並成功透過 Output 串接 Compute Module。Terraform 專案開始具備企業常見的分層架構，為後續 Multi Environment 及 Kubernetes Infrastructure 奠定基礎。

---

# 下一步

完成 Terraform Multi Environment（dev / stage / prod），並整理整體 Terraform 專案架構，完成 Week9。
