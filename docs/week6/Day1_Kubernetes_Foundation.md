<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day1 — Kubernetes 控制迴圈

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2_Pod_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

kubectl 對 API server 送出宣告，controller 再逐步收斂；apply 成功只表示宣告被接受。CRD 讓 JobSet／Kueue 類型可被辨識，還需要對應 controller 才能執行協調。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week6/Day1_Kubernetes_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day1 - Kubernetes Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/api-service.yaml](../../k8s/api-service.yaml)

---

## 今日平台增加什麼

今天沒有安裝 Kubernetes。

今天建立的是 Kubernetes 最重要的觀念：

```text
Docker

↓

Kubernetes
```

理解：

> Docker 負責執行 Container。

> Kubernetes 負責管理 Container。

---

# Platform Problem

目前平台：

```text
Docker Compose

├── api
├── redis
└── postgres
```

查看：

```bash
docker ps
```

結果：

```text
api
redis
postgres
```

平台共有：

```text
3 Containers
```

架構：

```text
Docker Host
│
├── api Container
├── redis Container
└── postgres Container
```

---

# Docker 的限制

假設：

```text
api

↓

api × 3
```

變成：

```text
api-1
api-2
api-3
redis
postgres
```

如果：

```text
api-2 Crash
```

Docker 不會：

* 自動建立新 Container
* 維持固定數量
* 自動修復

需要人工：

```bash
docker compose restart api
```

或：

```bash
docker compose up -d
```

---

# Kubernetes 解決什麼？

Kubernetes 不負責建立 Container。

Kubernetes 負責：

```text
Desired State
```

例如：

```text
API

我要 3 個
```

如果：

```text
api-2 Crash
```

Kubernetes：

```text
重新建立新的 Pod
```

自動恢復到：

```text
API = 3
```

這就是：

```text
Self Healing
```

---

# Docker vs Kubernetes

Docker：

```text
Build Image

Run Container
```

Kubernetes：

```text
Scheduling

Scaling

Self Healing

Service Discovery

Container Orchestration
```

兩者不是互相取代，而是合作。

---

# 今日知識鏈

```text
Container
      │
      ▼
Pod
      │
      ▼
ReplicaSet
      │
      ▼
Deployment
      │
      ▼
Service
```

Week6 全部內容都圍繞這條知識鏈展開。

---

# 今日重點

Docker：

```text
Container Runtime
```

Kubernetes：

```text
Container Orchestrator
```

Container 是 Docker 的核心。

Pod 是 Kubernetes 的核心。

Kubernetes 管理的是：

```text
Pod
```

不是：

```text
Container
```

---

# 用目前的平台理解

現在：

```text
Docker Compose

api
redis
postgres
```

未來：

```text
api Pod
└── api Container

redis Pod
└── redis Container

postgres Pod
└── postgres Container
```

目前每個 Pod 都只有一個 Container。

因此：

```text
Pod ≠ Container
```

只是目前：

```text
1 Pod = 1 Container
```

---

# Platform Evolution

目前：

```text
Docker Host
│
├── api Container
├── redis Container
└── postgres Container
```

未來：

```text
Kubernetes Cluster
│
├── api Pod
│     └── api Container
│
├── redis Pod
│     └── redis Container
│
└── postgres Pod
      └── postgres Container
```

---

# Interview Q&A

## Q1：Docker 和 Kubernetes 的差別？

Docker 負責建立與執行 Container。

Kubernetes 負責管理大量 Container，提供自動修復、擴展、排程與服務管理。

---

## Q2：為什麼 Docker Compose 不夠？

Docker Compose 適合單機開發。

當服務需要：

* 自動修復
* 自動擴展
* 高可用
* 多台主機管理

就需要 Kubernetes。

---

# 今日成果

建立 Kubernetes 最重要的基礎觀念：

```text
Docker
    │
    ▼
Container
```

以及：

```text
Kubernetes
    │
    ▼
Pod
```

理解：

* Docker 管理 Container。
* Kubernetes 管理 Pod。
* Kubernetes 透過 Desired State 維持平台運作。

---

# 下一步

Week6 Day2：

Pod Foundation

學習內容：

* Pod 是什麼
* Pod 與 Container 的差別
* Pod Lifecycle
* 第一個 Pod YAML
* 使用 kubectl 建立與查看 Pod
