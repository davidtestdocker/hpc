# Week4 Day5 - Dockerize API

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

