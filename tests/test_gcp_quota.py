"""GPU rehearsal 必須同時滿足區域 accelerator 與專案全域 quota。"""

from scripts.check_gcp_quota import evaluate


def document(**quotas):
    return {"quotas": [{"metric": name, "limit": limit, "usage": usage}
                        for name, (limit, usage) in quotas.items()]}


def test_global_quota_can_block_available_spot_l4():
    region = document(PREEMPTIBLE_NVIDIA_L4_GPUS=(1, 0))
    project = document(GPUS_ALL_REGIONS=(1, 1))
    checks = evaluate(region, project, gpu_count=1, spot=True)
    assert checks[0]["passed"] is True
    assert checks[1]["passed"] is False


def test_all_gpu_quota_layers_must_pass():
    region = document(NVIDIA_L4_GPUS=(2, 1))
    project = document(GPUS_ALL_REGIONS=(2, 1))
    assert all(item["passed"] for item in evaluate(region, project, 1, spot=False))
