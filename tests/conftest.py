import pytest

import api.main


class FakeRedis:
    def set(self, *args, **kwargs):
        return True

    def rpush(self, *args, **kwargs):
        return 1


class FakeSession:
    def add(self, *args, **kwargs):
        pass

    def commit(self):
        pass

    def close(self):
        pass


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def fake_session():
    return FakeSession()


@pytest.fixture(autouse=True)
def mock_external_services(fake_redis, fake_session, monkeypatch):
    monkeypatch.setattr(
        api.main,
        "redis_client",
        fake_redis,
    )

    monkeypatch.setattr(
        api.main,
        "SessionLocal",
        lambda: fake_session,
    )
