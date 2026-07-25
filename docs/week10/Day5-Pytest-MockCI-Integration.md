# Week10 Day5 - Pytest Mock & CI Integration

## 今日目標

- 學習 Unit Test 與 Integration Test 的差異
- 使用 Fake Object 隔離外部依賴
- 使用 Fixture 與 Monkey Patch
- 將 Pytest 整合至 GitHub Actions

---

# 今日成果

- 建立 `tests/conftest.py`
- 建立 Fake Redis
- 建立 Fake SQLAlchemy Session
- 使用 `fixture`
- 使用 `monkeypatch`
- Mock Redis 與 PostgreSQL
- Pytest 全部通過
- GitHub Actions 新增 Pytest Workflow

---

# conftest.py

pytest 會自動載入 `conftest.py`。

用途：

- Fixture
- Fake Object
- Mock
- 共用測試設定

---

# Fake Object

建立：

- FakeRedis
- FakeSession

取代：

- Redis
- PostgreSQL

避免單元測試依賴真正外部服務。

---

# Fixture

```python
@pytest.fixture
```

用途：

建立可重複使用的測試物件。

例如：

- fake_redis
- fake_session

---

# Monkey Patch

```python
monkeypatch.setattr(...)
```

用途：

測試期間暫時替換正式程式中的物件。

例如：

```
redis_client
        ↓
FakeRedis
```

```
SessionLocal()
        ↓
FakeSession()
```

測試結束後自動還原。

---

# Pytest Workflow

Git Push

↓

GitHub Actions

↓

Python Syntax Check

↓

Ruff

↓

Pytest

↓

Pass

---

# 今日遇到的問題

### Redis Connection Error

原因：

Pytest 執行時未啟動 Redis。

解法：

使用 FakeRedis + Monkey Patch。

---

### PostgreSQL Connection Error

原因：

SessionLocal() 建立真正 Database Session。

解法：

建立 FakeSession 並 Monkey Patch SessionLocal。

---

### API Contract Drift

原因：

API Response 已修改，但測試仍驗證舊欄位。

解法：

更新 Test Case，使測試符合最新 API Contract。

---

# Unit Test vs Integration Test

Unit Test

- Fake Redis
- Fake PostgreSQL
- 快速
- 不依賴外部服務

Integration Test

- 真正 Redis
- 真正 PostgreSQL
- 驗證整體系統

---

# 今日重點

- conftest.py 為 pytest 共用設定。
- Fixture 建立共用測試資源。
- Fake Object 隔離外部依賴。
- Monkey Patch 暫時替換正式物件。
- GitHub Actions 已完成 Pytest 自動化驗證。

---

# Interview Q&A

### Q1：為什麼 Unit Test 要使用 Mock？

避免依賴 Redis、PostgreSQL 等外部服務，使測試快速、穩定且可重複執行。

---

### Q2：Monkey Patch 的用途？

測試期間暫時替換正式程式中的物件，例如將 `redis_client` 或 `SessionLocal()` 替換為 Fake Object，測試結束後自動恢復。

---

# 本日總結

完成 Pytest Mock 機制，使用 Fixture、Fake Object 與 Monkey Patch 隔離 Redis、PostgreSQL，成功將 API 單元測試整合至 GitHub Actions，建立企業級 CI 自動化測試流程。
