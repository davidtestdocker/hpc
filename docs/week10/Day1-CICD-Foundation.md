<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day1 — CI／CD 基礎

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-First-GitHub-ActionsCI-Pipeline.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：規劃與 workflow 靜態核對。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

完整圖是規劃；現行 workflow 沒有 image scan、部署後 health check 或 Terraform 步驟。Delivery 與無人工核准自動 Deployment 不應混成同義。觸發只涵蓋配置的 master push/PR。

## 程式／設定與來源

本次核對：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day1-CICD-Foundation.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Image Scan
```

建立 workflows 目錄不是整條 pipeline 成功證據；未保存本課 run ID。

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
