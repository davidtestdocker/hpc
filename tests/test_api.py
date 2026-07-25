from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["message"] == "HPC API DEV"
    assert body["status"] == "running"


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
    ]

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
    assert body["next_step"] == "job status API will be added next"


