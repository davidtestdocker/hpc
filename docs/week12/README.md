# Week12 — Linux 效能工具：以假說選工具

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week11](../week11/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

量測先定義問題：是吞吐不足、尾延遲高、資源不足，還是工作根本沒啟動？相同指標在不同工作負載下有不同意義。

CPU 使用率與 load、memory 的 available／RSS、I/O 的 latency／IOPS／throughput 要分開看。perf 取樣 CPU 執行位置，strace 觀察 syscall；工具會帶來負擔且可能需要權限。

本週範例以唯讀觀察和舊結果判讀為主。stress-ng、sysbench、fio 會消耗資源，strace 可能捕捉敏感參數，不應直接對主平台所有程序執行。

## 目前環境與實測邊界

歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

[本週實作／證據入口](<../../benchmark/cpu/results/cpu_benchmark_20260810.md>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：CPU 分析](<Day1-Linux-CPU-Performance-Analysis.md>)
- [Day2：Memory 分析](<Day2-Linux-Memory-Performance-Analysis.md>)
- [Day3：Disk 分析](<Day3-Linux-Disk-Performance-Analysis.md>)
- [Day4：歷史監控與時間對齊](<Day4-Linux-Historical-Performance-Analysis.md>)
- [Day5：CPU baseline 與 sysbench](<Day5-Linux-CPU-Benchmark-with-sysbench.md>)
- [Day6：perf 取樣](<Day6-Linux-CPU-Profiling-with-perf.md>)
- [Day7：strace 與 system call](<Day7-Linux-System-Call-Analysis-with-strace.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
