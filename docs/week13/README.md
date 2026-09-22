# Week13 — Benchmark：從負載定義到可重算結果

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week12](../week12/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

先定義量測範圍和單位：API request/s、DB transaction/s、磁碟 IOPS、網路 bit/s、模型 tokens/s 並不互換。Latency 描述單次時間，throughput 描述單位時間完成量。

控制 workload、硬體、版本、seed、warmup 與重複次數，避免只選最好數字。平均與尾延遲回答不同問題；CV 是標準差相對平均的比例，不是信賴區間。

現行 13M causal LM 的 raw bundle 可離線核對與分析；舊 CPU／storage／DB／network shell runner 是獨立工具，包含資源壓力與寫入行為，不代表已接到 MPI API。

## 目前環境與實測邊界

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

[本週實作／證據入口](<../../benchmark/results/causal-lm-20260922/evidence.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：FastAPI benchmark](<Day1-FastAPI-API-Benchmark.md>)
- [Day2：Redis benchmark](<Day2-Redis-Benchmark.md>)
- [Day3：PostgreSQL benchmark](<Day3-PostgreSQL-Benchmark.md>)
- [Day4：DB concurrency](<Day4-PostgreSQL-Concurrency-Benchmark.md>)
- [Day5：資源監控與量測區段](<day5-resource-monitoring.md>)
- [Day6：測試自動化](<day6-benchmark-automation.md>)
- [Day7-1：CPU benchmark 子章](<day7-1-cpu-benchmark.md>)
- [Day7-2：Storage benchmark 子章](<day7-2-storage-benchmark.md>)
- [Day7-3：Network benchmark 子章](<day7-3-network-benchmark.md>)
- [Day7-4：Benchmark framework 子章](<day7-4-benchmark-framework.md>)
- [Day7-5：Framework v2 子章](<day7-5-benchmark-framework-v2.md>)
- [Day7-6：結果整合子章](<day7-6-result-integration.md>)
- [Day7-7：Week13 整合報告子章](<day7-7-week13-final-report.md>)
- [Day7：Benchmark 報告總結](<day7-benchmark-report.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
