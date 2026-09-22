<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day2 — GitHub Actions workflow

[上一課](<Day1-CICD-Foundation.md>) · [本週目錄](README.md) · [下一課](<Day3-CodeQuality-withRuff.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 CI Success 敘述。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

Node runtime 警告只保留為當時訊息，不推定目前 GitHub runner 狀況。現行 workflow 先進行 GCP auth，已不是單純離線 syntax CI；compileall 範圍 api monitoring，不覆蓋所有專案。

## 程式／設定與來源

本次核對：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)、[requirements.txt](<../../requirements.txt>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day2-First-GitHub-ActionsCI-Pipeline.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Node.js 20 is deprecated
```

Success 是文內敘述，沒有 job URL／log；依賴未完全釘版，乾淨 runner 不等於永久可重現。

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

# Week10 Day2 - First GitHub Actions CI Pipeline

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)：CI／映像建置與 GitOps 更新
- [requirements.txt](../../requirements.txt)

---

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
