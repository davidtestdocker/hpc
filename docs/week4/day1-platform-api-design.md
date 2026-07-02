# Week4 Day1 - Platform API Design

## 今日目標

建立 **HPC AI Performance Engineering Platform** 的第一個 API 入口。

平台從只能執行本機 Python Script：

```text
User
  ↓
python monitoring/process_monitor.py
```

進化成：

```text
Client / Browser
        ↓
      HTTP
        ↓
    FastAPI API
        ↓
HPC AI Performance Engineering Platform
```

---

# 今日完成內容

## 1. 建立 Python 套件管理

建立 `requirements.txt`

```text
fastapi
uvicorn[standard]
```

目的：

* 統一管理 Python 相依套件
* Docker Image 可重複建置
* 不依賴 VM 本機環境

---

## 2. 修改 Dockerfile

改為使用：

```dockerfile
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt
```

目的：

* Image 建構時安裝套件
* 不在 Host 安裝 Python 套件
* 建立可重現的 Runtime

---

## 3. 修改 Docker Compose

建立 API Service

```yaml
services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
```

目的：

* 建立 API Container
* 對外開放 8000 Port

---

## 4. 建立第一個 FastAPI

建立：

```text
api/main.py
```

提供第一個 API：

```text
GET /
```

回傳：

```json
{
  "message": "HPC AI Performance Engineering Platform API",
  "status": "running"
}
```

---

## 5. 建立 API Runtime

完成：

```bash
docker compose build
docker compose up -d
```

成功建立：

```text
hpc-ai-benchmark-platform-api
```

---

## 6. 驗證 API

成功驗證：

```bash
curl http://localhost:8000/
```

成功回傳 JSON。

---

## 7. 驗證 Swagger

成功：

```text
http://localhost:8000/docs
```

FastAPI 自動產生 Swagger UI。

---

## 8. 驗證 OpenAPI

成功：

```text
http://localhost:8000/openapi.json
```

確認 API Contract 已建立。

---

# 今日平台架構

```text
Client
    │
 HTTP Request
    │
    ▼
Docker Container
    │
    ▼
Uvicorn
    │
    ▼
FastAPI
    │
    ▼
GET /
    │
    ▼
JSON Response
```

---

# 今日知識重點

```text
Platform
    ↓
API
    ↓
HTTP
    ↓
FastAPI
    ↓
OpenAPI
    ↓
Swagger
```

今天建立的是整個平台的 **API Control Plane**，未來會一路串接：

```text
API
 ↓
Redis Queue
 ↓
Worker
 ↓
Benchmark
 ↓
Monitoring
 ↓
Analysis
```

---

# Interview

### Q1：為什麼平台需要 API，而不是直接執行 Python Script？

因為平台需要讓 Browser、CI/CD、Worker、Dashboard 等外部系統透過 HTTP 呼叫功能，而不是登入主機執行 Python 程式，因此需要 API 作為平台的對外入口。

---

### Q2：`docker compose build` 與 `docker compose up` 有什麼不同？

`docker compose build` 依照 Dockerfile 建立 Image；`docker compose up` 則使用 Image 啟動 Container。Build 是建構執行環境，Up 是執行服務。

