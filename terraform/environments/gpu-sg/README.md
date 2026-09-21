# hpc-gpu-sg Terraform environment

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
  -var='project_id=project-4b82f780-0a12-4087-b94' \
  google_container_cluster.this \
  projects/project-4b82f780-0a12-4087-b94/locations/asia-southeast1-a/clusters/hpc-gpu-sg

terraform -chdir=terraform/environments/gpu-sg import \
  -var='project_id=project-4b82f780-0a12-4087-b94' \
  google_container_node_pool.system \
  projects/project-4b82f780-0a12-4087-b94/locations/asia-southeast1-a/clusters/hpc-gpu-sg/nodePools/system-pool

terraform -chdir=terraform/environments/gpu-sg import \
  -var='project_id=project-4b82f780-0a12-4087-b94' \
  google_container_node_pool.gpu \
  projects/project-4b82f780-0a12-4087-b94/locations/asia-southeast1-a/clusters/hpc-gpu-sg/nodePools/gpu-pool
```

Import 只建立 Terraform state 關聯，不會修改雲端資源。state 被 git 忽略，因此每個新的 backend／工作目錄都必須自行 import。匯入後先執行 refresh-only plan，再執行一般 plan：

```bash
terraform -chdir=terraform/environments/gpu-sg plan \
  -refresh-only -var='project_id=project-4b82f780-0a12-4087-b94'

terraform -chdir=terraform/environments/gpu-sg plan \
  -var='project_id=project-4b82f780-0a12-4087-b94' -out=/tmp/hpc-gpu-sg.tfplan
terraform -chdir=terraform/environments/gpu-sg show /tmp/hpc-gpu-sg.tfplan
```

只有 plan 確認沒有 replacement／destroy，且變更符合預期後才可 apply。2026-09-21 匯入現有三個資源後的結果為 `No changes`，沒有 apply。

## 建立隔離 rehearsal cluster

**不可在已匯入主環境的同一份 state 修改 `cluster_name`**，否則 plan 會要求替換主 cluster。先把本目錄的 `.tf`、lock file 與 example 複製到 repo 外的新暫存目錄，在那裡使用獨立 state：

```bash
REHEARSAL_DIR="$(mktemp -d)"
cp terraform/environments/gpu-sg/*.tf "$REHEARSAL_DIR/"
cp terraform/environments/gpu-sg/.terraform.lock.hcl "$REHEARSAL_DIR/"
cp terraform/environments/gpu-sg/terraform.tfvars.example "$REHEARSAL_DIR/terraform.tfvars"
terraform -chdir="$REHEARSAL_DIR" init -backend=false
terraform -chdir="$REHEARSAL_DIR" plan -out=rehearsal.tfplan
```

example 使用不同 `cluster_name`、`gpu_node_count=0`、`gpu_spot=false`、`deletion_protection=false` 與 `enable_network_policy=true`。這會規劃啟用 Calico 的 cluster、system pool 與零節點 GPU pool；需要短暫 GPU rehearsal 時才把 GPU node count 提高為 1，並可將 `gpu_spot=true` 使用可中斷節點。主環境的兩個變數預設皆為 false，用以對齊現況。

這個設定使用共享 default subnet 與 GKE alias IP 自動配置。建立前仍要確認 subnet secondary ranges、L4 quota、GKE／Compute API、服務帳號權限與預估費用。2026-09-21 已完成 CPU-only lifecycle、Calico allow／deny，以及全新 CPU-only cluster 的 controllers／platform bootstrap、acceptance、destroy；另已在主叢集驗證 GPU 模式的 server dry-run。全新 GPU cluster 因全域 quota 尚未完成 MPI 驗收。多人使用前仍需建立 GCS backend 與權限流程。

GPU quota 必須同時檢查區域 accelerator metric 與專案全域
`GPUS_ALL_REGIONS`。即使 `PREEMPTIBLE_NVIDIA_L4_GPUS` 有餘額，全域 quota 用滿
仍會讓 Spot node pool 進入 ERROR。apply 前執行：

```bash
PYTHONPATH=. .venv/bin/python -m scripts.check_gcp_quota \
  --project YOUR_PROJECT --region asia-southeast1 --gpu-count 1 --spot \
  --output /tmp/gpu-quota.json
```
