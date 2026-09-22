<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day4 — pytest 與斷言

[上一課](<Day3-CodeQuality-withRuff.md>) · [本週目錄](README.md) · [下一課](<Day5-Pytest-MockCI-Integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

test 用 assert 表達可檢查的契約，fixture 建立條件。只有測到的行為才有保障；一個 HTTP 測試成功不代表 real cluster 跑過。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[tests/test_api.py](<../../tests/test_api.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def test_root():
    body = root()

    assert body["message"] == "HPC API DEV"
    assert body["status"] == "running"


# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_benchmarks():
    body = list_benchmarks()

    assert "benchmarks" in body
    assert isinstance(body["benchmarks"], list)
    assert body["benchmarks"] == [
        "cpu",
        "memory",
        "disk_io",
        "mpi",
    ]

# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_submit_benchmark():
    body = create_benchmark(BenchmarkRequest(benchmark="cpu"))

```

## 已有結果與解讀

### 已保存的本機驗證結果

2026-09-22 教材改寫時，在此 repo 開發環境執行並記錄：`53 passed`；三個 Helm charts lint 通過，完整主 overlay 離線渲染出 14 個物件。這是本機測試與渲染結果，**不是遠端 GitHub Actions 整條 CI 成功，也不是新雲端驗收**。

目前 CI 改的是 values-dev.yaml，主 overlay 使用獨立 api-values.yaml，因此不能說 push 一定更新主展示。下方完整保留原本課程與當時輸出；不要求你再跑一次 pytest。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week10/Day4-Pytest-API-Testing-Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行測試入口為 pytest tests；mock／CI 與實機證據分開。GitOps 尚未對齊主 overlay。
> **閱讀順序**：先學本文基礎，再讀[Week10 現行對照與檢核](../learning-guide.md#week10)及[對應現行入口](../../tests/test_worker.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week10 Day4 - Pytest API Testing Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)：CI／映像建置與 GitOps 更新
- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [requirements-dev.txt](../../requirements-dev.txt)
- [requirements.txt](../../requirements.txt)
- [tests/conftest.py](../../tests/conftest.py)
- [tests/test_api.py](../../tests/test_api.py)

---

## 今日目標

- 建立 Python Virtual Environment
- 建立第一個 API 測試
- 學習 Pytest
- 使用 TestClient 測試 FastAPI

---

# 今日成果

- 建立 `.venv`
- 安裝 Runtime 與 Development Dependencies
- 建立 `tests/test_api.py`
- 完成 GET `/` 測試
- 完成 GET `/benchmarks` 測試
- 完成 POST `/benchmark` 測試（Redis Dependency 發現）

---

# Python Virtual Environment

建立：

```bash
python3 -m venv .venv
```

啟用：

```bash
source .venv/bin/activate
```

安裝：

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

---

# Pytest

執行：

```bash
python -m pytest
```

Pytest 會自動搜尋：

- `tests/`
- `test_*.py`
- `test_*()` 函式

---

# TestClient

```python
client = TestClient(app)
```

TestClient 不需要：

- Uvicorn
- localhost:8000
- HTTP Server

直接呼叫 FastAPI `app` 進行 API 測試。

---

# assert

```python
assert response.status_code == 200
```

`assert` 用來驗證條件是否成立。

成立：

```
Pass
```

不成立：

```
AssertionError
```

---

# API Test

完成：

- GET `/`
- GET `/benchmarks`

新增：

- POST `/benchmark`

驗證：

- HTTP Status
- Response Body
- API Contract

---

# 今日遇到的問題

### 1.

```
ModuleNotFoundError: No module named 'fastapi'
```

原因：

未安裝 Runtime Dependency。

解法：

```
pip install -r requirements.txt
```

---

### 2.

```
ModuleNotFoundError: No module named 'api'
```

原因：

在 `tests/` 目錄執行 `pytest`。

解法：

於專案根目錄執行：

```bash
python -m pytest
```

---

### 3.

```
ConnectionError: redis:6379
```

原因：

POST `/benchmark` 依賴 Redis。

本機 Pytest 未連接 Docker Compose 的 Redis。

此問題將於 Day5 使用 Mock 或測試環境解決。

---

# 今日重點

- `.venv` 提供專案隔離的 Python 環境。
- Runtime 與 Development Dependency 應分離管理。
- `python -m pytest` 使用目前 Python 環境執行測試。
- TestClient 可直接測試 FastAPI，不需啟動 Uvicorn。
- API 測試會驗證 Response 是否符合 API Contract。

---

# Interview Q&A

### Q1：為什麼要使用 `.venv`？

避免不同專案的 Python 套件互相衝突，每個專案擁有獨立的執行環境。

---

### Q2：為什麼使用 TestClient 而不是 curl？

TestClient 直接呼叫 FastAPI `app`，不需要啟動 HTTP Server，速度快且適合單元測試。

---

# 本日總結

今天完成 HPC AI Performance Platform 第一個 API 自動化測試，建立 Python Virtual Environment、導入 Pytest 與 TestClient，成功驗證 GET API，並透過 POST `/benchmark` 測試發現 Redis 外部依賴，為後續 Mock 與整合測試奠定基礎。
