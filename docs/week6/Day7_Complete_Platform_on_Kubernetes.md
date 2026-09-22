<!-- readable-curriculum: 2026-09-22 -->
# Week6 Day7 — 完整平台驗收

[上一課](<Day6_Deploy_API_and_Redis.md>) · [本週目錄](README.md) · [下一週](../week7/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

rollout 只檢查 workload readiness；DB 初始化、RBAC、queue、JobSet 與結果回收需要不同驗收。全新 CPU bootstrap 與既有單 L4 的 MPI 驗收是兩組證據。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[scripts/deploy_platform.py](<../../scripts/deploy_platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def deploy(context, execute, output, require_gpu=True):
    # 每次都使用顯式 context；報告不保存 Secret、環境變數或 kubectl stderr。
    report = {"context": context, "execute": execute, "passed": False, "steps": []}
    base = ["kubectl", "--context", context, "--request-timeout=30s", "-n", NAMESPACE]

    def run(args, timeout=60):
        result = subprocess.run(base + args, cwd=ROOT, capture_output=True,
                                text=True, timeout=timeout, check=False)
        if result.returncode:
            raise RuntimeError(f"kubectl {args[0]} failed (exit {result.returncode})")
        return result.stdout

    def record(step):
        report["steps"].append(step)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(step, flush=True)

    try:
        report["preflight"] = inspect(context, require_gpu=require_gpu)
        if not report["preflight"]["passed"]:
            raise RuntimeError("前置檢查失敗，詳見 report.preflight")
        record("prerequisites passed")
        existing = run(["get", "deployment", "redis", "--ignore-not-found", "-o", "json"])
        validate_redis(json.loads(existing) if existing.strip() else None)
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week6/Day7_Complete_Platform_on_Kubernetes.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行主環境為 GKE hpc-gpu-sg；舊 K3s／手動 manifest 是學習歷史，不是主部署入口。
> **閱讀順序**：先學本文基礎，再讀[Week6 現行對照與檢核](../learning-guide.md#week6)及[對應現行入口](../runbooks/platform-bootstrap.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week6 Day7 - Complete Platform on Kubernetes

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-configmap.yaml](../../k8s/api-configmap.yaml)
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/api-service.yaml](../../k8s/api-service.yaml)
- [k8s/postgres-pvc.yaml](../../k8s/postgres-pvc.yaml)
- [k8s/postgres-secret.example.yaml](../../k8s/postgres-secret.example.yaml)
- [k8s/postgres-service.yaml](../../k8s/postgres-service.yaml)
- [k8s/postgres-statefulset.yaml](../../k8s/postgres-statefulset.yaml)
- [k8s/redis-deployment.yaml](../../k8s/redis-deployment.yaml)
- [k8s/redis-service.yaml](../../k8s/redis-service.yaml)

---

## 今日平台增加什麼

今天完成 HPC AI Benchmark Platform 的 Kubernetes 化。

平台從：

```text
Docker Compose
```

正式演進成：

```text
Kubernetes Platform
```

完成：

* PostgreSQL StatefulSet
* Persistent Volume Claim (PVC)
* PostgreSQL Service
* API ↔ Redis ↔ PostgreSQL 整合
* Rolling Update
* Platform Verification

---

# Platform Architecture

完成後平台架構：

```text
                     api-service
                          │
                    api Deployment
                          │
                      ReplicaSet
                          │
                          ▼
                      api Pod
                    /           \
                   ▼             ▼
          redis-service    postgres-service
                 │                  │
          redis Deployment    postgres StatefulSet
                 │                  │
             redis Pod         postgres-0
                                    │
                                    ▼
                             PersistentVolumeClaim
                                    │
                                    ▼
                             PersistentVolume
```

---

# 今日知識鏈

```text
StorageClass
      │
      ▼
PersistentVolumeClaim
      │
      ▼
PersistentVolume
      │
      ▼
StatefulSet
      │
      ▼
PostgreSQL
```

完成 Kubernetes Storage 與 Stateful Workload。

---

# Hands-on

## 1. 查看 StorageClass

執行：

```bash
kubectl get storageclass
```

結果：

```text
local-path (default)
```

Storage Provisioner：

```text
rancher.io/local-path
```

提供 Dynamic Provisioning。

---

## 2. 建立 PersistentVolumeClaim

建立：

```text
k8s/postgres-pvc.yaml
```

申請：

```text
1Gi
```

Storage。

第一次查看：

```bash
kubectl get pvc -n hpc-platform
```

狀態：

```text
Pending
```

原因：

StorageClass：

```text
WaitForFirstConsumer
```

等待 Pod 使用。

---

## 3. 建立 PostgreSQL StatefulSet

建立：

```text
k8s/postgres-statefulset.yaml
```

使用：

* postgres:16-alpine
* StatefulSet
* PVC
* volumeMount

資料掛載：

```text
/var/lib/postgresql/data
```

對應 Docker Compose：

```text
postgres_data:/var/lib/postgresql/data
```

---

## 4. PVC 自動 Bound

當 StatefulSet 建立 Pod：

```text
postgres-0
```

PVC：

由：

```text
Pending
```

變成：

```text
Bound
```

代表：

Dynamic Provisioning 成功。

---

## 5. 建立 PostgreSQL Service

建立：

```text
postgres-service
```

提供：

```text
ClusterIP
```

Service Discovery。

驗證：

```bash
kubectl get svc -n hpc-platform
kubectl get endpointslices -n hpc-platform
```

確認：

Service 已成功指向：

```text
postgres-0
```

---

## 6. 修改 API Database Connection

原本：

```text
postgres
```

修改：

```text
postgres-service
```

Kubernetes 內部：

透過 Service Name：

完成：

```text
DNS Service Discovery
```

---

## 7. Rolling Update

重新：

* Build Docker Image
* 匯入 K3s containerd
* Restart Deployment

執行：

```bash
kubectl rollout restart deployment api -n hpc-platform
```

驗證：

```bash
kubectl rollout status deployment api -n hpc-platform
```

結果：

```text
successfully rolled out
```

Deployment：

完成：

```text
Rolling Update
```

---

## 8. 驗證平台

API：

```bash
kubectl logs -n hpc-platform deployment/api
```

確認：

```text
Application startup complete
```

Redis：

```bash
curl http://localhost:8000/health/redis
```

成功：

```text
healthy
```

PostgreSQL：

第一次：

```sql
\dt
```

結果：

```text
Did not find any relations.
```

原因：

Kubernetes PostgreSQL 使用新的 Persistent Volume。

建立：

```sql
jobs
```

Table。

再次測試：

```bash
POST /benchmark
```

成功寫入：

* Redis
* PostgreSQL

---

# Platform Evolution

Week5：

```text
Docker Compose

api

redis

postgres
```

Week6：

```text
Kubernetes

Namespace

Deployment

Service

StatefulSet

PersistentVolumeClaim

PersistentVolume
```

平台正式遷移完成。

---

# 今日重點

## Deployment

適合：

* Stateless Application
* FastAPI
* Web API
* Backend

---

## StatefulSet

適合：

* PostgreSQL
* MySQL
* Redis Cluster
* Kafka
* MongoDB

提供：

* Stable Identity
* Stable Storage

---

## PVC

PVC：

不是 Storage。

PVC 是：

```text
Storage Request
```

真正 Storage：

來自：

```text
Persistent Volume
```

---

## Dynamic Provisioning

流程：

```text
PVC

↓

StorageClass

↓

Provisioner

↓

PV

↓

Pod
```

不用手動建立 PV。

---

# Interview Q&A

## Q1：Deployment 和 StatefulSet 有什麼差別？

Deployment 適合 Stateless Application，例如 API。

StatefulSet 適合 Stateful Application，例如 PostgreSQL。

StatefulSet 提供固定 Pod 名稱、固定 Storage 與穩定身分識別。

---

## Q2：為什麼 PVC 一開始是 Pending？

因為 K3s 預設 StorageClass 使用：

```text
WaitForFirstConsumer
```

PVC 會等 Pod 真正需要 Volume 時，才建立並綁定 Persistent Volume。

---

## Q3：為什麼 Kubernetes 的 PostgreSQL 沒有 jobs Table？

因為 Kubernetes 使用新的 Persistent Volume。

資料與 Docker Compose 的 Volume 完全獨立，因此需要重新建立 Schema 或透過 Migration 工具初始化資料庫。

---

# 今日成果

成功完成 HPC AI Benchmark Platform Kubernetes 化。

平台已包含：

* Namespace
* Deployment
* ReplicaSet
* Pod
* Service
* StatefulSet
* Persistent Volume Claim
* Persistent Volume
* Rolling Update
* Service Discovery
* API ↔ Redis ↔ PostgreSQL 整合

整個平台已可在 K3s Cluster 上正常運作。

---

# Week6 完成成果

完成 Kubernetes Foundation：

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
      │
      ▼
PersistentVolumeClaim
      │
      ▼
PersistentVolume
      │
      ▼
StatefulSet
```

並成功將 HPC AI Benchmark Platform 從 Docker Compose 遷移至 Kubernetes。

---

# 下一步

**Week7：Kubernetes Advanced**

內容包括：

* ConfigMap
* Secret
* Liveness Probe
* Readiness Probe
* Resource Requests / Limits
* Ingress（Traefik）
* Horizontal Pod Autoscaler（HPA）
* Kubernetes Debug Workflow
* 將平台提升至更接近生產環境的部署方式
