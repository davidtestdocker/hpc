# Week11 Day1 - 建立 Prometheus 監控平台與 Observability Node Pool

---

# 今日目標

今天完成以下內容：

- 建立 Observability Node Pool
- 理解 Node Pool、Node、Label、nodeSelector
- 建立 Prometheus Helm Chart
- 使用 Helm + Kustomize + ArgoCD 部署 Prometheus
- 理解 ConfigMap、PVC、Volume Mount
- 排除 Prometheus CrashLoopBackOff
- 完成 GitOps 自動部署流程

---

# 今日架構

```text
Terraform
    │
    ▼
建立 Observability Node Pool
    │
    ▼
Node Label
workload=observability
    │
    ▼
Helm Chart
    │
    ▼
Kustomize
    │
    ▼
ArgoCD
    │
    ▼
Deployment
    │
    ▼
Kubernetes Scheduler
    │
    ▼
Observability Node
    │
    ▼
Prometheus Pod
```

---

# 一、建立 Observability Node Pool

## Terraform

```hcl
resource "google_container_node_pool" "observability" {

  name     = "observability-pool"

  cluster  = google_container_cluster.this.name

  location = var.zone

  node_count = 1

  node_config {

    machine_type = "e2-standard-2"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      workload = "observability"
    }
  }
}
```

---

## 驗證

```bash
terraform validate
terraform plan
terraform apply
```

查看 Node

```bash
kubectl get nodes -L workload
```

結果

```text
NAME                                           WORKLOAD

gke-hpc-dev-primary-pool-xxxx

gke-hpc-dev-observability-pool-xxxx            observability
```

代表 Terraform 已建立新的 Node Pool，並替所有 Node 加上：

```text
workload=observability
```

---

# 二、Node Pool、Node 關係

```text
GKE Cluster

├── Primary Node Pool
│      └── Node (VM)
│
└── Observability Node Pool
       └── Node (VM)
```

Node Pool：

- 管理 Node
- 決定 VM 規格
- Auto Scaling
- Labels
- Upgrade Policy

Node：

- 真正執行 Pod 的 VM

---

# 三、nodeSelector

values.yaml

```yaml
nodeSelector:
  workload: observability
```

deployment.yaml

```yaml
nodeSelector:
  {{- toYaml .Values.nodeSelector | nindent 8 }}
```

Helm Render

```yaml
nodeSelector:
  workload: observability
```

Scheduler 流程

```text
Deployment

↓

nodeSelector

↓

workload=observability

↓

Scheduler 尋找符合 Label 的 Node

↓

Prometheus Pod

↓

Observability Node
```

---

# 四、建立 Prometheus Helm Chart

建立

```text
helm/prometheus
```

目錄

```text
prometheus

├── Chart.yaml

├── values.yaml

└── templates

    ├── configmap.yaml

    ├── pvc.yaml

    ├── deployment.yaml

    └── service.yaml
```

---

# 五、ConfigMap

Prometheus 設定檔

```text
prometheus.yml
```

建立 ConfigMap

```yaml
volumes:
  - name: prometheus-config
    configMap:
      name: prometheus
```

掛載

```yaml
volumeMounts:
  - name: prometheus-config
    mountPath: /etc/prometheus
```

Prometheus 啟動

```yaml
args:
  - --config.file=/etc/prometheus/prometheus.yml
```

流程

```text
ConfigMap

↓

prometheus.yml

↓

Volume

↓

/etc/prometheus

↓

Prometheus 程式讀取
```

---

# 六、PersistentVolumeClaim (PVC)

建立 PVC

```yaml
persistentVolumeClaim:
  claimName: prometheus
```

掛載

```yaml
volumeMounts:
  - name: prometheus-data
    mountPath: /prometheus
```

Prometheus

```yaml
args:
  - --storage.tsdb.path=/prometheus
```

流程

```text
Prometheus

↓

寫入

↓

/prometheus

↓

PVC

↓

Google Persistent Disk
```

因此：

Pod 被刪除

↓

資料仍存在

---

# 七、Helm + Kustomize

加入

```yaml
helmCharts:

  - name: prometheus
    releaseName: prometheus
    namespace: hpc-platform-dev
```

Render

```bash
kubectl kustomize kustomize/overlays/dev \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone
```

流程

```text
Helm

↓

Render YAML

↓

Kustomize

↓

ArgoCD
```

---

# 八、GitOps 流程

```text
git push

↓

GitHub

↓

GitHub Actions

↓

更新 Image Tag

↓

Push Repository

↓

ArgoCD 偵測新 Commit

↓

Kustomize + Helm

↓

Deployment 更新

↓

建立新 Pod
```

---

# 九、CrashLoopBackOff 排除

錯誤

```text
permission denied

open /prometheus/queries.active
```

原因

PVC 已成功掛載

但是

Prometheus 沒有寫入權限

解法

```yaml
spec:
  securityContext:
    fsGroup: 65534
```

流程

```text
Prometheus

↓

寫入 /prometheus

↓

Permission Denied

↓

設定 fsGroup

↓

Kubernetes 修改 Volume 群組權限

↓

Prometheus 正常啟動
```

---

# 十、驗證

Helm

```bash
helm lint helm/prometheus

helm template prometheus helm/prometheus
```

Kustomize

```bash
kubectl kustomize kustomize/overlays/dev \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone
```

GitOps

```bash
git add .

git commit -m "feat: add prometheus"

git pull --rebase origin master

git push origin master
```

確認 Pod

```bash
kubectl get pods -o wide -n hpc-platform-dev
```

確認 PVC

```bash
kubectl get pvc -n hpc-platform-dev
```

確認 Node

```bash
kubectl get nodes -L workload
```

預期結果

```text
Prometheus

Running

Node

gke-hpc-dev-observability-pool-xxxxx
```

---

# 今日重點整理

- Node Pool 是一群 Node 的管理單位
- Node 才是真正執行 Pod 的 VM
- Scheduler 依 nodeSelector 找符合 Label 的 Node
- ConfigMap 提供 prometheus.yml
- Prometheus 啟動時讀取 /etc/prometheus/prometheus.yml
- PVC 提供永久磁碟
- Metrics 存放於 PVC，不會因 Pod 重建而消失
- Helm Render 後交由 Kustomize
- ArgoCD 偵測 Git Commit 後自動部署
- fsGroup 可解決 PVC 權限問題

---

# Interview QA

## Q1：Node Pool 與 Node 有什麼差別？

### Answer

Node Pool 是一組具有相同設定的 Node，例如 VM 規格、Label、Auto Scaling 與升級策略；Node 則是真正執行 Pod 的虛擬機器（VM）。Scheduler 最終是將 Pod 排程到某一台 Node，而不是排到 Node Pool。

---

## Q2：為什麼 Prometheus 已經成功掛載 PVC，仍然出現 permission denied？

### Answer

PVC 只代表永久磁碟已成功掛載，但不代表容器擁有寫入權限。Prometheus 以非 root 身分執行，因此需要設定：

```yaml
securityContext:
  fsGroup: 65534
```

Kubernetes 會自動修改掛載 Volume 的群組權限，讓 Prometheus 能正常寫入 TSDB 資料。
