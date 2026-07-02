# Week 3 Day 2－安裝 Docker Engine

## 今日目標

在 Ubuntu VM 安裝 Docker 官方版本（Docker CE），讓平台具備 Container Runtime。

---

# 為什麼不用 Ubuntu Repository？

Ubuntu 提供：

- docker.io

本專案使用：

- Docker CE（Docker Community Edition）

原因：

- 官方維護
- 更新速度較快
- 與官方文件一致
- 支援最新功能

---

# 安裝流程

1. 確認系統沒有安裝舊版 Docker。
2. 安裝必要工具：

- ca-certificates
- curl
- gnupg
- lsb-release

3. 加入 Docker 官方 GPG Key。
4. 加入 Docker Official Repository。
5. 更新 Repository。
6. 安裝 Docker CE。

---

# 安裝套件

本次安裝：

- docker-ce
- docker-ce-cli
- containerd.io
- docker-buildx-plugin
- docker-compose-plugin

---

# 驗證

驗證 Docker：

```bash
docker --version
```

輸出：

```
Docker version 29.x.x
```

代表 Docker Engine 與 Docker CLI 可正常使用。

---

驗證 Docker Compose：

```bash
docker compose version
```

輸出：

```
Docker Compose version v5.x.x
```

代表 Docker Compose Plugin 已安裝完成。

---

# 今日重點

Docker Platform 並非只有一個套件，而是由多個元件組成：

- Docker Engine
- Docker CLI
- Container Runtime（containerd）
- Buildx
- Docker Compose

這些元件共同提供完整的 Container Platform。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的服務都將執行於 Docker Container，例如：

- Monitoring Framework
- FastAPI
- Prometheus
- Grafana
- Benchmark Worker
- vLLM

Docker Engine 負責建立與管理這些 Container。

Docker Compose 將負責多個服務的啟動與管理。

---

# 今日成果

平台已具備：

- Docker Engine
- Docker CLI
- Docker Compose

代表 HPC AI Performance Engineering Platform 已完成 Container Runtime 建置，可開始部署 Container。
