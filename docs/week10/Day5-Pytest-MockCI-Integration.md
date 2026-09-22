<!-- readable-curriculum: 2026-09-22 -->
# Week10 Day5 — Mock 與故障分支

[上一課](<Day4-Pytest-API-Testing-Foundation.md>) · [本週目錄](README.md) · [下一課](<Day6-Docker-Build-inCI.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

worker 測試用假的 Redis／DB／Kubernetes 觸發真實難重現的失敗窗口。重點不是 mock 越多越好，而是確認有沒有測到 DB-first、409 owner 與 lease 失效等契約。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[tests/test_worker.py](<../../tests/test_worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def test_dispatch_recovers_without_queue_entry(store, state):
    data, _ = store
    data[f'job:{JOB_ID}'] = json.dumps(job(state))
    worker.tick()
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'submitted'
    main.submit_mpi_jobset.assert_called_once_with(JOB_ID)


@pytest.mark.parametrize('terminal', ['completed', 'failed'])
def test_collects_terminal_status_automatically(store, monkeypatch, terminal):
    data, _ = store
    data[f'job:{JOB_ID}'] = json.dumps(job('submitted'))
    monkeypatch.setattr(main, 'collect_mpi_jobset', lambda _: {
        'status': terminal, 'result': {'ranks': [0, 1, 2]}})
    worker.tick()
    saved = json.loads(data[f'job:{JOB_ID}'])
    assert saved['status'] == terminal
    assert saved['result']['ranks'] == [0, 1, 2]
    assert 'finished_at' in saved
    main.persist_job_status.assert_called_with(JOB_ID, terminal)


def test_db_outage_leaves_submitted_for_retry(store, monkeypatch):
    data, _ = store
```

## 已有結果與解讀

### 已保存的本機驗證結果

2026-09-22 教材改寫時，在此 repo 開發環境執行並記錄：`53 passed`；三個 Helm charts lint 通過，完整主 overlay 離線渲染出 14 個物件。這是本機測試與渲染結果，**不是遠端 GitHub Actions 整條 CI 成功，也不是新雲端驗收**。

目前 CI 改的是 values-dev.yaml，主 overlay 使用獨立 api-values.yaml，因此不能說 push 一定更新主展示。下方完整保留原本課程與當時輸出；不要求你再跑一次 pytest。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week10/Day5-Pytest-MockCI-Integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
