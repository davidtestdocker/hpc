<!-- current-curriculum: 2026-09-22 -->
# Week13 Day7-6 — 結果整合子章

[上一課](<day7-5-benchmark-framework-v2.md>) · [本週目錄](README.md) · [下一課](<day7-7-week13-final-report.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「結果整合子章」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

JSON schema 讓分析器能檢查必要欄位；checksum 防止不小心修改原始資料後仍引用舊结論。summary 是衍生結果，不能取代 raw latency 和環境快照。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[analysis/causal_lm_report.py](<../../analysis/causal_lm_report.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def verify_bundle(directory):
    """比對 evidence.json 登錄的 SHA-256，拒絕分析已被改動的原始結果。"""
    evidence = json.loads((directory / 'evidence.json').read_text())
    for name, expected in evidence['sha256'].items():
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Artifact checksum mismatch: {name}')


def summarize_runs(runs):
    """各 batch 至少三次；保留均值、範圍與 CV，計算 8→16 的相對變化。"""
    groups = {}
    for batch in (8, 16):
        selected = [r for r in runs if r['batch_size'] == batch]
        if len(selected) < 3:
            raise ValueError('At least three runs per batch required')
        throughput = [r['tokens_per_second'] for r in selected]
        if not all(math.isfinite(x) and x > 0 for x in throughput):
            raise ValueError('Throughput must be finite and positive')
        # CV = 樣本標準差／均值，表示重複測量波動；不是信賴區間。
        # peak memory 取三次中的最大值；throughput 與 mean step 則各自取平均。
        groups[str(batch)] = {
            'repetitions': len(selected),
            'mean_tokens_per_second': statistics.fmean(throughput),
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 verify_bundle 與 summarize_runs，解釋缺 run、非法 throughput 或 hash 不符時為何應拒絕出報告。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '16,39p' 'analysis/causal_lm_report.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week13/day7-6-result-integration.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
