# 直接驗證同步 endpoint 回傳、benchmark 清單與工作提交格式；HTTP transport 由部署驗收覆蓋。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
from api.main import BenchmarkRequest, create_benchmark, list_benchmarks, root


# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_root():
    body = root()

    assert body["message"] == "HPC API DEV"
    assert body["status"] == "running"


# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_benchmarks():
    body = list_benchmarks()

    assert "benchmarks" in body
    assert isinstance(body["benchmarks"], list)
    assert body["benchmarks"] == [
        "cpu",
        "memory",
        "disk_io",
        "mpi",
    ]

# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_submit_benchmark():
    body = create_benchmark(BenchmarkRequest(benchmark="cpu"))

    assert "job_id" in body
    assert body["benchmark"] == "cpu"
    assert body["status"] == "accepted"
    assert body["next_step"] == f"Check job status at GET /jobs/{body['job_id']}"
