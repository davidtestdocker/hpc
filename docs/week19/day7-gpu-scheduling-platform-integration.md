<!-- current-curriculum: 2026-09-22 -->
# Week19 Day7 — 排程主線整合

[上一課](<day6-topology-aware-gpu-scheduling.md>) · [本週目錄](README.md) · [下一週](../week20/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「排程主線整合」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

worker create JobSet、Kueue admission、Scheduler placement、MPI 執行、collector 回寫各有失敗窗口。每個階段都有自己的對象，不能只靠 /health 宣稱全流程成功。

## 在現在的專案中

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

本課對照：[api/workloads/collector.py](<../../api/workloads/collector.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def collect_mpi_jobset(jobset_name: str, namespace: str = NAMESPACE) -> dict | None:
    """Query one JobSet and return an update only after it reaches a terminal state."""
    # API Pod 使用 ServiceAccount；本機只讀驗收可沿用明確設定的 kubeconfig context。
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()
    custom_api = client.CustomObjectsApi()
    core_api = client.CoreV1Api()

    jobset = custom_api.get_namespaced_custom_object(
        group="jobset.x-k8s.io",
        version="v1alpha2",
        namespace=namespace,
        plural="jobsets",
        name=jobset_name,
        _request_timeout=15,
    )
    if classify_jobset(jobset) is None:
        return None

    # Labels survive generated Pod suffixes and JobSet restarts, unlike a guessed Pod name.
    selector = (
        f"jobset.sigs.k8s.io/jobset-name={jobset_name},"
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 用自動驗收的兩筆 completed 與一筆模擬 failed，逐項指向狀態、ranks、DB、queue 證據；說明模擬 dispatch failure 不是 MPI kernel failure。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '81,104p' 'api/workloads/collector.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week19/day7-gpu-scheduling-platform-integration.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
