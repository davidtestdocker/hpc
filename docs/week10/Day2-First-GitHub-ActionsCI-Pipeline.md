# Week10 Day2 - First GitHub Actions CI Pipeline

## 今日目標

- 建立第一條 GitHub Actions CI Pipeline
- 自動驗證 Python 專案
- 成功觸發 GitHub Actions
- 理解 Workflow 執行流程

---

# 今日成果

- 建立 `ci.yml`
- 成功觸發 GitHub Actions
- 自動建立 GitHub Runner
- 自動安裝 Python 3.12
- 自動安裝 Project Dependency
- 自動完成 Python Syntax Check

---

# 專案架構

```text
.github/
└── workflows/
    └── ci.yml
```

---

# CI Workflow

```text
Git Push
    │
    ▼
GitHub Actions
    │
    ▼
Checkout Repository
    │
    ▼
Setup Python
    │
    ▼
Install Dependencies
    │
    ▼
Python Syntax Check
    │
    ▼
Success
```

---

# Workflow 結構

```yaml
Workflow
│
├── Trigger (on)
│
└── Job
      │
      └── Step
            │
            ├── Checkout
            ├── Setup Python
            ├── Install Dependency
            └── Syntax Check
```

---

# Workflow 說明

## name

Workflow 名稱。

GitHub Actions 頁面會顯示：

```text
CI
```

---

## on

Workflow Trigger。

目前：

- push → master
- pull_request → master

代表 Push 或 Pull Request 到 master 時自動執行。

---

## jobs

一個 Workflow 可以包含多個 Job。

目前只有：

```text
test
```

---

## runs-on

```text
ubuntu-latest
```

GitHub 每次都會建立一台全新的 Ubuntu Runner 執行 Workflow。

Workflow 結束後 Runner 立即銷毀。

---

## steps

Job 的執行流程。

依照順序：

1. Checkout Repository
2. Setup Python
3. Install Dependencies
4. Python Syntax Check

後面的 Step 可使用前面 Step 建立的環境。

---

# uses 與 run

## uses

使用 GitHub 官方或第三方 Action。

例如：

```yaml
uses: actions/checkout@v4
```

代表使用官方 Checkout Action。

---

## run

直接在 Runner 執行 Shell Command。

例如：

```bash
pip install -r requirements.txt
```

---

# Checkout Repository

Runner 建立時沒有任何程式碼。

Checkout：

```text
GitHub Repository
        │
        ▼
GitHub Runner
```

將目前 Commit 下載至 Runner。

---

# Setup Python

建立：

```text
Python 3.12
```

執行環境。

保持與專案 Docker Runtime 一致。

---

# Install Dependencies

依照：

```text
requirements.txt
```

安裝：

- FastAPI
- Uvicorn
- Redis
- SQLAlchemy
- PostgreSQL Driver

等所有專案依賴。

---

# Python Syntax Check

使用：

```bash
python -m compileall
```

檢查：

- SyntaxError
- IndentationError
- 無法編譯的 Python 檔案

不會執行程式，只驗證語法是否合法。

---

# GitHub Runner

GitHub 每次 Workflow：

```text
建立 Runner

↓

執行 Workflow

↓

刪除 Runner
```

因此每次 CI 都是乾淨環境。

避免：

```text
我電腦可以跑
CI 卻失敗
```

或

```text
CI 可以跑
正式環境失敗
```

---

# Warning

本次 Workflow 出現：

```text
Node.js 20 is deprecated
```

原因：

GitHub Runner 已升級至 Node.js 24。

官方 Action：

- actions/checkout
- actions/setup-python

目前仍相容執行。

不影響 Workflow。

---

# 驗證結果

GitHub Actions：

✅ Checkout Repository

✅ Setup Python

✅ Install Dependencies

✅ Python Syntax Check

Workflow：

```text
Success
```

---

# 今日重點

- GitHub Actions 透過 Trigger 自動啟動 Workflow。
- Workflow 由 Job 組成。
- Job 由多個 Step 組成。
- 每次 Workflow 都使用全新的 GitHub Runner。
- CI 成功代表專案可在乾淨環境完成基本驗證。

---

# Interview Q&A

### Q1：GitHub Runner 是什麼？

GitHub 提供的臨時執行環境，每次 Workflow 都會建立新的 Runner，完成後立即銷毀，確保 CI 在乾淨環境中執行。

---

### Q2：`uses` 與 `run` 有什麼差別？

`uses` 用來使用現成的 GitHub Action；`run` 用來直接執行 Shell 指令。

---

### Q3：為什麼 CI 要在全新的 Runner 執行？

避免依賴開發者本機環境，確保任何人、任何時間都能在一致環境驗證程式，提高 CI 的可靠性。

---

# 本日總結

今天完成 HPC AI Performance Platform 第一條 GitHub Actions CI Pipeline。專案已具備自動化驗證能力，每次 Push 或 Pull Request 到 master 時，GitHub 會自動建立乾淨的 Ubuntu Runner，完成程式碼下載、Python 環境建立、依賴安裝與 Python 語法驗證，正式建立企業 CI 的第一階段。
