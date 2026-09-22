<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day5 — API 映像與啟動

[上一課](<day4-memory-queue.md>) · [本週目錄](README.md) · [下一課](<day6-monitoring-integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Uvicorn 載入 app 物件，容器啟動還需要相依套件及外部 DB／Redis 設定。Expose 或 containerPort 只是宣告，不會自動打開所有網路路徑。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[helm/api/templates/deployment.yaml](<../../helm/api/templates/deployment.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
        envFrom:
          - configMapRef:
              name: {{ include "api.fullname" . }}-config
          - secretRef:
              name: postgres-secret

        # 資源設定；Pod 中是 requests／limits，Kustomize 中是待組合的檔案清單。
        resources:
{{- toYaml .Values.resources | nindent 10 }}
        # 就緒探針决定 Pod 是否可接收 Service 流量。
        readinessProbe:
{{- toYaml .Values.readinessProbe | nindent 10 }}
        # 存活探針失敗達門檻時，kubelet 會重啟容器。
        livenessProbe:
{{- toYaml .Values.livenessProbe | nindent 10 }}
```

## 已有結果與解讀

### 自動工作驗收：已保存的真實結果

日期：2026-09-22T04:58:58.875811+00:00。環境：GKE hpc-gpu-sg，既有單 L4 叢集上的 **CPU MPI**，不是 GPU 訓練。

| 情境 | 保存的結果 | 怎麼解讀 |
|---|---|---|
| 正常工作 `f2d8df72-aef3-48bf-9d6b-6863523daa65` | `completed`；ranks `[0, 1, 2]` | 真實 MPI 程序啟動、完成並自動收回結果 |
| worker 重啟 `a697300a-b267-4554-bdd5-2c82bb9c9eda` | `completed`；同 job 的 JobSet 數 `1` | 停止期间 Kubernetes 已完成，worker 恢復後接續收集 |
| 模擬 dispatch 失敗 `0852fb7b-8efd-4600-b8ac-d4205554f6f3` | `failed`；retry_count `3` | 模擬提交分支耗盡重試，不是 MPI kernel crash |

正常工作的 launcher log 原文摘錄（只省略 SSH known-host warning）：

```text
RANK=0 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-0-0
RANK=1 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-1-0
RANK=2 HOST=mpi-f2d8df72-aef3-48bf-9d6b-6863523daa65-worker-2-0
```

驗收後的 queue 與手動端點結果，取自同份 JSON：

```json
{
  "database_status": {
    "a697300a-b267-4554-bdd5-2c82bb9c9eda": "completed",
    "f2d8df72-aef3-48bf-9d6b-6863523daa65": "completed",
    "0852fb7b-8efd-4600-b8ac-d4205554f6f3": "failed"
  },
  "queues": {
    "job_queue": [],
    "processing_queue": [],
    "dead_letter_queue": [
      "0852fb7b-8efd-4600-b8ac-d4205554f6f3"
    ]
  },
  "manual_endpoint_rejections": {
    "process-next": 409,
    "collect-mpi": 409,
    "recover-stuck": 409
  }
}
```

空 job_queue／processing_queue 表示本次驗收工作已清理；failed ID 留在 dead-letter。409 是自動模式刻意拒絕手動推進端點，並非 API 故障。這些結果不保證跨 DB 原子交易、Redis 全失恢復或 node failover。

來源：[完整原始驗收 JSON](<../evidence/automatic-worker-20260922.json>)。無須再提交一次工作。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week4/day5-dockerize-api.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 POST 提交／GET 查詢，MPI 由獨立 worker 執行；主 overlay 的手動 /worker/* 端點停用。
> **閱讀順序**：先學本文基礎，再讀[Week4 現行對照與檢核](../learning-guide.md#week4)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week4 Day5 - Dockerize API

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [compose.yaml](../../compose.yaml)：本機服務組合
- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [requirements.txt](../../requirements.txt)

---

## 今日平台增加什麼？

今天平台完成 **Docker 化部署** 的最後一塊，建立可配置（Configuration）與可攜帶（Portable）的 API。

平台流程由：

```text
Docker Image
    ↓
固定設定
```

進化成：

```text
Docker Compose
        ↓
Environment Variable
        ↓
Container
        ↓
FastAPI
```

平台開始具備多環境部署能力。

---

## 今日解決的 Platform Problem

同一份程式碼需要部署到：

```text
Development
QA
Stage
Production
```

每個環境都有不同設定，例如：

* APP_NAME
* Redis Host
* Database Host
* Log Level

如果把設定寫死在程式，每次換環境都需要修改程式並重新建置。

因此平台必須做到：

```text
Code
    ↓
Configuration
```

兩者完全分離。

---

## 今日知識鏈

```text
Application
      ↓
Configuration
      ↓
Environment Variable
      ↓
Docker Compose
      ↓
Container
      ↓
Container Network
```

---

## 今日實作

### 1. Compose Environment Variable

新增：

```yaml
environment:
  APP_NAME: HPC API Dev
```

Compose 啟動 Container 時，會自動將環境變數注入 Container。

---

### 2. Python 讀取設定

新增：

```python
import os

APP_NAME = os.getenv(
    "APP_NAME",
    "HPC AI Performance Engineering Platform"
)
```

並修改：

```python
app = FastAPI(
    title=APP_NAME,
    version="0.1.0"
)
```

平台不再將 APP 名稱寫死於程式。

---

### 3. Bind Mount（Volume）

Compose 新增：

```yaml
volumes:
  - ./api:/app/api
```

用途：

* Host 修改程式
* Container 直接讀取最新檔案
* 開發階段不用重新 Build Image

---

### 4. Docker Network

Compose 自動建立：

```text
hpc-ai-benchmark-platform_default
```

API Container 已加入此 Network。

未來 Redis 加入後：

```text
api
  │
Docker Network
  │
redis
```

Container 之間使用 **Service Name** 通訊，而不是固定 IP。

---

## 今日驗證

### Environment Variable

```bash
docker compose exec api env | grep APP_NAME
```

成功取得：

```text
APP_NAME=HPC API Dev
```

---

### OpenAPI Metadata

修改：

```yaml
APP_NAME: HPC API Dev
```

重新啟動後：

```bash
curl http://localhost:8000/openapi.json
```

OpenAPI Title 成功變更為：

```text
HPC API Dev
```

證明 FastAPI 已從 Environment Variable 讀取設定。

---

### Bind Mount

修改：

```text
api/main.py
```

重新建立 Container 後：

```bash
curl http://localhost:8000/
```

成功讀取最新程式內容，驗證 Bind Mount 生效。

---

### Docker Network

```bash
docker network inspect hpc-ai-benchmark-platform_default
```

確認：

* API Container 已加入 Network
* Docker 自動分配 IP
* 後續可透過 Service Name 通訊

---

## 今日平台架構

```text
Host
    │
    ▼
Compose
    │
    ├──────────────┐
    ▼              ▼
Environment     Bind Mount
    │              │
    ▼              ▼
Container      /app/api
    │
    ▼
FastAPI
    │
    ▼
Docker Network
```

---

## 今日學到的重點

* Code 與 Configuration 應完全分離。
* `os.getenv()` 可提供預設值，避免缺少環境變數導致程式啟動失敗。
* Bind Mount 適合開發環境，可直接使用 Host 最新程式碼。
* 修改 `compose.yaml`（例如新增 `volumes`）需要重新建立 Container 才會套用。
* Docker Compose 會建立專案專屬 Network，Container 可透過 Service Name 溝通，不需依賴固定 IP。

---

## 它最後會變成平台哪一部分？

今天建立的是 **Deployment Foundation**。

後續會一路演進：

```text
Docker Compose
      ↓
Redis
      ↓
PostgreSQL
      ↓
Kubernetes
      ↓
ConfigMap
      ↓
Secret
      ↓
Helm
      ↓
Argo CD
```

Day5 完成的是整個 HPC AI Performance Engineering Platform 的部署基礎。

---

## Interview

### Q1：為什麼平台要把 Configuration 與 Code 分離？

因為同一份程式需要部署到不同環境（Dev、QA、Stage、Production），若將設定寫死在程式中，每次換環境都必須修改程式並重新建置。透過 Environment Variable，可在不修改程式碼的情況下完成部署。

---

### Q2：為什麼 Container 不建議使用 `localhost` 連線到其他服務？

`localhost` 永遠代表目前 Container 自己。不同 Container 應透過 Docker Network 的 Service Name（例如 `redis`）互相通訊，而不是使用 `localhost` 或固定 IP。
