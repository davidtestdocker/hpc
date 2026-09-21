# 以 FastAPI TestClient 驗證 HTTP 回應、benchmark 清單與工作提交格式。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_root():
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["message"] == "HPC API DEV"
    assert body["status"] == "running"


# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_benchmarks():
    response = client.get("/benchmarks")

    assert response.status_code == 200

    body = response.json()

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

    response = client.post(
        "/benchmark",
        json={
            "benchmark": "cpu"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "job_id" in body
    assert body["benchmark"] == "cpu"
    assert body["status"] == "accepted"
    assert body["next_step"] == f"Check job status at GET /jobs/{body['job_id']}"

