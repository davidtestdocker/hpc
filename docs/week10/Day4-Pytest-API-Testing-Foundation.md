<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day4 — pytest 與斷言

[上一課](<Day3-CodeQuality-withRuff.md>) · [本週目錄](README.md) · [下一課](<Day5-Pytest-MockCI-Integration.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史依賴失敗與現行測試。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

目前 test_api 直接呼叫 endpoint 函式，已不是文內 TestClient HTTP 測試；不驗證路由、中介層或 HTTP status。POST 現在先 DB後Redis，舊依賴錯誤順序不能當現行保證。

## 程式／設定與來源

本次核對：[tests/test_api.py](<../../tests/test_api.py>)、[tests/conftest.py](<../../tests/conftest.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day4-Pytest-API-Testing-Foundation.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
ConnectionError: redis:6379
```

保留當時 missing dependency 與 Redis錯誤；新增 fixtures 隔離依賴，不把替身成功當真實連線成功。

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
