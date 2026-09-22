<!-- current-curriculum: 2026-09-22 -->
# Week5 Day3 — 現行 worker 狀態機

[上一課](<day2-redis-persistence.md>) · [本週目錄](README.md) · [下一課](<day4-stuck-job-recovery.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「現行 worker 狀態機」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

reconcile_job 依狀態推進：processing 也可重入，submit 成功記 submitted，之後 collector 等終態。done marker 在狀態回寫與 queue 清理後設定；queue 並非唯一接續來源。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
```

## 閱讀與練習

先用這張表追程式，不必一次背完 Redis API：

| 讀到的狀態 | 現行 MPI 分支做什麼 | 下一步 |
|---|---|---|
| accepted／retrying／processing | 保存 processing，再以固定名稱提交／接回 JobSet | 保存 submitted 與 jobset_name |
| submitted，collector 回 None | 尚未拿到終態，不寫 completed | 留待下一輪 |
| submitted，collector 回終態 | 先保存 DB status，再回寫 Redis result／finished_at | 清 queue、設 done marker |
| completed／failed，尚未 done | 補寫 DB，再完成 queue 清理 | 設 done marker |

例如：Kubernetes 已建立 JobSet，但 worker 在寫 submitted 前停止，Redis 可能仍是 processing。下次重入 submit 會遇到同名物件；dispatcher 必須核對 owner label 才能接回，不能把所有 409 都忽略。這才是「可重試」的具體設計，不是保證所有外部副作用只發生一次。

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 逐支閱讀 reconcile_job，畫出 MPI 正常路徑。對照 test_worker 的重啟／回寫失敗測試，說明 submitted 為何不等於 Running。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '19,42p' 'api/worker.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week5/day3-reliable-worker-state-machine.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
