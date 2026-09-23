# Week12 — Linux 效能工具：以假說選工具

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week11](../week11/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

量測先定義問題：是吞吐不足、尾延遲高、資源不足，還是工作根本沒啟動？相同指標在不同工作負載下有不同意義。

CPU 使用率與 load、memory 的 available／RSS、I/O 的 latency／IOPS／throughput 要分開看。perf 取樣 CPU 執行位置，strace 觀察 syscall；工具會帶來負擔且可能需要權限。

本週範例以唯讀觀察和舊結果判讀為主。stress-ng、sysbench、fio 會消耗資源，strace 可能捕捉敏感參數，不應直接對主平台所有程序執行。

## 目前環境與實測邊界

歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

## 本週材料怎麼讀

本週各課以 Linux 工具命令和文內輸出為材料，沒有每課專用的 Python 實作。

- **Day1～Day3：CPU、記憶體、磁碟** — 讀各課的觀察指令與輸出欄位，分辨使用量、等待和吞吐；Day3 的磁碟測試對象是當時的 `/data`。
- **Day4：歷史資料** — 課文的 `sar` 紀錄用來學時間對齊，將問題發生時間與資源數值放在一起看。
- **Day5：CPU 基線** — 課文比較 `sysbench` 的 1／4 threads 結果。原先連結的 `cpu_benchmark_20260810.md` 是 Week13 的 stress-ng 材料，已從本週入口移除。
- **Day6～Day7：程式在忙什麼、等什麼** — `perf` 與 `strace` 的命令、工具限制、輸出解讀都在各課正文。

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
