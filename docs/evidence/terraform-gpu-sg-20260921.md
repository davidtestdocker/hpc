# hpc-gpu-sg Terraform 對齊證據

日期：2026-09-21

## 範圍

新增獨立 root module `terraform/environments/gpu-sg`，描述既有 zonal GKE
`hpc-gpu-sg`、`system-pool` 與 NVIDIA L4 `gpu-pool`。共享的 `default`
VPC／subnet 只透過 data source 讀取，不納入本 state 的生命週期。

## 驗證結果

```text
terraform fmt -check  PASS
terraform validate   PASS
```

先匯入現有 cluster 與兩個 node pools 到本機、被 git 忽略的 state。第一次
plan 顯示 `1 add, 1 change, 1 destroy`，原因是匯入後 API 回報
`initial_node_count=0`，而該欄位是 ForceNew。沒有執行這份 plan。

修正建立期欄位的 lifecycle、NodeLocal DNS 表示方式與 provider 正規化後，
最終匯入後 plan 為：

```text
No changes. Your infrastructure matches the configuration.
```

這證明 2026-09-21 執行 plan 時，三個已匯入資源與目前 HCL 收斂；不代表
remote state、另一個專案或未納管的 Kubernetes add-ons 已完成。

## 隔離 lifecycle rehearsal

另以 repo 外的空 state、不同名稱 `hpc-gpu-sg-rehearsal`、
`gpu_node_count=0` 與 `deletion_protection=false` 執行 plan：

```text
Plan: 3 to add, 0 to change, 0 to destroy.
```

接著實際執行 apply：

```text
Apply complete! Resources: 3 added, 0 changed, 0 destroyed.
```

- control plane 約 7 分 40 秒完成。
- `system-pool` 約 1 分 4 秒完成，GKE API 回報 `RUNNING`、
  `initialNodeCount: 1`、`e2-standard-2`。
- 零節點 `gpu-pool` 約 23 秒完成，GKE API 回報 `RUNNING`，設定為
  `g2-standard-4`、1 x NVIDIA L4、`TIME_SHARING`、每 GPU 4 clients。
- apply 後再次 plan，結果為 `No changes`。

驗收後用同一份 state 執行 destroy plan（0 add／0 change／3 destroy）並
完成：

```text
Apply complete! Resources: 0 added, 0 changed, 3 destroyed.
```

destroy 後 `terraform state list` 無輸出，`gcloud container clusters
describe hpc-gpu-sg-rehearsal` 回傳 404 `Not found`。這證明 Terraform 可建立、
收斂與清理這個 CPU-only rehearsal；沒有配置 GPU VM，也沒有在該叢集部署
Kubernetes platform workloads。

## NetworkPolicy rehearsal

同日第二次以相同隔離 state 建立 cluster，將 `enable_network_policy=true`。
GKE API 回報 provider `CALICO`，system node 為 Ready；完成 packet-level
baseline／allow／deny／recovery 後再次 destroy。完整結果見
[NetworkPolicy evidence](network-policy-validation-20260921.json)。第二次 cleanup
同樣是 3 destroyed、空 state 與 GKE 404。

## 安全邊界

- 現有主叢集沒有被 apply、replace 或 destroy；apply／destroy 只針對獨立 rehearsal state。
- `.tfstate` 與 plan 檔不提交 repo；`.terraform.lock.hcl` 固定 provider 版本。
- 正式多人管理仍需 GCS backend、state locking／權限與 bootstrap 流程。
- Kubernetes controllers、Kueue、JobSet、Secret 與 platform overlay 不屬於此
  Terraform state，必須由後續 bootstrap／GitOps 驗收。
