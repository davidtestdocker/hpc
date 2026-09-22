<!-- current-curriculum: 2026-09-22 -->
# Week4 Day4 — Memory queue 的限制

[上一課](<day3-job-identity.md>) · [本週目錄](README.md) · [下一課](<day5-dockerize-api.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Memory queue 的限制」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

Python list 只在單一程序記憶體中，程序重啟或 API 多副本就無法共享一致的待處理列表。現行以 Redis record 保存工作，worker 掃描 record 接續，不只依賴 queue 中還有 ID。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 用自己的話比較 list、Redis queue、Redis job record 的責任；在 worker 找掃描和 done marker，說明為何 queue 清空不能代表所有工作資料消失。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '84,107p' 'api/worker.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week4/day4-memory-queue.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
