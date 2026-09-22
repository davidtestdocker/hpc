"""自動 worker 實機驗收：停啟接續、正常 MPI、模擬 dispatch 失敗及 DB／queue 核對。

validate 會建立三筆工作並短暫縮放 worker；audit 讀取保存的工作 ID 交叉核對。
操作前置條件與證據說明見 docs/runbooks/automatic-worker.md。
"""
import argparse
import json
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def audit(context, url, output):
    """核對已保存工作的 DB 終態、queue 清理，以及手動端點應回傳的 409。"""
    report = json.loads(output.read_text())
    expected = {
        report['jobs']['restart']['job_id']: 'completed',
        report['jobs']['normal']['job_id']: 'completed',
        report['jobs']['simulated_dispatch_failure']['job_id']: 'failed',
    }
    # 在 API Pod 內沿用既有連線設定，僅輸出狀態與 queue IDs，不列印 Secret。
    code = (
        'import json; from uuid import UUID; from api import main; '
        f'ids = {list(expected)!r}; '
        's = main.SessionLocal(); '
        'print(json.dumps({"database_status": '
        '{i: s.get(main.Job, UUID(i)).status for i in ids}, '
        '"queues": {q: main.redis_client.lrange(q, 0, -1) for q in '
        '["job_queue", "processing_queue", "dead_letter_queue"]}})); s.close()'
    )
    raw = subprocess.check_output([
        'kubectl', '--context', context, '--request-timeout=20s',
        '-n', 'hpc-platform-dev', 'exec', 'deployment/api', '--', 'python', '-c', code,
    ], text=True, timeout=60)
    checks = json.loads(raw)
    assert checks['database_status'] == expected
    # 只要求本次工作已離開待處理 queue，不假設整個平台沒有其他使用者工作。
    for queue in ('job_queue', 'processing_queue'):
        assert not set(expected).intersection(checks['queues'][queue])
    assert report['jobs']['simulated_dispatch_failure']['job_id'] in checks['queues']['dead_letter_queue']
    # 這三次 POST 只驗證停用保護；它們不是用來推進前面的自動工作流程。
    codes = {}
    for endpoint in ('process-next', 'collect-mpi', 'recover-stuck'):
        req = urllib.request.Request(url + '/worker/' + endpoint, data=b'')
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                codes[endpoint] = response.status
        except urllib.error.HTTPError as exc:
            codes[endpoint] = exc.code
    assert all(code == 409 for code in codes.values())
    report['post_run_audit'] = {**checks, 'manual_endpoint_rejections': codes}
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(report['post_run_audit'], indent=2))


