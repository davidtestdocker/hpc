# Week 3 Day 4－Dockerfile 與建立自己的 Image

## 今日目標

學會使用 Dockerfile 建立自己的 Docker Image，而不是只使用官方 Image。

---

# Dockerfile

Dockerfile 是建立 Docker Image 的規格（Specification）。

Docker 會依照 Dockerfile 的內容建立新的 Image。

---

# FROM

```dockerfile
FROM ubuntu:24.04
```

指定 Base Image。

新的 Image 會建立在 ubuntu:24.04 之上。

---

# COPY

```dockerfile
COPY monitoring /app/monitoring
```

將本機的 `monitoring` 目錄複製到 Image 中。

注意：

COPY 發生在 Build 階段，而不是 Run 階段。

---

# docker build

```bash
docker build -f docker/Dockerfile -t hpc-monitor:v2 .
```

作用：

- 讀取 Dockerfile
- 建立新的 Image
- 將 Image 命名為 `hpc-monitor:v2`

---

# Build Context

本次使用：

```bash
.
```

代表 Build Context 為整個專案根目錄。

因此 Dockerfile 可以存取：

- monitoring/
- docker/
- docs/

如果 Context 設定錯誤，COPY 將找不到檔案。

---

# docker history

使用：

```bash
docker history hpc-monitor:v2
```

可以查看 Image 的 Layer。

本次新增：

```
COPY monitoring /app/monitoring
```

代表 Image 新增了一個 Layer。

---

# Image 與 Container

流程如下：

```
Source Code
        │
        ▼
docker build
        │
        ▼
Image
        │
docker run
        ▼
Container
```

Container 中可以看到：

```
/app/monitoring/process_monitor.py
```

代表程式已經被打包進 Image。

---

# 今日重點

- Dockerfile 是 Image 的規格。
- FROM 指定 Base Image。
- COPY 將本機檔案打包進 Image。
- docker build 建立新的 Image。
- docker history 可查看 Image Layer。
- Build 與 Run 是不同階段。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- Monitoring
- FastAPI
- Analysis
- Benchmark Worker

都會有自己的 Dockerfile。

CI/CD 流程：

```
修改程式
        │
        ▼
docker build
        │
        ▼
Image
        │
        ▼
Container
```

這也是 GitHub Actions 自動建置 Image 的基礎。
