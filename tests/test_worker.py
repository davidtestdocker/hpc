"""背景 worker 的離線保護測試：狀態接續、鎖、DB／Redis 失敗及 JobSet 重試。

以記憶體字典和 MagicMock 取代外部服務；不據此宣稱真實叢集已成功。
實機驗收另由 scripts/validate_automatic_worker.py 保存 evidence。
"""
import json
from unittest.mock import MagicMock

import pytest
from kubernetes.client.exceptions import ApiException

from api import main, worker
from api.workloads import dispatcher

JOB_ID = '11111111-1111-1111-1111-111111111111'


@pytest.fixture
def store(monkeypatch):
    """建立可讀回寫入狀態的 Redis 替身，並隔離 DB 與 Kubernetes 呼叫。

    pipeline 替身不模擬真正 Redis 的原子性；本檔測流程分支與重試行為。
    """
    data = {}
    redis = MagicMock()
    redis.get.side_effect = data.get
    redis.set.side_effect = lambda k, v: data.__setitem__(k, v)
    redis.scan_iter.side_effect = lambda **_: iter([k for k in data if k.startswith('job:')])
    pipe = redis.pipeline.return_value.__enter__.return_value
    pipe.set.side_effect = redis.set.side_effect
    monkeypatch.setattr(main, 'redis_client', redis)
    monkeypatch.setattr(main, 'persist_job_status', MagicMock())
    monkeypatch.setattr(main, 'submit_mpi_jobset', MagicMock(return_value=f'mpi-{JOB_ID}'))
    return data, redis


def job(status='accepted'):
    """產生同一個 job ID 的最小 MPI record，供不同中斷狀態重入測試。"""
    return {'job_id': JOB_ID, 'benchmark': 'mpi', 'status': status,
            'retry_count': 0, 'result': {'jobset_name': f'mpi-{JOB_ID}'}}


@pytest.mark.parametrize('state', ['accepted', 'processing', 'retrying'])
def test_dispatch_recovers_without_queue_entry(store, state):
    data, _ = store
    data[f'job:{JOB_ID}'] = json.dumps(job(state))
    worker.tick()
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'submitted'
    main.submit_mpi_jobset.assert_called_once_with(JOB_ID)


@pytest.mark.parametrize('terminal', ['completed', 'failed'])
def test_collects_terminal_status_automatically(store, monkeypatch, terminal):
    data, _ = store
    data[f'job:{JOB_ID}'] = json.dumps(job('submitted'))
    monkeypatch.setattr(main, 'collect_mpi_jobset', lambda _: {
        'status': terminal, 'result': {'ranks': [0, 1, 2]}})
    worker.tick()
    saved = json.loads(data[f'job:{JOB_ID}'])
    assert saved['status'] == terminal
    assert saved['result']['ranks'] == [0, 1, 2]
    assert 'finished_at' in saved
    main.persist_job_status.assert_called_with(JOB_ID, terminal)


def test_db_outage_leaves_submitted_for_retry(store, monkeypatch):
    data, _ = store
    data[f'job:{JOB_ID}'] = json.dumps(job('submitted'))
    monkeypatch.setattr(main, 'collect_mpi_jobset', lambda _: {'status': 'completed'})
    main.persist_job_status.side_effect = RuntimeError('DB offline')
    worker.tick()
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'submitted'
    main.persist_job_status.side_effect = None
    worker.tick()
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'completed'


def test_lost_lease_prevents_result_publication(store):
    data, _ = store
    def guard():
        raise RuntimeError('lost')
    with pytest.raises(RuntimeError):
        worker.reconcile_job(job(), guard)
    assert not data
    main.submit_mpi_jobset.assert_not_called()


def test_created_jobset_db_failure_retries_same_job_id(store):
    data, _ = store
    data[f'job:{JOB_ID}'] = json.dumps(job())
    main.persist_job_status.side_effect = RuntimeError('DB offline after create')
    worker.tick()
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'processing'
    main.persist_job_status.side_effect = None
    worker.tick()
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'submitted'
    assert [call.args for call in main.submit_mpi_jobset.call_args_list] == [(JOB_ID,), (JOB_ID,)]


def test_terminal_redis_failure_retries_db_first(store, monkeypatch):
    data, redis = store
    data[f'job:{JOB_ID}'] = json.dumps(job('submitted'))
    monkeypatch.setattr(main, 'collect_mpi_jobset', lambda _: {'status': 'completed'})
    redis.set.side_effect = RuntimeError('Redis write unavailable')
    worker.tick()
    main.persist_job_status.assert_called_with(JOB_ID, 'completed')
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'submitted'
    redis.set.side_effect = lambda k, v: data.__setitem__(k, v)
    worker.tick()
    assert json.loads(data[f'job:{JOB_ID}'])['status'] == 'completed'


def test_held_lease_skips_dispatch(store):
    data, redis = store
    data[f'job:{JOB_ID}'] = json.dumps(job())
    redis.lock.return_value.acquire.return_value = False
    worker.tick()
    main.submit_mpi_jobset.assert_not_called()


def test_simulated_failure_exhausts_three_attempts(store):
    data, _ = store
    data[f'job:{JOB_ID}'] = json.dumps({**job(), 'simulate_failure': True})
    for _ in range(3):
        worker.tick()
    saved = json.loads(data[f'job:{JOB_ID}'])
    assert saved['status'] == 'failed'
    assert saved['retry_count'] == 3
    main.submit_mpi_jobset.assert_not_called()


@pytest.mark.parametrize('owner,accepted', [(JOB_ID, True), ('different', False)])
def test_dispatch_conflict_requires_matching_owner(monkeypatch, owner, accepted):
    monkeypatch.setattr(dispatcher.config, 'load_incluster_config', lambda: None)
    api = MagicMock()
    api.create_namespaced_custom_object.side_effect = ApiException(status=409)
    api.get_namespaced_custom_object.return_value = {
        'metadata': {'name': f'mpi-{JOB_ID}', 'labels': {'platform-job-id': owner}}}
    monkeypatch.setattr(dispatcher.client, 'CustomObjectsApi', lambda: api)
    if accepted:
        assert dispatcher.submit_mpi_jobset(JOB_ID) == f'mpi-{JOB_ID}'
    else:
        with pytest.raises(RuntimeError, match='not owned'):
            dispatcher.submit_mpi_jobset(JOB_ID)


def test_manual_operations_disabled_when_automatic(monkeypatch):
    monkeypatch.setenv('AUTOMATIC_WORKER', 'true')
    for endpoint in (main.process_next_job, main.collect_submitted_mpi_jobs,
                     main.recover_stuck_jobs):
        with pytest.raises(main.HTTPException) as error:
            endpoint()
        assert error.value.status_code == 409
