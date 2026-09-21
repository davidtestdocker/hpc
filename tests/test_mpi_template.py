import yaml

from api.workloads.renderer import render_mpi_jobset
from scripts.collect_mpi import ranks_from_log


def test_launcher_completion_finishes_ssh_workers_and_runtime_is_bounded():
    # 驗證 template 有明確成功條件、期限，且不再用 sleep 900 假裝執行中。
    manifest = yaml.safe_load(render_mpi_jobset("validation-run"))
    assert manifest["spec"]["successPolicy"] == {
        "operator": "All", "targetReplicatedJobs": ["launcher"],
    }
    jobs = manifest["spec"]["replicatedJobs"]
    assert all(0 < job["template"]["spec"]["activeDeadlineSeconds"] <= 330 for job in jobs)
    launcher = jobs[0]["template"]["spec"]["template"]["spec"]["containers"][0]
    assert "sleep 900" not in launcher["command"][-1]
    assert "__JOBSET_NAME__" not in render_mpi_jobset("validation-run")


def test_rank_evidence_ignores_warnings_and_handles_interleaved_output():
    # rank log 順序不固定，且 SSH warning 不應污染 rank 結果。
    assert ranks_from_log("warning\nRANK=2 HOST=w2\nRANK=0 HOST=w0\nRANK=1 HOST=w1\n") == [0, 1, 2]
    assert ranks_from_log("RANK=0 HOST=w0\nRANK=0 HOST=w0\n") == [0]
