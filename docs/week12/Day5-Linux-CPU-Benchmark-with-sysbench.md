<!-- current-curriculum: 2026-09-22 -->
# Week12 Day5 — CPU baseline 與 sysbench

[上一課](<Day4-Linux-Historical-Performance-Analysis.md>) · [本週目錄](README.md) · [下一課](<Day6-Linux-CPU-Profiling-with-perf.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「CPU baseline 與 sysbench」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

baseline 必須固定 threads、時間與工作內容；工具版本或事件定義不同，分數不可直接混用。現存 CPU 腳本採 stress-ng，不能因課程標題是 sysbench 就把輸出改名。

## 在現在的專案中

歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

本課對照：[benchmark/cpu/run_stress_ng.sh](<../../benchmark/cpu/run_stress_ng.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
echo "Duration: ${TIMEOUT}s"

echo ""

# CPU 壓測：--cpu 指定 worker 數，--timeout 指定持續時間，metrics 顯示量測統計。
stress-ng \
  --cpu ${CPU_WORKERS} \
  --timeout ${TIMEOUT}s \
  --metrics-brief
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 比較舊教材的 sysbench 概念與現存 stress-ng 腳本，列出建立新 baseline 要記錄的條件；本課不宣稱已重跑 sysbench。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '17,25p' 'benchmark/cpu/run_stress_ng.sh'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/cpu/results/cpu_benchmark_20260810.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week12/Day5-Linux-CPU-Benchmark-with-sysbench.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
