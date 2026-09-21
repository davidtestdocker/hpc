"""部署必須拒絕將舊 Redis 的資料路徑切換至空磁碟。"""

import pytest

from scripts import deploy_platform
from scripts.deploy_platform import validate_redis


def existing_redis(claim="redis-pvc", path="/data", **mount_options):
    return {"spec": {"template": {"spec": {
        "containers": [{"name": "redis", "volumeMounts": [
            {"name": "data", "mountPath": path, **mount_options}]}],
        "volumes": [{"name": "data", "persistentVolumeClaim": {"claimName": claim}}],
    }}}}


def test_new_or_persistent_redis_allowed():
    validate_redis(None)
    validate_redis(existing_redis())


@pytest.mark.parametrize("deployment", [
    existing_redis(claim="old-pvc"),
    existing_redis(path="/backup"),
    existing_redis(subPath="other-data"),
    existing_redis(subPathExpr="$(POD_NAME)"),
    {"spec": {"template": {"spec": {"containers": [{"name": "redis"}]}}}},
])
def test_storage_switch_is_rejected(deployment):
    with pytest.raises(RuntimeError, match="資料遷移"):
        validate_redis(deployment)


@pytest.mark.parametrize("execute", [False, True])
def test_dry_run_precedes_apply_and_failure_stops_mutations(monkeypatch, tmp_path, execute):
    # 模擬 API server 拒絕 manifest，確認 execute 也不會繼續套用或初始化 DB。
    from types import SimpleNamespace

    calls = []
    monkeypatch.setattr(deploy_platform, "inspect",
                        lambda context, require_gpu=True: {"passed": True})
    monkeypatch.setattr(deploy_platform, "render", lambda: "kind: Service\n")

    def run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=1 if "apply" in args else 0, stdout="")

    monkeypatch.setattr(deploy_platform.subprocess, "run", run)
    assert deploy_platform.deploy("test-context", execute, tmp_path / "report.json") == 1
    assert len(calls) == 2
    assert "--dry-run=server" in calls[-1]
    assert all("test-context" in args for args in calls)


def test_default_mode_never_applies_or_initializes_db(monkeypatch, tmp_path):
    from types import SimpleNamespace

    calls = []
    monkeypatch.setattr(deploy_platform, "inspect",
                        lambda context, require_gpu=True: {"passed": True})
    monkeypatch.setattr(deploy_platform, "render", lambda: "kind: Service\n")

    def run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(deploy_platform.subprocess, "run", run)
    assert deploy_platform.deploy("test-context", False, tmp_path / "report.json") == 0
    assert len(calls) == 2
    assert "--dry-run=server" in calls[-1]
