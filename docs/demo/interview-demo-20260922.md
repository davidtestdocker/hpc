# 本輪求職展示：平台自動化與 AI 效能

主要展示頁為 [README](../../README.md#interview-walkthrough)：架構、自動流程、
效能比較、證據與展示順序均已整合在同一頁。本文件作為講解時的詳細備忘。

日期：2026-09-22。主環境 `hpc-gpu-sg`，CPU system-pool＋單張 L4 gpu-pool。
兩條展示共用基礎設施，訓練 benchmark 目前仍由獨立 runner 執行。

## 架構師／平台方向：先展示工作生命週期

1. 開 [架構圖](../architecture/platform-architecture.md)，說明 API、Redis／DB、
   worker、Kueue admission、JobSet execution 的責任。
2. 開 [部署／bootstrap](../runbooks/platform-bootstrap.md) 與
   [CPU-only 重建驗收](../evidence/cpu-bootstrap-acceptance-20260921.json)，說明
   可重建範圍；保留 9/21 網路 allow／deny 與 controller／Redis 恢復案例。
3. 依 [自動 worker 操作](../runbooks/automatic-worker.md) 提交 MPI，只輪詢 GET result。
   [實測 evidence](../evidence/automatic-worker-20260922.json) 已保存正常完成、
   queued／submitted worker 重啟接續、ranks 0／1／2、DB 一致與失敗 dead-letter。
4. 說明固定 JobSet 名稱的重試保護，以及 Redis／Postgres 尚無跨系統原子交易。
   MPI rank smoke test 證明分散式啟動與結果回收，沒有宣稱 GPU performance。

## AI 效能方向：用一組數據說明方法與取捨

1. 開 [13M causal LM 報告](../performance/causal-lm-l4-20260922.md)，先說模型、
   byte tokenizer、固定資料、warmup、交錯三次量測與 profiler 分離。
2. 展示 batch 8／16：110,785→200,841 byte tokens/s；代價為 18.50→20.39 ms
   step latency、375.02→532.39 MiB peak allocated memory。
3. 開 [摘要](../../benchmark/results/causal-lm-20260922/summary.json) 和壓縮 trace，
   指出 multi-tensor kernels 五步约 21.7 ms 持平、GEMM 12.27→23.84 ms，
   解釋固定成本攤薄的推論。不能把 profiler GPU kernel 時間加總當作 wall time。
4. 說明低頻 telemetry、time-sharing、13M 小模型／小語料與品質驗證的邊界。
   數據支持效能工程方法，沒有大型 pretrained LLM 或多 GPU 結論。

## 本輪完成條件與證據

| 原約定 | 驗證入口 |
|---|---|
| 能部署 | [CPU-only bootstrap](../evidence/cpu-bootstrap-acceptance-20260921.json)、[主環境部署](../evidence/platform-deployment-20260921.json) |
| 能跑真實工作／自動拿結果 | [Day 4 自動 MPI、重啟、DB／queue 核對](../evidence/automatic-worker-20260922.json) |
| 能完成一次恢復 | [controller／Redis 恢復](platform-recovery-20260921.md)、Day 4 worker 重啟接續 |
| 能解釋一組 AI 效能實驗 | [Day 5／6 新報告與 traces](../performance/causal-lm-l4-20260922.md) |
| 文件與求職展示 | 本文件、[架構師版履歷](../career/resume-hpc-system.md)、[AI 效能版履歷](../career/resume-ai-performance.md) |

GPU 實驗後的 [主平台 preflight](../evidence/platform-after-training-20260922.json)
是唯讀前置條件檢查，不能取代上列 workload 成功證據。舊環境 log、失敗案例與
9/21 synthetic training 結果均保留，不將本輪改善反寫成歷史已完成。
