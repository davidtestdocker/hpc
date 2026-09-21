import json

import api.main
from api.workloads.collector import (
    build_terminal_update,
    classify_jobset,
    normalize_log,
)


def jobset(terminal_state=None, conditions=None):
    # 使用最小 JobSet status shape，讓終態判斷不依賴 Kubernetes client。
    status = {"conditions": conditions or []}
    if terminal_state is not None:
        status["terminalState"] = terminal_state
    return {"status": status}


def test_nonterminal_jobset_does_not_publish_an_update():
    assert classify_jobset(jobset()) is None
    assert build_terminal_update("mpi-1", jobset(), "RANK=0 HOST=w0\n") is None


def test_completed_jobset_collects_sorted_unique_ranks():
    update = build_terminal_update(
        "mpi-1",
        jobset(terminal_state="Completed"),
        "warning\nRANK=2 HOST=w2\nRANK=0 HOST=w0\nRANK=1 HOST=w1\n",
    )

    assert update["status"] == "completed"
    assert update["result"]["ranks"] == [0, 1, 2]
    assert update["result"]["rank_evidence_complete"] is True


def test_kubernetes_byte_log_is_decoded_before_rank_parsing():
    log = normalize_log(b"RANK=2 HOST=w2\nRANK=0 HOST=w0\nRANK=1 HOST=w1\n")
    update = build_terminal_update("mpi-1", jobset(terminal_state="Completed"), log)

    assert update["result"]["ranks"] == [0, 1, 2]


def test_stringified_byte_log_is_decoded_safely():
    log = normalize_log("b'RANK=0 HOST=w0\\nRANK=1 HOST=w1\\nRANK=2 HOST=w2\\n'")

    assert log == "RANK=0 HOST=w0\nRANK=1 HOST=w1\nRANK=2 HOST=w2\n"


def test_failed_condition_wins_without_complete_rank_evidence():
    failed = jobset(conditions=[{
        "type": "Failed", "status": "True", "reason": "FailedJobs",
    }])
    update = build_terminal_update("mpi-2", failed, "", "launcher pod not found")

    assert update["status"] == "failed"
    assert update["result"]["rank_evidence_complete"] is False
    assert update["result"]["log_error"] == "launcher pod not found"


def test_bulk_collector_persists_terminal_mpi_state(monkeypatch):
    job_id = "11111111-1111-1111-1111-111111111111"
    job = {
        "job_id": job_id,
        "benchmark": "mpi",
        "status": "submitted",
        "result": {"jobset_name": "mpi-1"},
    }

    class LifecycleRedis:
        def __init__(self):
            self.saved = None

        def scan_iter(self, match):
            assert match == "job:*"
            return iter([f"job:{job_id}"])

        def get(self, key):
            assert key == f"job:{job_id}"
            return json.dumps(job)

        def set(self, key, value):
            self.saved = (key, json.loads(value))

    redis = LifecycleRedis()
    db_updates = []
    monkeypatch.setattr(api.main, "redis_client", redis)
    monkeypatch.setattr(
        api.main,
        "collect_mpi_jobset",
        lambda name: build_terminal_update(
            name,
            jobset(terminal_state="Completed"),
            "RANK=0 HOST=w0\nRANK=1 HOST=w1\nRANK=2 HOST=w2\n",
        ),
    )
    monkeypatch.setattr(
        api.main,
        "persist_job_status",
        lambda saved_job_id, status: db_updates.append((saved_job_id, status)),
    )

    response = api.main.collect_submitted_mpi_jobs()

    assert response == {
        "updated_jobs": [job_id],
        "pending_jobs": [],
        "errors": [],
        "updated_count": 1,
    }
    assert db_updates == [(job_id, "completed")]
    assert redis.saved[1]["status"] == "completed"
    assert redis.saved[1]["result"]["ranks"] == [0, 1, 2]
    assert "finished_at" in redis.saved[1]
