# Week10 Day6 - Docker Build in CI

## 今日目標

- 建立 Production 等級 Dockerfile
- 建立 .dockerignore
- 將 Docker Build 整合至 GitHub Actions
- 驗證專案可成功建置 Docker Image

---

# 今日成果

- 建立 `.dockerignore`
- 優化 Dockerfile
- 使用非 root User 執行 Container
- 新增 Python Runtime Environment Variables
- GitHub Actions 新增 Docker Build
- Docker Image Build 成功

---

# Dockerfile 優化

新增：

- 非 root User
- `PYTHONDONTWRITEBYTECODE`
- `PYTHONUNBUFFERED`
- 升級 pip
- Layer 最佳化
- `COPY --chown`
- `EXPOSE 8000`

---

# .dockerignore

用途：

避免不必要檔案進入 Build Context。

例如：

- .git
- .venv
- docs
- tests
- terraform
- __pycache__
- *.tfstate

減少 Build 時間與 Image 體積。

---

# Docker Build

Workflow 新增：

```bash
docker build \
    -f docker/Dockerfile \
    -t hpc-api:ci \
    .
```

作用：

驗證 Dockerfile 能成功建置 Image。

---

# Docker Build Context

```text
docker build .
```

`.`

代表：

目前專案目錄。

Docker 只能 COPY Build Context 內的檔案。

因此：

```
COPY requirements.txt .
```

才能正常找到檔案。

---

# CI Workflow

Git Push

↓

GitHub Actions

↓

Python Syntax Check

↓

Ruff

↓

Pytest

↓

Docker Build

↓

PASS

---

# 今日遇到的問題

### Dockerfile Parse Error

原因：

CMD JSON Array 寫法錯誤。

解法：

改為合法 Docker CMD Exec Form。

---

### Docker Build 成功

成功於：

- 本機 Build
- GitHub Actions Build

代表 Dockerfile 可於全新環境正常建置。

---

# Build vs Deploy

Build

- 建立 Docker Image
- 驗證 Dockerfile
- 驗證依賴
- 驗證專案可封裝

Deploy

- 將 Image 部署至 Kubernetes
- Rolling Update
- 提供服務

Day6 僅完成 Build。

---

# 今日重點

- Docker Build 為 CI 的重要驗證流程。
- .dockerignore 可減少 Build Context。
- Dockerfile 採用非 root User 提升安全性。
- GitHub Actions 已完成 Docker Image 自動建置。

---

# Interview Q&A

### Q1：為什麼 CI 要做 Docker Build？

確認專案可在全新的環境成功建置成 Docker Image，避免部署時才發現 Dockerfile、依賴或 COPY 路徑問題。

---

### Q2：.dockerignore 的用途？

限制 Build Context，避免無關檔案進入 Docker Build，降低建置時間、減少 Image 大小，並避免將敏感或開發環境檔案打包。

---

# 本日總結

完成 Production 等級 Dockerfile 與 .dockerignore，成功將 Docker Build 整合至 GitHub Actions，建立從程式碼驗證到 Docker Image 建置的完整 CI 流程。
