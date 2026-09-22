<!-- current-curriculum: 2026-09-22 -->
# Week10 Day5 — Mock 與故障分支

[上一課](<Day4-Pytest-API-Testing-Foundation.md>) · [本週目錄](README.md) · [下一課](<Day6-Docker-Build-inCI.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Mock 與故障分支」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

worker 測試用假的 Redis／DB／Kubernetes 觸發真實難重現的失敗窗口。重點不是 mock 越多越好，而是確認有沒有測到 DB-first、409 owner 與 lease 失效等契約。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[tests/test_worker.py](<../../tests/test_worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 選一個 DB failure 測試，逐行說明設定、執行和斷言；再對照實機 restart evidence，說明兩者各自的限制。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '44,67p' 'tests/test_worker.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../tests/test_worker.py>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week10/Day5-Pytest-MockCI-Integration.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
