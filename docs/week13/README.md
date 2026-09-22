# Week13 — Benchmark：從負載定義到可重算結果

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week12](../week12/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

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

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
