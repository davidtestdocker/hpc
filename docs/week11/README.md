# Week11 — Observability：指標的來源與意義

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week10](../week10/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

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

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
