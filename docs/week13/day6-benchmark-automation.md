<!-- current-curriculum: 2026-09-22 -->
# Week13 Day6 — 測試自動化

[上一課](<day5-resource-monitoring.md>) · [本週目錄](README.md) · [下一課](<day7-1-cpu-benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「測試自動化」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

runner 編排環境、等待、收檔與清理，benchmark 才執行量測，analyzer 再核對及彙整。失敗時保留診斷資料，比只印 PASS／FAIL 更能追查。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[scripts/run_causal_lm_benchmark.py](<../../scripts/run_causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def run(context, name, output):
    """用明確 context 和唯一名稱執行一次實驗；失敗時保留現場供排查。"""
    # exist_ok=False 防止重跑覆寫舊證據；目錄建立後即保存本次輸入。
    output.mkdir(parents=True, exist_ok=False)
    base = ['kubectl', '--context', context, '--request-timeout=30s', '-n', 'hpc-platform-dev']

    def kubectl(args, data=None):
        """以參數陣列呼叫 kubectl；可用 stdin 傳 manifest，失敗立即拋出例外。"""
        return subprocess.check_output(base + args, input=data, timeout=90)

    # corpus 和程式可能日後改動，因此本次快照與現行原始碼分開保存。
    source = (ROOT / 'benchmark/gpu/causal_lm_benchmark.py').read_text()
    corpus = (ROOT / 'README.md').read_text()
    (output / 'corpus.txt').write_text(corpus)
    (output / 'benchmark-source.py').write_text(source)
    cm = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': name},
          'data': {'causal_lm_benchmark.py': source, 'corpus.txt': corpus}}
    # nodeSelector 決定 GPU pool；toleration 允許接受 GPU taint。
    # nvidia.com/gpu=1 在此叢集是一個 time-sharing share，不是額外建立一張 GPU。
    # 成功後 sleep 保留容器供 exec 取檔；emptyDir 隨 Pod 刪除，必須先收回結果。
    pod = {'apiVersion': 'v1', 'kind': 'Pod', 'metadata': {'name': name,
           'labels': {'app': 'causal-lm-benchmark'}}, 'spec': {
        'restartPolicy': 'Never', 'activeDeadlineSeconds': 1200,
        'nodeSelector': {'cloud.google.com/gke-nodepool': 'gpu-pool'},
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀新 runner 的建立、完成標記與失敗保留流程，指出 output 為何必須新目錄；不可覆寫 20260922 原始 bundle。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '18,41p' 'scripts/run_causal_lm_benchmark.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week13/day6-benchmark-automation.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
