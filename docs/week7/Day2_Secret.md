<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day2 — Secret 與身份

[上一課](<Day1_ConfigMap.md>) · [本週目錄](README.md) · [下一課](<Day3_Resource_Requests_Limits_QoS.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 Secret 中繼資料示例。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

原文「Application 不再保存密碼」過度：connection.py 仍有開發用預設值，不能當正式憑據。Secret 可以承載真正密碼，不能將舊頁首「Secret 不應保存真實密碼」理解成禁止使用 Secret；禁止的是把真實 Secret 值提交 Git。Base64 不是加密；實際叢集 at-rest 設定需另核對，不能由 YAML 判定。

## 程式／設定與來源

本次核對：[api/database/connection.py](<../../api/database/connection.py>)、[helm/postgres/templates/secret.yaml](<../../helm/postgres/templates/secret.yaml>)、[k8s/postgres-secret.example.yaml](<../../k8s/postgres-secret.example.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day2_Secret.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
POSTGRES_PASSWORD  12 bytes
```

這是原文示例帳密的位元組數，不代表正式密碼安全、輪替或加密驗收；不重印或讀取環境真實密碼。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
