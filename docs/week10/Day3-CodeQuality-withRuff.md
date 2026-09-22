<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day3 — Ruff 與程式品質

[上一課](<Day2-First-GitHub-ActionsCI-Pipeline.md>) · [本週目錄](README.md) · [下一課](<Day4-Pytest-API-Testing-Foundation.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 lint 結果敘述。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

CI fail 不等於自動禁止主分支合併，還要 repository branch protection／required checks，repo檔案無法證明已設定。Ruff 只檢查啟用規則，不保證安全／邏輯正確。

## 程式／設定與來源

本次核對：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)、[requirements-dev.txt](<../../requirements-dev.txt>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day3-CodeQuality-withRuff.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
CI Pass
```

原文列 import／check 問題但缺完整 run log，不作當前全repo lint通過聲明。

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

# Week10 Day3 - Code Quality with Ruff

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)：CI／映像建置與 GitOps 更新
- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [requirements-dev.txt](../../requirements-dev.txt)
- [requirements.txt](../../requirements.txt)

---

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