def validate(context, url, output):
    """依序驗證兩個重啟窗口、正常完成及三次模擬失敗；分段保存報告。"""
    base = ['kubectl', '--context', context, '--request-timeout=20s',
            '-n', 'hpc-platform-dev']
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
              'context': context, 'passed': False,
              'scope': 'CPU MPI on existing single-L4 cluster; automatic polling worker',
              'manual_worker_endpoint_calls': 0, 'jobs': {}}

    def save():
        """保存目前進度，途中失敗也能追查已建立的 job ID。"""
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')

    def kubectl(*args):
        """固定 context／namespace 執行命令，避免依賴使用者的 current-context。"""
        return subprocess.check_output(base + list(args), text=True, timeout=210)

    def request(path, payload=None):
        """有 payload 時送 JSON POST；否則 GET，並解析 JSON 回應。"""
        data = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(url + path, data=data,
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.load(response)

    def poll(job_id, states, timeout=420):
        """只查詢 API，不呼叫 worker endpoint；達到指定狀態即返回。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = request('/jobs/' + job_id)
            if result['status'] in states:
                return result
            time.sleep(1)
        raise TimeoutError(f'Job {job_id} did not reach {states}')

    original = json.loads(kubectl('get', 'deployment', 'api-worker', '-o', 'json'))
    if original['spec']['replicas'] != 1:
        raise RuntimeError('Expected one active worker before validation')
    restore_worker = False
    try:
        # 第一個窗口：worker 為零副本時提交，確認 accepted 能在重啟後自動推進。
        restore_worker = True
        kubectl('scale', 'deployment/api-worker', '--replicas=0')
        kubectl('wait', '--for=delete', 'pod', '-l', 'app=api-worker', '--timeout=90s')
        accepted = request('/benchmark', {'benchmark': 'mpi'})
        job_id = accepted['job_id']
        report['jobs']['restart'] = {'job_id': job_id, 'accepted_without_worker': True}
        save()
        assert request('/jobs/' + job_id)['status'] == 'accepted'
        kubectl('scale', 'deployment/api-worker', '--replicas=1')
        restore_worker = False
        kubectl('rollout', 'status', 'deployment/api-worker', '--timeout=180s')
        result = poll(job_id, {'submitted', 'completed', 'failed'})
        # 第二個窗口：submitted 後停掉 collector，讓 JobSet 自行完成，再測結果接續回收。
        # 若沒捕捉到 submitted 窗口就明確失敗，不把一般成功冒充重啟驗收。
        if result['status'] != 'submitted':
            raise RuntimeError('Missed submitted window; cannot claim collector restart test')
        restore_worker = True
        kubectl('scale', 'deployment/api-worker', '--replicas=0')
        kubectl('wait', '--for=delete', 'pod', '-l', 'app=api-worker', '--timeout=90s')
        name = result['result']['jobset_name']
        kubectl('wait', '--for=condition=Completed', 'jobset/' + name, '--timeout=180s')
        assert request('/jobs/' + job_id)['status'] == 'submitted'
        report['jobs']['restart']['completed_in_kubernetes_while_worker_stopped'] = True
        kubectl('scale', 'deployment/api-worker', '--replicas=1')
        restore_worker = False
        result = poll(job_id, {'completed', 'failed'})
        assert result['status'] == 'completed'
        assert result['result']['rank_evidence_complete'] is True
        report['jobs']['restart']['result'] = result
        matching = json.loads(kubectl('get', 'jobsets', '-l',
                                     f'platform-job-id={job_id}', '-o', 'json'))
        assert len(matching['items']) == 1
        report['jobs']['restart']['jobset_count'] = 1
        save()

        # 再跑不干預 worker 的正常案例，確認完整自動流程。
        normal = request('/benchmark', {'benchmark': 'mpi'})
        result = poll(normal['job_id'], {'completed', 'failed'})
        assert result['status'] == 'completed' and result['result']['rank_evidence_complete']
        report['jobs']['normal'] = result
        save()
        # 模擬的是 dispatch 失敗，非 MPI 程序或節點故障；三次後應回報 failed。
        failure = request('/benchmark', {'benchmark': 'mpi', 'simulate_failure': True})
        result = poll(failure['job_id'], {'failed'})
        assert result['retry_count'] == 3
        report['jobs']['simulated_dispatch_failure'] = result
        report['limitations'] = [
            'Failure case is simulated dispatch failure, not an injected MPI process failure',
            'Redis PVC persistence required; not a Redis-loss or cross-store transaction test',
            'MPI prints ranks; not an MPI throughput benchmark',
        ]
        report['passed'] = True
        save()
        print(json.dumps(report, indent=2))
    finally:
        # 本工具停止 worker 後若發生例外，嘗試恢復原先要求的一個副本並保留報告。
        if restore_worker:
            kubectl('scale', 'deployment/api-worker', '--replicas=1')
        save()


if __name__ == '__main__':
    # audit-only 不重建三筆工作；execute 才執行停啟與提交，之後再 audit。
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True)
    parser.add_argument('--url', default='http://127.0.0.1:18080')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--audit-only', action='store_true',
                        help='Verify saved job IDs against DB, queues and disabled manual endpoints')
    args = parser.parse_args()
    if args.audit_only:
        audit(args.context, args.url, args.output)
    elif not args.execute:
        parser.error('--execute required: creates three jobs and briefly stops the worker')
    else:
        validate(args.context, args.url, args.output)
        audit(args.context, args.url, args.output)
