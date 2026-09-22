<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day6 — CI 建置映像

[上一課](<Day5-Pytest-MockCI-Integration.md>) · [本週目錄](README.md) · [下一課](<Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 Docker build 敘述。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

非root是安全措施之一，不等於 production 等級認證。base tag 與部分套件未鎖digest/version；build成功不驗證啟動、憑據、服務依賴或漏洞。dockerignore 排除 build context 不必然影響最終未COPY檔案的映像體積。

## 程式／設定與來源

本次核對：[docker/Dockerfile](<../../docker/Dockerfile>)、[.dockerignore](<../../.dockerignore>)、[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day6-Docker-Build-inCI.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Docker Image Build 成功
```

保存原文build成功敘述，沒有本課image digest／完整build log；不重新build。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行測試入口為 pytest tests；mock／CI 與實機證據分開。GitOps 尚未對齊主 overlay。
> **閱讀順序**：先學本文基礎，再讀[Week10 現行對照與檢核](../learning-guide.md#week10)及[對應現行入口](../../tests/test_worker.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week10 Day6 - Docker Build in CI

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)：CI／映像建置與 GitOps 更新
- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [requirements.txt](../../requirements.txt)

---

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
