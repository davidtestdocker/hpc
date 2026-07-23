# Week9 Day6 - Terraform Network Module

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
