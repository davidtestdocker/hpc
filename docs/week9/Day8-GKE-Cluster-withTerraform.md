<!-- readable-curriculum: 2026-09-22 -->
# Week9 Day8 — GKE 到 CPU bootstrap

[上一課](<Day7-Terraform-Multi-Environment.md>) · [本週目錄](README.md) · [下一週](../week10/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

主環境 import／zero drift、隔離 cluster lifecycle、全新 CPU 平台 bootstrap 是不同驗收。後者完成 controllers／平台／RBAC／PVC，但不包含全新 GPU MPI 執行。

## 在現在的專案中

本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

本課對照：[scripts/bootstrap_cluster.py](<../../scripts/bootstrap_cluster.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def download_controller(name, target):
    # Release URL 與 digest 同時鎖定，避免相同操作取得不同或遭竄改的 manifest。
    metadata = CONTROLLERS[name]
    with urllib.request.urlopen(metadata["url"], timeout=60) as response:
        content = response.read()
    digest = hashlib.sha256(content).hexdigest()
    if digest != metadata["sha256"]:
        raise RuntimeError(f"{name} manifest checksum mismatch")
    target.write_bytes(content)


def validate_postgres_env(path):
    # 僅回傳鍵名集合；錯誤與 evidence 都不包含密碼值。
    values = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise RuntimeError("PostgreSQL env file 格式錯誤")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    required = {"POSTGRES_USER", "POSTGRES_PASSWORD"}
    if any(not values.get(key) for key in required):
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week9/Day8-GKE-Cluster-withTerraform.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 Terraform root 是 environments/gpu-sg；後續已完成全新 CPU-only 平台 bootstrap，不包含新 GPU 叢集 MPI 驗收。
> **閱讀順序**：先學本文基礎，再讀[Week9 現行對照與檢核](../learning-guide.md#week9)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week9 Day8 - Google Kubernetes Engine (GKE) with Terraform

> 現行入口（2026-09-21）：[gpu-sg Terraform README](../../terraform/environments/gpu-sg/README.md) 與 [驗證證據](../evidence/terraform-gpu-sg-20260921.md)。本文其餘內容保留 hpc-dev 歷史實驗；不可把歷史指令直接用於主環境。

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [terraform/environments/dev/main.tf](../../terraform/environments/dev/main.tf)
- [terraform/environments/dev/outputs.tf](../../terraform/environments/dev/outputs.tf)
- [terraform/modules/gke/main.tf](../../terraform/modules/gke/main.tf)
- [terraform/modules/gke/outputs.tf](../../terraform/modules/gke/outputs.tf)
- [terraform/modules/gke/variables.tf](../../terraform/modules/gke/variables.tf)
- [terraform/environments/gpu-sg/main.tf](../../terraform/environments/gpu-sg/main.tf)

## 2026-09-21 主環境對齊

主展示環境已使用獨立 root module 描述 GKE cluster、CPU system pool 與 L4
GPU pool。既有三個資源完成 import，最終 plan 為 `No changes`；另以隔離
state 與不同 cluster 名稱完成 `3 add / 0 change / 0 destroy` plan，並實際
完成 apply、GKE RUNNING、apply 後 zero drift 與 destroy。這一階段只驗證 CPU-only
基礎設施 lifecycle，當時尚未 bootstrap 完整平台或配置 GPU VM。

後續進度（截至 2026-09-22）：另一個全新 CPU-only 叢集已完成 controllers、Secrets、queues、平台部署、health／RBAC／PVC 驗收與銷毀，見 [CPU bootstrap 證據](../evidence/cpu-bootstrap-acceptance-20260921.json) 與 [現行操作](../runbooks/platform-bootstrap.md)。不包含全新 GPU 叢集 MPI 執行；不要將兩次驗證混成同一次結果。

---

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
