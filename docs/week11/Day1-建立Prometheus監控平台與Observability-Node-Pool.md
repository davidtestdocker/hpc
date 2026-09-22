<!-- readable-curriculum: 2026-09-22 -->
# Week11 Day1 — Prometheus 與資源分工

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-Prometheus-ScrapeJob-Target與PullModel.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

監控本身消耗 CPU、RAM、儲存，與被測工作共用節點時可能互相影響。舊 observability-pool 屬不同環境設計；現行 system-pool 的存在不能證明舊監控都已搬過來。

## 在現在的專案中

監控 manifests 和歷史 dashboard 保留為獨立路徑；不宣稱即時 target 健康。

本課對照：[helm/prometheus/templates/deployment.yaml](<../../helm/prometheus/templates/deployment.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
spec:
  # 期望副本數；設定為 0 表示不維持執行中的副本。
  replicas: {{ .Values.replicaCount }}
  strategy:
    type: Recreate
  # 選取要關聯的物件；不同資源種類支援的 selector 格式不同。
  selector:
    # 以完全相等的標籤鍵值選取物件。
    matchLabels:
      {{- include "prometheus.selectorLabels" . | nindent 6 }}
  # 子物件模板；控制器以此內容建立 Pod 或相關工作資源。
  template:
    metadata:
      #只要configmap.yaml內容有變 sha256sum就會變，所以就會偵測到prometheus的deployment有變，就會建新的prometheus pod
      # 附加設定或提示，由對應控制器解讀，不等同 selector 標籤。
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "prometheus.selectorLabels" . | nindent 8 }}
    spec:
      # Pod 使用的 ServiceAccount；RBAC 依此身分授予 API 權限。
      serviceAccountName: prometheus
      #這個 Pod 掛載的 Volume（PVC）都套用這個權限設定
      # 程序身分、權限與作業系統安全設定。
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week11/Day1-建立Prometheus監控平台與Observability-Node-Pool.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：舊監控環境／dashboard 不等於即時健康；9/22 訓練保存的是 nvidia-smi 遙測與 CUDA traces。
> **閱讀順序**：先學本文基礎，再讀[Week11 現行對照與檢核](../learning-guide.md#week11)及[對應現行入口](../evidence/README.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week11 Day1 - 建立 Prometheus 監控平台與 Observability Node Pool

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/prometheus/Chart.yaml](../../helm/prometheus/Chart.yaml)
- [helm/prometheus/templates/_helpers.tpl](../../helm/prometheus/templates/_helpers.tpl)
- [helm/prometheus/templates/clusterrole.yaml](../../helm/prometheus/templates/clusterrole.yaml)
- [helm/prometheus/templates/clusterrolebinding.yaml](../../helm/prometheus/templates/clusterrolebinding.yaml)
- [helm/prometheus/templates/configmap.yaml](../../helm/prometheus/templates/configmap.yaml)
- [helm/prometheus/templates/deployment.yaml](../../helm/prometheus/templates/deployment.yaml)
- [helm/prometheus/templates/pvc.yaml](../../helm/prometheus/templates/pvc.yaml)
- [helm/prometheus/templates/service.yaml](../../helm/prometheus/templates/service.yaml)
- [helm/prometheus/templates/serviceaccount.yaml](../../helm/prometheus/templates/serviceaccount.yaml)
- [helm/prometheus/values.yaml](../../helm/prometheus/values.yaml)
- [kustomize/overlays/dev/deployment-patch.yaml](../../kustomize/overlays/dev/deployment-patch.yaml)
- [kustomize/overlays/dev/kustomization.yaml](../../kustomize/overlays/dev/kustomization.yaml)
- [terraform/modules/gke/main.tf](../../terraform/modules/gke/main.tf)

---

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
