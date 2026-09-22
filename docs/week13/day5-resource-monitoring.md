<!-- current-curriculum: 2026-09-22 -->
# Week13 Day5 — 資源監控與量測區段

[上一課](<Day4-PostgreSQL-Concurrency-Benchmark.md>) · [本週目錄](README.md) · [下一課](<day6-benchmark-automation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「資源監控與量測區段」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

監控可協助解釋變化，但全程平均可能混入初始化、暖機與 export。9/22 telemetry 包含多階段，不能當成各 batch 的精確 GPU 使用率。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[benchmark/gpu/causal_lm_benchmark.py](<../../benchmark/gpu/causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
    """背景約每秒收集一次 nvidia-smi；記錄時間以區分暖機、計時與 profiler 階段。"""
    while not stop.is_set():
        try:
            sample = subprocess.check_output([
                'nvidia-smi', '--query-gpu=timestamp,uuid,utilization.gpu,memory.used,power.draw,temperature.gpu',
                '--format=csv,noheader,nounits',
            ], text=True, timeout=5).strip()
            rows.append({'unix_time': time.time(), 'sample': sample})
        except (OSError, subprocess.SubprocessError) as exc:
            rows.append({'error': str(exc)})
        stop.wait(1)


def main():
    """完成六次非 profiler 量測、兩組 CUDA trace，最後保存 JSON 與遙測。"""
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError('BF16 CUDA device required')
    output = Path(os.getenv('OUTPUT_DIR', '/results'))
    output.mkdir(parents=True, exist_ok=True)
    source = Path(os.getenv('CORPUS_PATH', '/benchmark/corpus.txt')).read_bytes()
    if len(source) <= SEQ:
        raise ValueError('Corpus too short')
    # 每個 UTF-8 byte 是一個 token；此處 tokens/s 不能與 BPE tokenizer 的數字直接比較。
    corpus = torch.tensor(list(source), dtype=torch.long)
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 在訓練程式找 telemetry thread 與 timed steps 的範圍，說明哪些資料支持趨勢、哪些不能直接歸因到某個 batch。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '90,113p' 'benchmark/gpu/causal_lm_benchmark.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week13/day5-resource-monitoring.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
