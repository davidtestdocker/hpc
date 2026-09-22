<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day4 — Outputs 與資源引用

[上一課](<Day3-Terraform-Apply-State-Resource-Lifecycle.md>) · [本週目錄](README.md) · [下一課](<Day5-Terraform-Module-Refactor.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

output 引用實際管理資源屬性，可供後續取得 credentials 或 bootstrap。輸出 pool_name 不能推論現有 node 數、Ready 狀態或 GPU 可執行性。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[terraform/environments/gpu-sg/outputs.tf](<../../terraform/environments/gpu-sg/outputs.tf>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```hcl
output "cluster_name" {
  description = "Managed GKE cluster name"
  value       = google_container_cluster.this.name
}

output "cluster_location" {
  description = "Zonal location used by kubectl credential commands"
  value       = google_container_cluster.this.location
}

output "system_pool_name" {
  description = "CPU platform node pool"
  value       = google_container_node_pool.system.name
}

output "gpu_pool_name" {
  description = "L4 time-sharing node pool"
  value       = google_container_node_pool.gpu.name
}
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day4-Terraform-Output-Resource-Reference.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day4 - Terraform Output & Resource Reference

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

早期 VM output 已重構至 compute module；stage outputs 提供模組輸出的引用範例，dev 現況則偏向 GKE。

- [terraform/environments/stage/outputs.tf](../../terraform/environments/stage/outputs.tf)
- [terraform/modules/compute/main.tf](../../terraform/modules/compute/main.tf)
- [terraform/modules/compute/outputs.tf](../../terraform/modules/compute/outputs.tf)

---

## 今日目標

今天的目標是理解 Terraform 如何取得已建立 Resource 的資訊，並學會使用 Output 與 Resource Reference，讓不同 Resource 可以互相引用，而不需要將 IP、ID 或 Name 寫死在程式中。

今天也是第一次真正使用 Terraform State，而不是只有知道它的存在。

---

# 今日成果

- 完成 Terraform Output
- 理解 Resource Reference
- 理解 Resource Attribute
- 理解 Terraform State 如何提供資料
- 理解 Implicit Dependency（隱式依賴）
- 完成 VM Name、Zone、Machine Type、Internal IP Output

---

# Terraform Output

Terraform 可以將 Resource 的屬性輸出。

建立：

```hcl
output "vm_name" {
  description = "VM Name"
  value       = google_compute_instance.api.name
}
```

完成 Apply 後：

```bash
terraform output
```

輸出：

```
vm_name = "hpc-api-dev"
```

Output 並不是查詢 Google Cloud API，而是直接從 Terraform State 取得資料。

---

# Resource Reference

今天第一次使用 Terraform Resource Reference：

```hcl
google_compute_instance.api.name
```

結構如下：

```
google_compute_instance

↓

Resource Type

↓

api

↓

Logical Name

↓

name

↓

Attribute
```

Terraform 會依照 Resource Address 找到 Resource，再取得指定 Attribute。

除了 `name` 之外，還可以取得：

```text
machine_type

zone

id

self_link

network_interface

network_ip
```

---

# Resource Attribute

今天新增以下 Output：

```hcl
output "vm_internal_ip" {
  value = google_compute_instance.api.network_interface[0].network_ip
}

output "vm_machine_type" {
  value = google_compute_instance.api.machine_type
}
```

成功取得：

```
vm_internal_ip = "10.140.0.3"

vm_machine_type = "e2-medium"
```

代表 Terraform 可以直接引用 Resource 的屬性，而不需要人工查詢或手動填寫。

---

# Terraform State

今天真正開始使用：

```
terraform.tfstate
```

Terraform Output 的流程：

```
terraform output

↓

terraform.tfstate

↓

Outputs

↓

顯示結果
```

因此：

```bash
terraform output
```

不需要再次呼叫 Google Cloud API。

Terraform 已經將 Resource 的資訊保存於 State。

---

# Resource Reference 的價值

假設未來建立第二台 VM：

```hcl
resource "google_compute_instance" "database" {

}
```

如果需要 API VM 的 Internal IP，

錯誤方式：

```hcl
value = "10.140.0.3"
```

正確方式：

```hcl
value = google_compute_instance.api.network_interface[0].network_ip
```

Terraform 會自動取得目前 API VM 的最新 IP。

即使未來 VM 重建、IP 改變，也不需要修改任何程式碼。

---

# Implicit Dependency

Terraform 並不是依照檔案順序建立 Resource。

而是依照 Resource Reference 建立 Dependency。

例如：

```
Firewall

↓

引用

↓

API VM
```

Terraform 會自動推導：

```
API VM

↓

Firewall
```

因此：

API VM 一定先建立。

Firewall 一定後建立。

整個 Dependency Graph 都由 Terraform 自動計算。

大部分情況下，不需要自行撰寫：

```hcl
depends_on
```

---

# 驗證

Terraform Output：

```bash
terraform output
```

結果：

```
vm_internal_ip = "10.140.0.3"

vm_machine_type = "e2-medium"

vm_name = "hpc-api-dev"

vm_zone = "asia-east1-a"
```

代表 Output 已成功從 Terraform State 取得所有 Resource Attribute。

---

# 今日重點

Terraform Resource 並不是一個固定字串。

它是一個可以被其他 Resource 引用的物件。

Terraform 透過：

```
Resource Type

↓

Logical Name

↓

Attribute
```

取得 Resource 的所有資訊。

這也是 Terraform 能夠建立大型 Infrastructure 的核心能力。

---

# Interview Q&A

## Q1：Terraform Output 的用途是什麼？

Terraform Output 用來輸出 Resource 的屬性，例如 VM Name、Internal IP、Machine Type 等資訊，方便其他 Module、使用者或 CI/CD 使用。

---

## Q2：什麼是 Resource Reference？

Resource Reference 是 Terraform 用來引用其他 Resource 的方式，例如：

```hcl
google_compute_instance.api.name
```

Terraform 會依照 Resource Type、Logical Name 與 Attribute 找到對應 Resource，並取得最新值，而不需要手動填寫。

---

## Q3：什麼是 Implicit Dependency？

當一個 Resource 引用另一個 Resource 時，Terraform 會自動建立 Dependency Graph，決定正確的建立順序，因此通常不需要手動撰寫 `depends_on`。

---

# 本日總結

今天正式進入 Terraform Resource 之間互相引用的階段。

學會使用 Output、Resource Reference 與 Resource Attribute 後，Terraform 已經不只是建立 Infrastructure，而是開始描述 Infrastructure 之間的關係。

這也是 Terraform 能夠管理大型雲端環境的重要基礎。

---

# 下一步

下一章將開始學習 Terraform Module，將 Compute、Network、Storage 等 Resource 模組化，建立符合企業實務的 Terraform 專案架構。
