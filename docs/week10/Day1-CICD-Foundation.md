<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day1 — CI／CD 基礎

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-First-GitHub-ActionsCI-Pipeline.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

測試、build、push image、改 GitOps tag 是不同階段，後兩者有外部副作用。workflow 可在 pull_request 觸發，不代表每個 PR 都應具備發佈權限；需要分開看事件和 permissions。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
permissions:
  contents: write
  id-token: write

# GitHub Actions 的工作清單，每個 job 可有自己的 runner。
jobs:

  test:

    runs-on: ubuntu-latest

    # 依序執行的步驟清單。
    steps:

      - name: Checkout Repository
        # 引用現成 GitHub Action，@ 後方是版本或提交。
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v3
        with:
```

## 已有結果與解讀

### 已保存的本機驗證結果

2026-09-22 教材改寫時，在此 repo 開發環境執行並記錄：`53 passed`；三個 Helm charts lint 通過，完整主 overlay 離線渲染出 14 個物件。這是本機測試與渲染結果，**不是遠端 GitHub Actions 整條 CI 成功，也不是新雲端驗收**。

目前 CI 改的是 values-dev.yaml，主 overlay 使用獨立 api-values.yaml，因此不能說 push 一定更新主展示。下方完整保留原本課程與當時輸出；不要求你再跑一次 pytest。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week10/Day1-CICD-Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行測試入口為 pytest tests；mock／CI 與實機證據分開。GitOps 尚未對齊主 overlay。
> **閱讀順序**：先學本文基礎，再讀[Week10 現行對照與檢核](../learning-guide.md#week10)及[對應現行入口](../../tests/test_worker.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week10 Day1 - CI/CD Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)：CI／映像建置與 GitOps 更新

---

## 今日目標

- 認識 CI/CD
- 了解 GitHub Actions 架構
- 建立 GitHub Actions 目錄
- 規劃 HPC AI Platform Pipeline

---

# 今日成果

- 建立 `.github/`
- 建立 `workflows/`
- 規劃完整 CI/CD Pipeline
- 理解 Workflow、Job、Step 關係

---

# GitHub Actions 目錄

```text
.github/
└── workflows/
```

GitHub 只會讀取：

```text
.github/workflows/
```

底下的 Workflow。

---

# CI 是什麼？

Continuous Integration（持續整合）。

每次：

```text
git push
```

都會自動：

- Build
- Test
- Lint
- 驗證程式

目的是盡早發現問題，降低多人開發整合成本。

---

# CD 是什麼？

Continuous Delivery / Continuous Deployment。

CI 成功後：

自動部署到：

- Development
- Stage
- Production

降低人工部署失誤。

---

# GitHub Actions

GitHub 內建的 CI/CD 平台。

可依事件（Event）自動執行：

- Build
- Test
- Docker
- Terraform
- Kubernetes Deploy
- Release

---

# GitHub Actions 架構

```text
Event
   │
   ▼
Workflow
   │
   ▼
Job
   │
   ▼
Step
   │
   ▼
Action / Script
```

---

# 我們專案最終 Pipeline

```text
Developer

↓

git push

↓

GitHub Actions

↓

Checkout Source

↓

Setup Python

↓

Install Dependency

↓

Lint

↓

Unit Test

↓

Docker Build

↓

Image Scan

↓

Push Artifact Registry

↓

Deploy Kubernetes

↓

Health Check

↓

Done
```

這就是 Week10 最終要完成的 CI/CD 流程。

---

# 為什麼要先建立 `.github/workflows`

GitHub Actions 只會自動偵測：

```text
.github/workflows/
```

中的 Workflow。

因此所有 Pipeline 都必須放在此目錄。

---

# 今日重點

- CI：自動驗證程式品質。
- CD：自動部署應用程式。
- GitHub Actions 由 Workflow、Job、Step 組成。
- CI/CD Pipeline 應由小到大逐步建立，而非一次完成。

---

# Interview Q&A

### Q1：CI 與 CD 有什麼差別？

CI 著重於程式整合與自動驗證；CD 著重於將通過驗證的程式自動部署到目標環境。

---

### Q2：GitHub Actions Workflow 必須放在哪裡？

必須放在：

```text
.github/workflows/
```

GitHub 才會自動偵測並執行。

---

### Q3：Workflow、Job、Step 的關係？

Workflow 是一條 Pipeline；Workflow 由多個 Job 組成；每個 Job 再由多個 Step 組成，Step 執行實際的 Action 或 Script。

---

# 本日總結

今天完成 GitHub Actions Foundation，建立 CI/CD 專案結構，理解 GitHub Actions 的執行流程，並完成 HPC AI Performance Platform 後續企業級 CI/CD Pipeline 的整體規劃。
