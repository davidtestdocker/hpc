# Week11 — Observability：指標的來源與意義

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week10](../week10/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

Metric 是帶有時間與 labels 的數值；Prometheus 以 scrape 週期拉取端點，Grafana 查詢並畫圖。Exporter 把特定系統狀態轉成可抓取的指標。

Counter 累計事件，Gauge 表示當下值，Histogram 用桶統計分布。看曲線前先確認單位、時間窗、label 和資料是否缺失。up=1 只表示 scrape 成功，不表示業務成功。

HTTP、node、GPU 是不同觀測層；沒有 job_id 關聯就不能假設某張 GPU 曲線只屬於某筆工作。9/22 訓練使用 nvidia-smi 取樣與 CUDA trace，並非當次 DCGM dashboard 驗收。

## 目前環境與實測邊界

監控 manifests 和歷史 dashboard 保留為獨立路徑；不宣稱即時 target 健康。

[本週實作／證據入口](<../evidence/README.md>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：Prometheus 與資源分工](<Day1-建立Prometheus監控平台與Observability-Node-Pool.md>)
- [Day2：Scrape target 與 pull model](<Day2-Prometheus-ScrapeJob-Target與PullModel.md>)
- [Day3：FastAPI application metrics](<Day3-FastAPI-Application-Metrics.md>)
- [Day4：Node Exporter 與 dashboard](<Day4-NodeExporter-GrafanaDashboard-KubernetesServiceDiscovery.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
