<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day6 — VPC 與 subnet

[上一課](<Day5-Terraform-Module-Refactor.md>) · [本週目錄](README.md) · [下一課](<Day7-Terraform-Multi-Environment.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：設定與 plan 敘述，無 apply 證據。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

原文在 plan 後寫「均建立成功」不成立：列出的驗證命令沒有 apply。現行舊 firewall 允許 0.0.0.0/0 的 TCP22/8000，不能稱最小權限；主 gpu-sg 使用既有 default network，未採這套自建 VPC。

## 程式／設定與來源

本次核對：[terraform/modules/network/main.tf](<../../terraform/modules/network/main.tf>)、[terraform/modules/firewall/main.tf](<../../terraform/modules/firewall/main.tf>)、[terraform/environments/dev/main.tf](<../../terraform/environments/dev/main.tf>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day6-Terraform-Network-Module.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Network
```

Network/Subnet/Firewall 只是文內摘要；沒有 apply 完成記錄就標未證實建立。

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
