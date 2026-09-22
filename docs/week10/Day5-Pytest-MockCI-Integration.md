<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day5 — Mock 與故障分支

[上一課](<Day4-Pytest-API-Testing-Foundation.md>) · [本週目錄](README.md) · [下一課](<Day6-Docker-Build-inCI.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：Mock 設計與成功敘述。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

FakeRedis 的 set/rpush 僅回固定值，不保存資料；FakeSession commit 不碰DB。這些測試不證明 Redis transaction、DB constraint 或實際連線。API contract 變更應先確認意圖，不是為通過測試任意改 assertion。

## 程式／設定與來源

本次核對：[tests/conftest.py](<../../tests/conftest.py>)、[tests/test_api.py](<../../tests/test_api.py>)、[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day5-Pytest-MockCI-Integration.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
FakeRedis
```

原文 Pytest全過缺獨立本課summary；目前函式測試範圍已說明，不宣稱 HTTP整合測試。

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

# Week10 Day5 - Pytest Mock & CI Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)：CI／映像建置與 GitOps 更新
- [tests/conftest.py](../../tests/conftest.py)
- [tests/test_api.py](../../tests/test_api.py)

---

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
