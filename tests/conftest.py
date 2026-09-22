# pytest 共用替身：以 monkeypatch 替換 Redis 與資料庫，避免 API 測試連到外部服務。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import pytest

import api.main


# class 定義 FakeRedis 類別，封裝相關資料與方法。
class FakeRedis:
    def pipeline(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def execute(self):
        return []

    # 定義 set 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    def set(self, *args, **kwargs):
        return True

    # 定義 rpush 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    def rpush(self, *args, **kwargs):
        return 1


# class 定義 FakeSession 類別，封裝相關資料與方法。
class FakeSession:
    # 定義 add 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    def add(self, *args, **kwargs):
        pass

    # 定義 commit 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    def commit(self):
        pass

    # 定義 close 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    def close(self):
        pass


# 定義 fake_redis 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
@pytest.fixture
def fake_redis():
    return FakeRedis()


# 定義 fake_session 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
@pytest.fixture
def fake_session():
    return FakeSession()


# autouse fixture 自動套用，monkeypatch 在測試結束後會復原替換。
@pytest.fixture(autouse=True)
def mock_external_services(fake_redis, fake_session, monkeypatch):
    # 在測試期間替換指定物件屬性，以替身隔離外部服務。
    monkeypatch.setattr(
        api.main,
        "redis_client",
        fake_redis,
    )

    # 在測試期間替換指定物件屬性，以替身隔離外部服務。
    monkeypatch.setattr(
        api.main,
        "SessionLocal",
        lambda: fake_session,
    )
