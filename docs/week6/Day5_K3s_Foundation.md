<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day5 — K3s 與 GKE 邊界

[上一課](<Day4_Service_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day6_Deploy_API_and_Redis.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

K3s 可用於學習 Kubernetes 基本物件，但 GKE 的 node labels、GPU 整合、儲存類別與雲端認證不可原樣搬過去。把主 overlay 套進不同叢集前需重新確認依賴。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[scripts/platform.py](<../../scripts/platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
CONTEXT = "gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg"


def command(args):
    # 統一由 repo 根目錄執行外部工具，並以 timeout 避免認證或 API server 卡住。
    try:
        result = subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"{args[0]} unavailable or timed out") from exc
    if result.returncode:
        # Avoid putting credential-plugin stderr into saved evidence.
        raise RuntimeError(f"command failed (exit {result.returncode}): {' '.join(args)}")
    return result.stdout


def render():
    # 只渲染 Kustomize／Helm，不會套用任何資源到叢集。
    return command([
        "kubectl", "kustomize", "kustomize/overlays/gpu-sg-platform",
        "--enable-helm", "--load-restrictor", "LoadRestrictionsNone",
    ])

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week6/Day5_K3s_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day5 - K3s Foundation

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day6_Deploy_API_and_Redis](Day6_Deploy_API_and_Redis.md)。

---

## 今日平台增加什麼

今天平台正式新增：

```text
Kubernetes Runtime
```

也就是：

```text
K3s Cluster
```

平台從：

```text
Docker Compose
```

開始演進到：

```text
Kubernetes Cluster
```

---

# Platform Problem

目前平台使用 Docker Compose 管理：

```text
api
redis
postgres
```

Docker Compose 適合單機開發，但缺少：

* Desired State
* Self Healing
* Pod Scheduling
* Service Discovery
* Kubernetes Resource Model

因此需要建立 Kubernetes 環境，讓後續可以使用：

* Pod
* Deployment
* Service
* ConfigMap
* Secret
* Volume
* PVC

---

# 今日知識鏈

```text
Linux VM
    ↓
K3s
    ↓
Kubernetes Control Plane
    ↓
Node
    ↓
kubectl
```

---

# Hands-on

## 1. 確認環境乾淨

確認尚未安裝 K3s：

```bash
which k3s
which kubectl
```

如果沒有輸出，代表環境尚未安裝 K3s。

---

## 2. 安裝 K3s

執行：

```bash
curl -sfL https://get.k3s.io | sh -
```

這個安裝流程會：

* 下載 K3s binary
* 建立 systemd service
* 啟動 K3s server
* 建立 kubeconfig
* 提供 kubectl 操作能力

---

## 3. 驗證 K3s Service

檢查：

```bash
systemctl status k3s
```

確認：

```text
active (running)
```

---

## 4. 驗證 Kubernetes Node

執行：

```bash
kubectl get nodes
```

結果：

```text
NAME       STATUS   ROLES           VERSION
hpc-demo   Ready    control-plane   v1.36.2+k3s1
```

代表：

* K3s 安裝成功
* Kubernetes Control Plane 正常
* kubeconfig 正常
* kubectl 可以連線
* Node 已 Ready

---

## 5. 檢查 kube-system 元件

執行：

```bash
kubectl get pods -A
```

確認以下元件正常：

```text
coredns                  Running
local-path-provisioner   Running
metrics-server           Running
traefik                  Running
svclb-traefik            Running
```

---

# K3s 內建元件

## CoreDNS

負責 Kubernetes 內部 DNS。

例如未來 Pod 可以透過：

```text
redis-service
postgres-service
api-service
```

互相存取。

---

## local-path-provisioner

負責提供本機磁碟型 StorageClass。

之後 Redis / PostgreSQL 的 PVC 會用到。

---

## metrics-server

提供 Kubernetes Metrics API。

未來 HPA、資源監控會用到。

---

## Traefik

K3s 預設內建 Ingress Controller。

後面學 Ingress 時會用到。

---

## svclb-traefik

K3s 內建 Service LoadBalancer 機制。

讓 Traefik 能提供外部入口。

---

# 平台架構

```text
Ubuntu VM
    ↓
K3s Server
    ↓
Kubernetes Control Plane
    ↓
Node: hpc-demo
    ↓
kube-system
    ├── CoreDNS
    ├── local-path-provisioner
    ├── metrics-server
    ├── Traefik
    └── svclb-traefik
```

---

# 今日重點

* K3s 是輕量 Kubernetes Distribution。
* K3s 適合單機學習、Lab、Edge 與小型平台。
* `kubectl get nodes` 是確認 Cluster 是否可用的第一步。
* `kubectl get pods -A` 可以查看整個 Cluster 內所有 Namespace 的 Pod。
* `kube-system` 是 Kubernetes 系統元件所在的 Namespace。
* Node `Ready` 代表 Kubernetes 可以開始排程 Pod。

---

# Interview Q&A

## Q1：K3s 和 Kubernetes 是什麼關係？

K3s 是一個輕量化的 Kubernetes Distribution。

它保留 Kubernetes API 與核心功能，但將安裝與運維簡化，適合 Lab、Edge、單機環境與輕量平台。

---

## Q2：為什麼要先確認 `kubectl get nodes`？

因為 Node Ready 代表：

* Kubernetes API Server 可用
* kubeconfig 正確
* kubectl 能連線
* Control Plane 正常
* Node 可接受 Pod Scheduling

如果 Node 不是 Ready，後續 Deployment、Service、PVC 都可能無法正常運作。

---

# 今日成果

成功建立第一個 Kubernetes Cluster：

```text
hpc-demo
    ↓
K3s
    ↓
Ready Node
```

平台正式從：

```text
Docker Compose Platform
```

進入：

```text
Kubernetes Platform
```

---

# 下一步

Week6 Day6：

開始把目前的 HPC AI Benchmark Platform 從 Docker Compose 遷移到 Kubernetes。

內容包括：

* 建立 Namespace
* 建立 API Deployment
* 建立 API Service
* 建立 Redis Deployment / Service
* 建立 PostgreSQL Deployment / Service
* 驗證 FastAPI 在 Kubernetes 中正常啟動
