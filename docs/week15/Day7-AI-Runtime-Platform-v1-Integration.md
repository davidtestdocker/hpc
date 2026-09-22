<!-- current-curriculum: 2026-09-22 -->
# Week15 Day7 — 現行 runtime 整合範圍

[上一課](<Day6-Performance-Analyzer.md>) · [本週目錄](README.md) · [下一週](../week16/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「現行 runtime 整合範圍」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

runner 產生 Pod／ConfigMap、等待完成、收回 raw bundle，成功後清理本次資源；這是一條獨立實驗流程，不是 MPI 完成後接著訓練。失敗會保留診斷資料。

## 在現在的專案中

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

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
2. 按 runner → benchmark → analyzer 畫出資料流，再另畫 API → worker → MPI；說明未整合的接點，不把兩張圖硬串成自動閉環。
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

[改寫前完整教材快照](<../history/20260922-before-current/week15/Day7-AI-Runtime-Platform-v1-Integration.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
