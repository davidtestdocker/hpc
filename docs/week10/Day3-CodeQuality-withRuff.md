# Week10 Day3 - Code Quality with Ruff

## 今日目標

- 導入 Ruff
- 建立 Code Quality Gate
- 將 Ruff 整合至 GitHub Actions
- 自動阻擋不符合規範的程式碼

---

# 今日成果

- 建立 `requirements-dev.txt`
- 導入 Ruff
- GitHub Actions 自動執行 Ruff
- 修正 Ruff 偵測出的程式碼問題
- 第二版 CI Pipeline 建立完成

---

# requirements-dev.txt

```text
ruff
pytest
```

---

# 為什麼要建立 requirements-dev.txt

Python 專案通常會區分：

## Runtime Dependency

```text
requirements.txt
```

正式程式執行需要的套件：

- FastAPI
- Uvicorn
- Redis
- SQLAlchemy

Docker Image 只需要這些。

---

## Development Dependency

```text
requirements-dev.txt
```

只提供：

- Ruff
- Pytest
- Black
- Mypy

這些工具不需要部署到正式環境。

---

# 更新 GitHub Actions

新增：

```yaml
- name: Ruff Lint

  run: |

    ruff check . --output-format=github
```

CI Pipeline：

```text
Push

↓

Checkout Repository

↓

Setup Python

↓

Install Dependencies

↓

Python Syntax Check

↓

Ruff Lint

↓

Success
```

---

# Ruff 是什麼？

Ruff 是目前 Python 最常使用的 Linter 之一。

主要功能：

- Import 排序
- 未使用 Import
- 未使用變數
- Coding Style
- 潛在 Bug
- Python Best Practice

速度比傳統 flake8、pylint 更快。

---

# GitHub Annotation

使用：

```bash
ruff check . --output-format=github
```

若有錯誤：

GitHub Actions 會直接在 Pull Request 或 Workflow 中標示：

```text
api/main.py

Line 12

Unused import
```

方便快速定位問題。

---

# 本次修正內容

Ruff 偵測：

```text
Import block is un-sorted

Unused import

subprocess.run without explicit check
```

修正後：

```text
CI Pass
```

---

# Code Quality Gate

目前 CI：

```text
Push
    │
    ▼
Syntax Check
    │
    ▼
Ruff
    │
    ▼
Pass
```

如果 Ruff 發現問題：

```text
Push
    │
    ▼
Ruff
    │
    ▼
Fail
```

Pipeline 將立即停止。

---

# 為什麼要先跑 Ruff？

企業 Pipeline：

```text
Checkout

↓

Install

↓

Lint

↓

Unit Test

↓

Docker Build

↓

Deploy
```

原因：

Lint 執行速度最快。

若程式碼品質已不符合規範，就不需要浪費時間進行 Build 或 Deploy。

---

# CI 演進

## Day2

```text
Push

↓

Syntax Check
```

---

## Day3

```text
Push

↓

Syntax Check

↓

Ruff Lint
```

開始具備程式碼品質檢查能力。

---

# GitHub Actions 成功驗證

本次 Workflow：

✅ Checkout Repository

✅ Setup Python

✅ Install Dependencies

✅ Python Syntax Check

✅ Ruff Lint

Workflow：

```text
Success
```

---

# 今日重點

- Runtime 與 Development Dependency 應分離管理。
- Ruff 可在 CI 自動檢查程式碼品質。
- GitHub Annotation 可直接標示錯誤位置。
- Code Quality Gate 可阻止不符合規範的程式碼進入主分支。

---

# Interview Q&A

### Q1：為什麼 Ruff 不放在 requirements.txt？

因為 Ruff 只用於開發與 CI，不屬於正式執行環境的 Runtime Dependency。

---

### Q2：為什麼 CI 要先跑 Ruff？

Lint 執行速度快，可快速攔截低品質程式碼，避免浪費時間進行 Test、Build 或 Deploy。

---

### Q3：`--output-format=github` 的用途？

讓 Ruff 的檢查結果以 GitHub Annotation 形式呈現，直接在 Workflow 或 Pull Request 標示錯誤位置，提高除錯效率。

---

# 本日總結

今天完成 HPC AI Performance Platform 第二版 CI Pipeline，導入 Ruff 作為程式碼品質檢查工具，建立 Code Quality Gate，並成功整合 GitHub Annotation。專案已具備自動化語法驗證與程式碼品質檢查能力，符合企業 CI 的基本實務。
