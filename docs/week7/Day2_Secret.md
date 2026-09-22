<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day2 — Secret 與身份

[上一課](<Day1_ConfigMap.md>) · [本週目錄](README.md) · [下一課](<Day3_Resource_Requests_Limits_QoS.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

DB 密碼 Secret 與 Kubernetes serviceAccount 是兩種不同憑證用途。Secret 名称存在不代表內容正確，也不要在教學或證據中印出真實值。

## 在現在的專案中

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
            - secretRef:
                name: postgres-secret
          resources:
            # requests 供排程器計算容量，limits 限制容器 CPU／記憶體上限。
            {{- toYaml .Values.worker.resources | nindent 12 }}
{{- end }}
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week7/Day2_Secret.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 API 與 worker 分開部署；API HPA 不等於 worker 擴縮，Secret 不應保存真實密碼。
> **閱讀順序**：先學本文基礎，再讀[Week7 現行對照與檢核](../learning-guide.md#week7)及[對應現行入口](../../helm/api/templates/worker.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week7 Day2 - Secret

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

實際 `postgres-secret.yaml` 不納入版本控制，提供可追蹤的 example 與 Helm 模板連結。

- [api/database/connection.py](../../api/database/connection.py)：資料庫連線
- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [helm/postgres/templates/secret.yaml](../../helm/postgres/templates/secret.yaml)
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/postgres-secret.example.yaml](../../k8s/postgres-secret.example.yaml)

---

## 今日平台增加什麼

今天平台新增：

```text
Secret
```

將 PostgreSQL 帳號與密碼從程式碼與 Deployment 中分離，改由 Kubernetes Secret 管理。

平台設定正式分成兩類：

* ConfigMap：非敏感設定
* Secret：敏感設定

---

# Platform Problem

原本資料庫連線資訊直接寫在程式中：

```text
POSTGRES_USER=hpc
POSTGRES_PASSWORD=hpc_password
```

這種做法會造成：

* 密碼出現在 Git Repository
* 密碼出現在程式碼
* 密碼難以更換
* 多環境管理困難

因此需要將敏感資訊抽離。

---

# 今日知識鏈

```text
ConfigMap
      │
      ├── REDIS_HOST
      ├── REDIS_PORT
      ├── POSTGRES_HOST
      ├── POSTGRES_PORT
      └── POSTGRES_DB

Secret
      │
      ├── POSTGRES_USER
      └── POSTGRES_PASSWORD

            │
            ▼

      Pod Environment

            │
            ▼

      Python os.getenv()

            │
            ▼

      SQLAlchemy Engine
```

---

# Secret 是什麼？

Secret 用來保存：

* Password
* API Key
* Token
* JWT Secret
* Certificate

而不是：

* Host
* Port
* Database Name

---

# Base64 ≠ Encryption

建立 Secret 前：

```bash
echo -n "hpc" | base64

echo -n "hpc_password" | base64
```

結果：

```text
POSTGRES_USER
aHBj

POSTGRES_PASSWORD
aHBjX3Bhc3N3b3Jk
```

注意：

Kubernetes Secret 預設只是：

```text
Base64 Encoding
```

不是加密。

真正企業通常還會搭配：

* Encryption at Rest
* KMS
* Vault
* External Secrets Operator

---

# Hands-on

## 1. 建立 Secret

建立：

```text
k8s/postgres-secret.yaml
```

內容：

```yaml
apiVersion: v1
kind: Secret

metadata:
  name: postgres-secret
  namespace: hpc-platform

type: Opaque

data:
  POSTGRES_USER: aHBj
  POSTGRES_PASSWORD: aHBjX3Bhc3N3b3Jk
```

部署：

```bash
kubectl apply -f k8s/postgres-secret.yaml
```

---

## 2. 驗證 Secret

查看：

```bash
kubectl get secret -n hpc-platform
```

查看內容：

```bash
kubectl describe secret postgres-secret -n hpc-platform
```

結果：

```text
POSTGRES_USER      3 bytes
POSTGRES_PASSWORD  12 bytes
```

Kubernetes 不會直接顯示真正內容。

---

## 3. 修改 API Deployment

Deployment 原本：

```yaml
envFrom:
  - configMapRef:
      name: api-config
```

修改成：

```yaml
envFrom:
  - configMapRef:
      name: api-config

  - secretRef:
      name: postgres-secret
```

重新部署：

```bash
kubectl apply -f k8s/api-deployment.yaml

kubectl rollout status deployment api -n hpc-platform
```

---

## 4. 驗證 Pod

查看：

```bash
kubectl describe pod -n hpc-platform -l app=api
```

確認：

```text
Environment Variables from:

api-config

postgres-secret
```

代表 Pod 同時讀取：

* ConfigMap
* Secret

---

## 5. 修改 Python 程式

修改：

```text
api/database/connection.py
```

原本：

```python
DATABASE_URL = (
    "postgresql+psycopg2://"
    "hpc:hpc_password@postgres-service:5432/hpc_platform"
)
```

修改：

```python
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres-service")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hpc_platform")
POSTGRES_USER = os.getenv("POSTGRES_USER", "hpc")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hpc_password")

DATABASE_URL = (
    "postgresql+psycopg2://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DB}"
)
```

Application 不再直接保存密碼。

---

## 6. 重新部署 API

重新：

```bash
docker build -f docker/Dockerfile \
-t hpc-ai-benchmark-platform-api:latest .

docker save hpc-ai-benchmark-platform-api:latest \
| sudo k3s ctr images import -

kubectl rollout restart deployment api -n hpc-platform
```

Deployment 完成：

```text
Rolling Update
```

---

## 7. 驗證平台

查看：

```bash
kubectl logs -n hpc-platform deployment/api
```

確認：

```text
Application startup complete
```

驗證：

```bash
curl http://localhost:8000/health/redis

POST /benchmark
```

結果：

* Redis 正常
* PostgreSQL 正常
* SQLAlchemy 正常
* Secret 成功提供資料庫帳號與密碼

平台功能正常。

---

# 平台架構

```text
                 ConfigMap
                     │
                     │
                 Secret
                     │
                     ▼
              api Deployment
                     │
                     ▼
                  api Pod
                     │
             Python os.getenv()
                     │
                     ▼
             SQLAlchemy Engine
                /           \
               ▼             ▼
        redis-service   postgres-service
```

---

# 今日重點

* ConfigMap 保存非敏感設定。
* Secret 保存敏感設定。
* Secret 預設只是 Base64，不是加密。
* Application 應透過環境變數取得帳號密碼。
* 程式碼中不應硬寫密碼。

---

# Interview Q&A

## Q1：ConfigMap 和 Secret 差在哪？

ConfigMap 保存非敏感設定，例如 Host、Port、Database Name。

Secret 保存敏感資訊，例如 Password、Token、API Key。

---

## Q2：Kubernetes Secret 有加密嗎？

預設沒有。

Secret 預設只做 Base64 Encoding。

若需要真正加密，通常搭配 Encryption at Rest、KMS、Vault 或 External Secrets。

---

## Q3：為什麼程式還保留 `os.getenv()` 的預設值？

預設值可讓開發環境（例如 Docker Compose、本機測試）在未提供環境變數時仍可執行。

正式部署到 Kubernetes 時，ConfigMap 與 Secret 會提供實際值並覆蓋預設值。

---

# 今日成果

平台正式完成設定與敏感資訊分離：

```text
Application
        │
        ├── ConfigMap
        └── Secret
                │
                ▼
           Environment
                │
                ▼
         SQLAlchemy Engine
```

這是 Kubernetes 應用程式最常見的企業部署模式之一。

---

# 下一步

**Week7 Day3：Resource Requests、Limits 與 QoS**

學習如何限制 CPU、Memory 使用量，避免單一 Pod 耗盡整個 Node 的資源，並理解 Kubernetes 如何根據 Requests 與 Limits 進行排程與資源管理。
