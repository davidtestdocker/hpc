"""A Ready node alone is insufficient for the GPU prerequisite."""

from scripts.platform import ready_nodes


def node(*, ready=True, cordoned=False, gpu="1", pool="gpu-pool"):
    # 建立最小 Kubernetes Node shape，測試只關注排程相關欄位。
    return {"items": [{
        "metadata": {"labels": {"cloud.google.com/gke-nodepool": pool}},
        "spec": {"unschedulable": cordoned},
        "status": {
            "conditions": [{"type": "Ready", "status": "True" if ready else "False"}],
            "allocatable": {"nvidia.com/gpu": gpu},
        },
    }]}


def test_gpu_requires_ready_schedulable_node_with_advertised_device():
    # Ready、可排程、GPU resource 三個條件缺一不可。
    assert ready_nodes(node(), "gpu-pool", gpu=True)
    assert not ready_nodes(node(ready=False), "gpu-pool", gpu=True)
    assert not ready_nodes(node(cordoned=True), "gpu-pool", gpu=True)
    assert not ready_nodes(node(gpu="0"), "gpu-pool", gpu=True)
    assert not ready_nodes(node(pool="system-pool"), "gpu-pool", gpu=True)


def test_system_pool_does_not_require_gpu():
    # system-pool 只需是 Ready、可排程，不應被 GPU 條件誤擋。
    assert ready_nodes(node(pool="system-pool", gpu="0"), "system-pool")
    assert not ready_nodes({"items": []}, "system-pool")
