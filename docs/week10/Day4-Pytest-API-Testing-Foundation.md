# Week10 Day4 - Pytest API Testing Foundation

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
