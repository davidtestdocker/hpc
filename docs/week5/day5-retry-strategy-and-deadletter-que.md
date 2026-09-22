<!-- current-curriculum: 2026-09-22 -->
# Week5 Day5 — Retry 與 dead-letter

[上一課](<day4-stuck-job-recovery.md>) · [本週目錄](README.md) · [下一課](<day6-postgresql-foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Retry 與 dead-letter」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

simulate_failure 分支會累計三次後 failed 並進 dead-letter；真實依賴例外由 tick 記錄後下輪重試，不是每種錯誤都三次耗盡。重試需要能辨識同一工作，否則可能產生重複副作用。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 對照模擬失敗測試與例外處理，寫出何時增加 retry_count、何時清 queue。指出 retry_count 尚未同步 DB，不能假設 DB 與 Redis 所有欄位一致。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '38,61p' 'api/worker.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week5/day5-retry-strategy-and-deadletter-que.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
