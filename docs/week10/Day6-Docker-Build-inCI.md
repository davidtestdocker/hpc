<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day6 — CI 建置映像

[上一課](<Day5-Pytest-MockCI-Integration.md>) · [本週目錄](README.md) · [下一課](<Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

docker build 產生 image，push 才上 registry，部署再引用 tag 或 digest。Git SHA tag 提供追溯性但不等於已經上線，且 image 內實際 source 仍需核對。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
      - name: Build Docker Image

        run: |

          docker build \
            -f docker/Dockerfile \
            -t asia-east1-docker.pkg.dev/project-4b82f780-0a12-4087-b94/hpc-images/hpc-api:${{ github.sha }} \
            .

      - name: Push Docker Image
        run: |
          docker push \
            asia-east1-docker.pkg.dev/project-4b82f780-0a12-4087-b94/hpc-images/hpc-api:${{ github.sha }}



      - name: Update Image Tag
        run: |
          sed -i "s/^  tag:.*/  tag: ${{ github.sha }}/" helm/api/values-dev.yaml
          cat helm/api/values-dev.yaml



      - name: Commit GitOps Changes
```

## 已有結果與解讀

### 已保存的本機驗證結果

2026-09-22 教材改寫時，在此 repo 開發環境執行並記錄：`53 passed`；三個 Helm charts lint 通過，完整主 overlay 離線渲染出 14 個物件。這是本機測試與渲染結果，**不是遠端 GitHub Actions 整條 CI 成功，也不是新雲端驗收**。

目前 CI 改的是 values-dev.yaml，主 overlay 使用獨立 api-values.yaml，因此不能說 push 一定更新主展示。下方完整保留原本課程與當時輸出；不要求你再跑一次 pytest。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week10/Day6-Docker-Build-inCI.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
