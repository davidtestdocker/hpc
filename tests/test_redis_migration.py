import pytest

from scripts.migrate_redis_empty import redis_manifests, require_empty_keyspace


def test_nondefault_database_also_blocks_empty_migration():
    # 不能只檢查 Redis DB 0，其他 DB 有資料也必須中止。
    with pytest.raises(RuntimeError, match="contains data"):
        require_empty_keyspace("# Keyspace\r\ndb3:keys=1,expires=0,avg_ttl=0\r\n")


def test_empty_database_is_allowed():
    # 空 keyspace 才能進入本輪專用的安全遷移流程。
    require_empty_keyspace("# Keyspace\r\n")


def test_migration_manifest_excludes_other_platform_resources():
    # 遷移腳本只能產生 Redis 兩項資源，不能意外包含 Secret 或 API。
    rendered = """
kind: Deployment
metadata: {name: api}
---
kind: Secret
metadata: {name: postgres-secret}
---
kind: Deployment
metadata: {name: redis}
---
kind: PersistentVolumeClaim
metadata: {name: redis-pvc}
"""
    result = redis_manifests(rendered)
    assert [item["metadata"]["name"] for item in result["items"]] == ["redis", "redis-pvc"]


def test_missing_pvc_blocks_migration():
    # 缺 PVC 時拒絕執行，避免執行結果與預期持久化不一致。
    with pytest.raises(RuntimeError, match="exactly"):
        redis_manifests("kind: Deployment\nmetadata: {name: redis}\n")
