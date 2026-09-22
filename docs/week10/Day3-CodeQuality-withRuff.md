<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day3 — Ruff 與程式品質

[上一課](<Day2-First-GitHub-ActionsCI-Pipeline.md>) · [本週目錄](README.md) · [下一課](<Day4-Pytest-API-Testing-Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Lint 找出靜態問題，不會幫你證明 worker 恢復或 MPI 成功。整個 repo 的歷史程式可能採不同規範，因此 scoped lint 通過與 ruff check . 通過應分開描述。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
      - name: Ruff Lint

        run: |

          ruff check . --output-format=github


      - name: Run Pytest

        run: |

          python -m pytest

      - name: Login to Artifact Registry
        uses: docker/login-action@v4
        with:
          registry: asia-east1-docker.pkg.dev
          username: oauth2accesstoken
          password: ${{ steps.auth.outputs.access_token }}


      - name: Build Docker Image

        run: |
```

## 已有結果與解讀

### 已保存的本機驗證結果

2026-09-22 教材改寫時，在此 repo 開發環境執行並記錄：`53 passed`；三個 Helm charts lint 通過，完整主 overlay 離線渲染出 14 個物件。這是本機測試與渲染結果，**不是遠端 GitHub Actions 整條 CI 成功，也不是新雲端驗收**。

目前 CI 改的是 values-dev.yaml，主 overlay 使用獨立 api-values.yaml，因此不能說 push 一定更新主展示。下方完整保留原本課程與當時輸出；不要求你再跑一次 pytest。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week10/Day3-CodeQuality-withRuff.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
