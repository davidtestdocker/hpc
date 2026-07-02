# Week 3 Day 5－Docker Compose 與 Container 生命週期

## 今日目標

理解 Docker Compose 的用途，以及 Container 為什麼會持續執行或停止。

---

# Docker Compose

Docker Compose 用於管理多個相關服務（Services）。

透過 `compose.yaml` 可以描述整個平台需要啟動的 Container。

例如：

```yaml
services:
  monitor:
    image: hpc-monitor:v4
```

Docker Compose 會根據設定建立 Container。

---

# compose.yaml

Compose 描述的是 **Service**，不是 Container。

Container 是 Service 啟動後產生的執行實體。

---

# docker compose config

```bash
docker compose config
```

可驗證 compose.yaml 是否正確。

Docker Compose 也會自動建立預設 Network。

---

# docker compose up

```bash
docker compose up
```

作用：

- 建立 Network
- 建立 Container
- 啟動 Container

---

# Main Process

Container 的生命週期由 Main Process 決定。

例如：

```dockerfile
CMD ["ls","/app"]
```

流程：

```
ls

↓

執行完成

↓

Container 停止
```

---

改為：

```dockerfile
CMD ["tail","-f","/dev/null"]
```

流程：

```
tail

↓

持續等待

↓

Container 持續執行
```

---

# Docker Compose 與 Docker Run

docker run：

適合啟動單一 Container。

docker compose：

適合管理多個服務。

未來平台中的：

- FastAPI
- Monitoring
- Prometheus
- Grafana

都會透過 Compose 管理。

---

# 與 HPC AI Performance Engineering Platform 的關聯

目前平台：

```
Dockerfile
        │
        ▼
Image
        │
        ▼
Compose
        │
        ▼
Container
```

後續將加入：

- FastAPI
- Monitoring Framework
- Prometheus
- Grafana

共同組成完整平台。

---

# 今日重點

- Docker Compose 管理的是 Service。
- Compose 會建立 Container 與 Network。
- Container 的生命週期由 Main Process 決定。
- Main Process 持續執行，Container 就會持續 Running。
- Main Process 結束，Container 就會停止。
