# Week9 Day8 - Google Kubernetes Engine (GKE) with Terraform

## 今日目標

- 使用 Terraform 建立 Google Kubernetes Engine
- 建立 Node Pool
- 使用 kubectl 連線 GKE
- 理解 Regional 與 Zonal Cluster 差異
- 優化 GKE 成本

---

# 今日成果

- 完成 GKE Cluster 建立
- 完成 Node Pool 建立
- 安裝 `gke-gcloud-auth-plugin`
- 成功使用 `kubectl` 連線 GKE
- 將 Regional Cluster 修改為 Zonal Cluster
- 將 Node 數量由 3 台優化為 1 台
- 移除未使用的 Compute Engine VM (`hpc-api-dev`)
- 完成 Terraform Infrastructure 最佳化

---

# Google Kubernetes Engine

Google Kubernetes Engine（GKE）是 Google Cloud 提供的 Managed Kubernetes Service。

使用者不用自行安裝：

- Kubernetes Control Plane
- etcd
- API Server
- Scheduler
- Controller Manager

Google 會負責維護 Kubernetes Control Plane，使用者只需要管理 Worker Node 與 Kubernetes Workload。

---

# Terraform GKE Module

建立：

```hcl
module "gke" {

  source = "../../modules/gke"

  project_id  = var.project_id
  region      = var.region
  zone        = var.zone

  cluster_name = "hpc-dev"

  network    = module.network.network_name
  subnetwork = module.network.subnet_name

  node_count   = 1
  machine_type = "e2-standard-2"

}
```

透過 Module 建立：

- GKE Cluster
- Node Pool

---

# Google Container Cluster

Terraform：

```hcl
resource "google_container_cluster" "this"
```

用途：

建立 Kubernetes Cluster。

包含：

- Kubernetes Control Plane
- API Server
- Scheduler
- Controller Manager

Google Cloud 會負責維護。

---

# Google Container Node Pool

Terraform：

```hcl
resource "google_container_node_pool" "primary"
```

用途：

建立 Worker Node。

Node Pool 內的每一台 VM 都會加入 Kubernetes Cluster。

Pod 最終會執行於 Node 上。

---

# Regional Cluster

原本設定：

```hcl
location = var.region
```

例如：

```
asia-east1
```

代表建立：

```
asia-east1

├── asia-east1-a
├── asia-east1-b
└── asia-east1-c
```

每個 Zone 都會建立 Worker Node。

因此即使：

```hcl
node_count = 1
```

最後仍建立：

```
3 Nodes
```

---

# Zonal Cluster

修改：

```hcl
location = var.zone
```

例如：

```
asia-east1-a
```

Cluster 僅建立於單一 Zone。

結果：

```
asia-east1-a

└── Worker Node
```

Node 數量：

```
1
```

適合：

- 個人專案
- Lab
- Demo
- 學習環境

可有效降低雲端成本。

---

# Compute Engine 最佳化

Terraform 原本建立：

```
hpc-api-dev
```

用途原本預計部署 API。

後續專案改為：

```
API

↓

Docker

↓

Kubernetes

↓

GKE
```

因此：

Compute Engine 已無用途。

最終移除：

```
module "api"
```

降低 Compute Engine 成本。

---

# Terraform Workflow

初始化：

```bash
terraform init
```

格式化：

```bash
terraform fmt
```

檢查：

```bash
terraform validate
```

預覽：

```bash
terraform plan
```

建立：

```bash
terraform apply
```

---

# kubectl Authentication

取得 Cluster Credentials：

```bash
gcloud container clusters get-credentials hpc-dev \
    --zone asia-east1-a
```

之後即可使用：

```bash
kubectl
```

管理 GKE。

---

# 驗證

查看 Cluster：

```bash
kubectl cluster-info
```

查看 Node：

```bash
kubectl get nodes
```

預期：

```
STATUS

Ready
```

Node：

```
1
```

---

# 今日遇到的問題

### 1.

```
kubectl 無法連線 GKE
```

原因：

缺少：

```
gke-gcloud-auth-plugin
```

解法：

安裝 Google Cloud CLI 官方 Plugin。

---

### 2.

```
建立完成後出現三台 Node
```

原因：

Cluster 建立為：

```
Regional Cluster
```

Terraform：

```hcl
location = var.region
```

解法：

修改：

```hcl
location = var.zone
```

重新建立 Cluster。

---

### 3.

```
Terraform plan 出現 module.api 錯誤
```

原因：

已移除：

```
module "api"
```

但：

```
outputs.tf
```

仍引用：

```
module.api
```

解法：

同步移除相關 Output。

---

# 今日重點

- GKE 為 Google Cloud Managed Kubernetes。
- Google 負責 Kubernetes Control Plane。
- Node Pool 提供 Kubernetes Worker Node。
- Regional Cluster 會跨多個 Zone 建立 Node。
- Zonal Cluster 僅建立於單一 Zone。
- Terraform Module 可提升 Infrastructure 重用性。
- Terraform State 會追蹤所有建立的雲端資源。

---

# Interview Q&A

### Q1：Regional Cluster 與 Zonal Cluster 差異？

Regional Cluster 會將 Control Plane 與 Worker Node 分散於多個 Zone，提高可用性；Zonal Cluster 僅建立於單一 Zone，成本較低，適合開發與學習環境。

---

### Q2：為什麼刪除 Compute Engine VM？

平台後續將全面部署於 GKE，API 不再直接執行於 Compute Engine，因此移除未使用 VM 可降低成本並簡化架構。

---

# 本日總結

今天完成 HPC AI Performance Platform 雲端 Kubernetes 基礎建設，利用 Terraform 建立 Google Kubernetes Engine、Node Pool 與 Kubernetes 環境，成功使用 `kubectl` 連線 GKE，並將 Regional Cluster 最佳化為 Zonal Cluster、移除未使用的 Compute Engine，完成 Terraform Infrastructure as Code 與雲端成本優化，為後續將平台部署至 GKE 與建立 CI/CD 流程奠定基礎。
