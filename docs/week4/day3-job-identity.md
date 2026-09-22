<!-- current-curriculum: 2026-09-22 -->
# Week4 Day3 — Job identity

[上一課](<day2-rest-api-design.md>) · [本週目錄](README.md) · [下一課](<day4-memory-queue.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Job identity」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

UUID 是工作身分，固定 mpi-<job_id> 名稱讓重試可接回同一 JobSet。名稱衝突不自動表示是自己的工作，dispatcher 還核對 owner label。

## 在現在的專案中

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

本課對照：[api/workloads/dispatcher.py](<../../api/workloads/dispatcher.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
        # create 成功後程序可能中斷。409 時查回同名資源，而不是產生第二個 JobSet。
        # 其他 API 錯誤保持拋出，讓背景 worker 留待下一輪重試。
        if exc.status != 409:
            raise
        response = api.get_namespaced_custom_object(
            group='jobset.x-k8s.io', version='v1alpha2', namespace=NAMESPACE,
            plural='jobsets', name=manifest['metadata']['name'], _request_timeout=15,
        )
        if response.get('metadata', {}).get('labels', {}).get('platform-job-id') != job_id:
            raise RuntimeError('Existing JobSet is not owned by this platform job') from exc

    return response["metadata"]["name"]
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 從 API 的 uuid4 追到 renderer 與 dispatcher 的 409 分支；解釋使用隨機新名稱重試為何可能重複執行。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '36,47p' 'api/workloads/dispatcher.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week4/day3-job-identity.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
