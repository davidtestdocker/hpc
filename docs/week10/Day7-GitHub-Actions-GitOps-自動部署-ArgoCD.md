<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day7 — GitOps image tag 路徑

[上一課](<Day6-Docker-Build-inCI.md>) · [本週目錄](README.md) · [下一週](../week11/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

現有 CI 修改 helm/api/values-dev.yaml，主環境的 tag 在 gpu-sg-platform/api-values.yaml。兩者不是同一檔；不能說 push code 一定更新目前展示平台。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
      - name: Update Image Tag
        run: |
          sed -i "s/^  tag:.*/  tag: ${{ github.sha }}/" helm/api/values-dev.yaml
          cat helm/api/values-dev.yaml



      - name: Commit GitOps Changes
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"

          git add helm/api/values-dev.yaml

          git commit -m "chore: update image tag [skip ci]" || echo "No changes"

          git push
```

## 已有結果與解讀

### 已保存的本機驗證結果

2026-09-22 教材改寫時，在此 repo 開發環境執行並記錄：`53 passed`；三個 Helm charts lint 通過，完整主 overlay 離線渲染出 14 個物件。這是本機測試與渲染結果，**不是遠端 GitHub Actions 整條 CI 成功，也不是新雲端驗收**。

目前 CI 改的是 values-dev.yaml，主 overlay 使用獨立 api-values.yaml，因此不能說 push 一定更新主展示。下方完整保留原本課程與當時輸出；不要求你再跑一次 pytest。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week10/Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行測試入口為 pytest tests；mock／CI 與實機證據分開。GitOps 尚未對齊主 overlay。
> **閱讀順序**：先學本文基礎，再讀[Week10 現行對照與檢核](../learning-guide.md#week10)及[對應現行入口](../../tests/test_worker.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week10 Day7 - GitHub Actions + GitOps 自動部署

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)：CI／映像建置與 GitOps 更新
- [argocd/application-dev.yaml](../../argocd/application-dev.yaml)
- [helm/api/values-dev.yaml](../../helm/api/values-dev.yaml)
- [kustomize/overlays/dev/deployment-patch.yaml](../../kustomize/overlays/dev/deployment-patch.yaml)
- [kustomize/overlays/dev/kustomization.yaml](../../kustomize/overlays/dev/kustomization.yaml)

---

## 今日新增

今天完成整套 GitOps CI/CD Pipeline。

流程如下：

```
Developer
    │
git push
    │
    ▼
GitHub Actions
    │
    ├── Python Syntax Check
    ├── Ruff
    ├── Pytest
    ├── Docker Build
    ├── Push Artifact Registry
    ├── 更新 Helm Image Tag
    └── Commit & Push
             │
             ▼
        Git Repository
             │
             ▼
          Argo CD
             │
        Detect Change
             │
             ▼
          Auto Sync
             │
             ▼
      Kustomize + Helm
             │
             ▼
        Kubernetes
             │
             ▼
      Rolling Update
```

---

# GitHub Actions

Workflow

```
.github/workflows/ci.yml
```

完成流程：

```
Checkout

↓

Python Syntax Check

↓

Ruff

↓

Pytest

↓

Docker Build

↓

Push Artifact Registry

↓

更新 values-dev.yaml

↓

Git Commit

↓

Git Push
```

---

# Image 更新

GitHub Actions 使用

```
${{ github.sha }}
```

更新

```
helm/api/values-dev.yaml
```

例如

```yaml
image:
  tag: 07d197082a66...
```

---

# Argo CD

Application

```
hpc-dev
```

監控

```
master

↓

kustomize/overlays/dev
```

Git 有變更

↓

Argo CD Detect

↓

Sync

↓

Apply

↓

Healthy

---

# Kustomize

Argo CD Sync

↓

讀取

```

kustomize/overlays/dev

```

↓

Helm Render

```

helm/api
helm/postgres
helm/redis

```

↓

產生 Kubernetes YAML

---

# Rolling Update

Deployment Template 發生變化

↓

建立新的 ReplicaSet

↓

建立新的 Pod

↓

舊 Pod Terminate

↓

完成 Rolling Update

---

# PostgreSQL 修正

GKE Persistent Disk

根目錄存在

```

lost+found

```

PostgreSQL 初始化失敗

```

initdb:
directory exists but is not empty

```

新增

```yaml
- name: PGDATA
  value: /var/lib/postgresql/data/pgdata
```

Database 初始化位置

```

/var/lib/postgresql/data/pgdata

```

避免直接初始化於 Mount Root。

---

# Commands

查看 Application

```bash
kubectl get app -n argocd
```

查看 Deployment

```bash
kubectl get deployment -n hpc-platform-dev
```

查看 ReplicaSet

```bash
kubectl get rs -n hpc-platform-dev
```

查看 Pods

```bash
kubectl get pods -n hpc-platform-dev
```

查看 Image

```bash
kubectl get deployment api \
-n hpc-platform-dev \
-o jsonpath='{.spec.template.spec.containers[0].image}'
```

查看 Workflow

```
Actions
```

查看 Image Tag

```bash
cat helm/api/values-dev.yaml
```

---

# Interview

## Q1

GitHub Actions 更新哪個檔案後，Argo CD 才會偵測到 Git 變更？

**A：**

```
helm/api/values-dev.yaml
```

Image Tag 改變後，Git Commit Push。

Argo CD 發現 Git 與 Cluster 不一致，就會開始 Sync。

---

## Q2

Argo CD 如何知道要部署哪個 Helm Chart？

**A：**

Application 指向

```
kustomize/overlays/dev
```

Kustomize 讀取

```
kustomization.yaml
```

其中

```yaml
helmCharts:
  - name: api
  - name: postgres
  - name: redis
```

再到

```
helm/
```

找到對應 Chart Render 成 Kubernetes YAML，最後套用到 Cluster。

---

# 今日成果

✅ GitHub Actions CI

✅ Docker Build

✅ Push Artifact Registry

✅ 更新 Helm Image Tag

✅ Git Commit & Push

✅ Argo CD Auto Sync

✅ Helm + Kustomize Render

✅ Rolling Update

✅ PostgreSQL PGDATA 修正

✅ 完成完整 GitOps CI/CD Pipeline
