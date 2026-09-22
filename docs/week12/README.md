# Week12 — Linux 效能工具：以假說選工具

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week11](../week11/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

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

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
