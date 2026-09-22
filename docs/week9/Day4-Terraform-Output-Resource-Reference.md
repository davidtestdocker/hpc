<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day4 — Outputs 與資源引用

[上一課](<Day3-Terraform-Apply-State-Resource-Lifecycle.md>) · [本週目錄](README.md) · [下一課](<Day5-Terraform-Module-Refactor.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 output 摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

terraform output 顯示保存的 state output，不保證 cloud 最新實況；resource 引用值在規劃／apply 時解析，不是每次讀取就即時刷新。資源依賴取決於真實引用，不能一概 firewall 必須晚於 VM。

## 程式／設定與來源

本次核對：[terraform/modules/compute/outputs.tf](<../../terraform/modules/compute/outputs.tf>)、[terraform/environments/stage/outputs.tf](<../../terraform/environments/stage/outputs.tf>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day4-Terraform-Output-Resource-Reference.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
vm_internal_ip = "10.140.0.3"
```

保存的是當時 e2-medium VM 私有 IP，不是可連線現行服務；本次不讀可能含敏感資料的 state。

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
