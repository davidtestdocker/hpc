# Week 3 Day 7－Docker Integration

## 今日目標

整合 Week 3 Docker 學到的內容，確認 Docker 已經能支撐後續 FastAPI、Monitoring、Benchmark Worker、Prometheus、Grafana 等平台元件。

---

# Week 3 完整流程

本週建立了完整 Docker 工作流程：

```
Source Code
        │
        ▼
Dockerfile
        │
        ▼
docker build
        │
        ▼
Docker Image
        │
        ▼
docker compose
        │
        ▼
Container
        │
        ▼
Main Process
```

---

# 目前平台中的 Docker 元件

目前專案已包含：

```
docker/
└── Dockerfile

compose.yaml

monitoring/
└── process_monitor.py
```

目前已建立 Image：

```
hpc-monitor:v5
```

並可透過 Docker Compose 啟動 Monitoring Container。

---

# Dockerfile 的角色

Dockerfile 是 Image 的規格。

目前 Dockerfile 負責：

- 選擇 Base Image
- 安裝 Python
- 複製 Monitoring 程式
- 指定 Container 啟動時的 Main Process

---

# Image 的角色

Image 是 Container 的模板。

目前：

```
hpc-monitor:v5
```

是本專案第一個自製 Image。

它包含：

- Ubuntu Base
- Python
- monitoring/process_monitor.py

---

# Compose 的角色

Docker Compose 負責描述與啟動服務。

目前：

```yaml
services:
  monitor:
    image: hpc-monitor:v5
```

代表平台有一個 Monitoring Service。

未來會擴展為：

```yaml
services:
  api:
  monitor:
  prometheus:
  grafana:
  benchmark-worker:
```

---

# Main Process

Container 的生命週期由 Main Process 決定。

例如：

```dockerfile
CMD ["python3","/app/monitoring/process_monitor.py"]
```

代表 Container 啟動後會執行 Monitoring 程式。

如果程式結束，Container 也會結束。

---

# 與直接在 Ubuntu 執行的差異

如果直接在 Ubuntu 執行：

```bash
python3 monitoring/process_monitor.py
```

會依賴 Host VM 的 Python 與系統環境。

如果使用 Docker：

```
Docker Image
        │
        ▼
Container
```

則環境被打包進 Image。

優點：

- 環境一致
- 部署方式一致
- 相依套件隔離
- 易於擴充
- 易於交給 Kubernetes 管理

---

# 對 HPC AI Performance Engineering Platform 的意義

Docker 讓平台具備：

## 1. Consistency

同一個 Image 在不同環境中執行結果一致。

## 2. Deployability

服務可以透過 Compose 或 Kubernetes 部署。

## 3. Isolation

FastAPI、Monitoring、Prometheus、Grafana、Benchmark Worker 可各自擁有獨立環境。

## 4. Scalability

未來 Benchmark Worker 可以從 1 個 Container 擴展到多個 Container。

---

# Week 3 最終成果

本週完成：

- Docker Engine 安裝
- Docker Image 使用
- Container 生命週期理解
- Dockerfile 建立
- 自製 Image 建立
- Docker Compose 使用
- Monitoring Framework Container 化

目前平台已具備 Container Foundation。

---

# 下一週銜接

Week 4 將開始建立 FastAPI Benchmark API。

Docker 將繼續作為部署基礎：

```
FastAPI
        │
        ▼
Docker Image
        │
        ▼
Docker Compose
        │
        ▼
API Service
```

Week 4 的目標不是學 FastAPI，而是建立 Benchmark Platform 的 API Entry Point。
