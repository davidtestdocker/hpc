# Week10 Day1 - CI/CD Foundation

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
