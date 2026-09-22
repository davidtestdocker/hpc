<!-- current-curriculum: 2026-09-22 -->
# Week17 Day6 — 排程層整合

[上一課](<day5-ray-kuberay-distributed-computing.md>) · [本週目錄](README.md) · [下一週](../week18/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「排程層整合」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

API 接受、Kueue admitted、Pod scheduled、MPI started、工作 completed 是一串不同狀態。每一層都能卡住，必須依症狀定位而不是看到 Pending 就認為缺 GPU。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 用現行 worker 與 JobSet 流程串出每層查詢位置，說明 Slurm／Ray 並未排在 MPI API 的後面自動執行。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '54,77p' 'api/worker.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week17/day6-cluster-scheduling-integration.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
