<!-- current-curriculum: 2026-09-22 -->
# Week13 Day7-5 — Framework v2 子章

[上一課](<day7-4-benchmark-framework.md>) · [本週目錄](README.md) · [下一課](<day7-6-result-integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Framework v2 子章」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

逐步框架應分清執行、結果 schema 和分析，不能把整合目錄當作每一種 workload 都已端到端驗證。新 causal LM runner 保存 image／hash／source，是可追溯設計的具體例子。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[scripts/run_causal_lm_benchmark.py](<../../scripts/run_causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
                'sha256': {f: hashlib.sha256((output / f).read_bytes()).hexdigest()
                           for f in artifacts + ['corpus.txt', 'benchmark-source.py']},
                'passed': True}
    # 成功收回證據才清理本次具名 Pod／ConfigMap；不刪節點、PVC 或其他工作。
    print(kubectl(['delete', 'pod', name, '--wait=false']).decode(), flush=True)
    print(kubectl(['delete', 'configmap', name]).decode(), flush=True)
    evidence['cleanup'] = 'temporary Pod deletion requested; ConfigMap deleted; artifacts retained'
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2), flush=True)


if __name__ == '__main__':
    # --execute 是明確的操作開關，因為此程式會建立、執行並清理叢集資源。
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('--execute is required to create and run the temporary GPU Pod')
    run(args.context, args.name, args.output)
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 對照舊 shell runner 與新 runner 的 evidence 欄位，列出哪些資料用來證明測的是同一份程式，而不是只記最終數字。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '85,106p' 'scripts/run_causal_lm_benchmark.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week13/day7-5-benchmark-framework-v2.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
