import pytest

from scripts.recover_stale_placement import stale_pending_pods


def pod(phase="Pending", host="removed-node"):
    # 用最小 Pod metadata 模擬 Kueue／Scheduler 已注入 hostname selector。
    return {"metadata": {"name": "worker"}, "status": {"phase": phase},
            "spec": {"nodeSelector": {"kubernetes.io/hostname": host}}}


def test_recovery_refuses_running_work():
    # 工具不可透過恢復流程驅逐仍在執行的工作。
    with pytest.raises(RuntimeError, match="exclusively Pending"):
        stale_pending_pods([pod(), pod(phase="Running")], {"new-node"})


def test_recovery_refuses_other_pending_causes():
    # Pending 但 node 仍存在時，必須交給一般排障流程處理。
    with pytest.raises(RuntimeError, match="No missing hostname"):
        stale_pending_pods([pod(host="new-node")], {"new-node"})


def test_recovery_identifies_missing_host():
    # 只有不存在的 hostname 才符合 stale placement 條件。
    assert stale_pending_pods([pod()], {"new-node"}) == ["worker"]
