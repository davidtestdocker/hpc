"""可重啟的背景 worker：以 Redis job record 接續提交、查詢終態與結果回寫。

流程：run 定期呼叫 tick → 每筆工作取得 lease → reconcile_job 推進狀態。
queue 保留相容用途；接續處理靠掃描 job record，不依賴 ID 還留在 queue。
操作與驗收：docs/runbooks/automatic-worker.md。
"""
import json
import logging
import os
import signal
import threading
from datetime import datetime, timezone

from api import main

logger = logging.getLogger(__name__)


def reconcile_job(job, guard=lambda: None):
    """推進一筆工作；先記錄提交意圖，終態則先寫 PostgreSQL 再發布 Redis。

    guard 在關鍵寫入前檢查 lease；預設空操作供單元測試直接呼叫使用。
    這是可重試流程，並非兩個資料庫之間的原子交易或 exactly-once 保證。
    """
    redis = main.redis_client
    job_id = job['job_id']
    key = f'job:{job_id}'
    state = job['status']
    guard()
    if state in {'completed', 'failed'}:
        # 終態已發布但尚未標記 done 時，補寫 DB 並接續下方 queue 清理。
        main.persist_job_status(job_id, state)
    elif state in {'accepted', 'retrying', 'processing'}:
        # processing 也可以重入：上次可能已建立 JobSet，卻來不及保存 submitted。
        # dispatcher 會用固定名稱及 owner label 接回同一個 JobSet。
        job['status'] = 'processing'
        redis.set(key, json.dumps(job))
        if job.get('simulate_failure'):
            # 僅此模擬故障累計三次後 failed；真實依賴例外由 tick 記錄並於下輪重試。
            job['retry_count'] = job.get('retry_count', 0) + 1
            job['status'] = 'failed' if job['retry_count'] >= 3 else 'retrying'
            job['result'] = {'message': 'Simulated dispatch failure'}
        elif job['benchmark'] == 'mpi':
            name = main.submit_mpi_jobset(job_id)
            job['status'] = 'submitted'
            job['result'] = {'jobset_name': name, 'message': 'MPI JobSet submitted'}
        else:
            job['status'] = 'completed'
            job['result'] = {'message': 'benchmark simulated'}
        guard()
        main.persist_job_status(job_id, job['status'])
        guard()
        redis.set(key, json.dumps(job))
    elif state == 'submitted' and job['benchmark'] == 'mpi':
        # submitted 只代表已提交；collector 回傳 None 表示尚未取得終態。
        update = main.collect_mpi_jobset(job['result']['jobset_name'])
        if update is None:
            return
        guard()
        main.persist_job_status(job_id, update['status'])
        job.update(update)
        job['finished_at'] = datetime.now(timezone.utc).isoformat()
        guard()
        redis.set(key, json.dumps(job))
    else:
        raise ValueError(f'Unsupported job state: {state}')
    # pipeline 預設使用 MULTI/EXEC，把 queue 清理與 done 標記放在同一 Redis 交易。
    # 此交易不涵蓋上方 PostgreSQL；DB-first 失敗時保留可在下一輪重試的狀態。
    guard()
    with redis.pipeline() as pipe:
        pipe.lrem('job_queue', 0, job_id)
        pipe.lrem('processing_queue', 0, job_id)
        if job['status'] == 'failed':
            pipe.lrem('dead_letter_queue', 0, job_id)
            pipe.rpush('dead_letter_queue', job_id)
        if job['status'] in {'completed', 'failed'}:
            pipe.set(f'worker:done:{job_id}', '1')
        pipe.execute()


def tick():
    """逐筆掃描並取得 lease；單筆例外不阻止本輪繼續處理其他工作。"""
    redis = main.redis_client
    for key in redis.scan_iter(match='job:*', count=100):
        job_id = key.removeprefix('job:')
        if redis.get(f'worker:done:{job_id}'):
            continue
        # 不等待其他持有者；thread_local=False 讓續期執行緒可使用相同 lock token。
        lock = redis.lock(f'worker:lock:{job_id}', timeout=120, blocking=False,
                          thread_local=False)
        if not lock.acquire(blocking=False):
            continue
        finished = threading.Event()
        lost = threading.Event()

        def renew(finished=finished, lock=lock, lost=lost):
            """每 30 秒把 lease 有效期重設為 120 秒；失敗後通知主流程停止發布。"""
            # 預設參數固定本次迴圈的物件，避免執行緒引用到下一筆工作的變數。
            while not finished.wait(30):
                try:
                    lock.extend(120, replace_ttl=True)
                except Exception:
                    logger.exception('Worker lease renewal failed')
                    lost.set()
                    return

        def guard(lost=lost, lock=lock):
            """同時檢查續期結果與 Redis 所有權，降低過期持有者繼續寫入的風險。"""
            if lost.is_set() or not lock.owned():
                raise RuntimeError('Worker lease lost; stop publishing this attempt')

        renewal = threading.Thread(target=renew, daemon=True)
        renewal.start()
        try:
            raw = redis.get(key)
            if raw:
                reconcile_job(json.loads(raw), guard)
        except Exception:
            logger.exception('Job reconciliation failed; next poll will retry: %s', job_id)
        finally:
            # 無論成功或例外，都停止續期並嘗試釋放鎖；崩潰時仍有 TTL 自動到期。
            finished.set()
            renewal.join(timeout=6)
            try:
                lock.release()
            except Exception:
                logger.exception('Job lease release failed: %s', job_id)


def run():
    """執行輪詢主迴圈；SIGTERM／Ctrl+C 會設旗標，在當前 tick 返回後退出。"""
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    interval = float(os.getenv('WORKER_POLL_SECONDS', '5'))
    if interval <= 0:
        raise ValueError('WORKER_POLL_SECONDS must be positive')
    while not stop.is_set():
        try:
            tick()
        except Exception:
            logger.exception('Worker dependencies unavailable; retrying')
        # Event.wait 可被停止訊號提早喚醒，不必等滿整段輪詢間隔。
        stop.wait(interval)


if __name__ == '__main__':
    run()
