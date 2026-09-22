<!-- readable-curriculum: 2026-09-22 -->
# Week4 Day5 — API 映像與啟動

[上一課](<day4-memory-queue.md>) · [本週目錄](README.md) · [下一課](<day6-monitoring-integration.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史環境變數摘錄，現行 Compose 有差異。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

Bind mount 使檔案變更可見，不自動重載已載入的 Python；現行 Uvicorn CMD 沒有 --reload。更改容器環境變數需要重建容器，單純 restart 不套用新的 Compose 設定。現行 Compose 沒有獨立 worker；API 未設定 POSTGRES_HOST，而程式預設 postgres-service，與 Compose 服務 postgres 不符。不能把這份 Compose 稱為當前主平台完整可執行入口。localhost 是目前網路命名空間，不宜絕對說永遠只有一個容器。

## 程式／設定與來源

本次核對：[api/main.py](<../../api/main.py>)、[compose.yaml](<../../compose.yaml>)、[docker/Dockerfile](<../../docker/Dockerfile>)、[api/database/connection.py](<../../api/database/connection.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day5-dockerize-api.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
APP_NAME=HPC API Dev
```

這是舊文保存的 env 顯示值；現有 Compose 也設定相同 APP_NAME，API 用它設定 title，不代表根路由的 message 跟著改。

**仍缺的證據／不能證明的事：** 沒有現行 Compose 整體成功驗收；舊文未保存 network inspect 原始 JSON、容器 ID 或 OpenAPI 全文。本次只揭露差異，沒有啟動或更改服務。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
