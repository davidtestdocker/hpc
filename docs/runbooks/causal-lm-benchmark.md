# 單 GPU 訓練與 profiling 操作

現行入口（2026-09-22）。沿用一張 L4，不增加 GPU pool／quota。

程式閱讀順序：`scripts/run_causal_lm_benchmark.py` 建立環境與收檔 →
`benchmark/gpu/causal_lm_benchmark.py` 的 `prepare`／`step`／`main` 執行訓練與量測 →
`analysis/causal_lm_report.py` 核對 hashes 並產出比較。現行程式已補中文註解；
結果目錄的 `benchmark-source.py` 保留當時實測原文，避免註解更新改變證據 hash。

先確認目前 GPU workload 已完成、節點可用，以及本機有 kubeconfig、kubectl、
repo `.venv`（PyYAML）。本機不用安裝 PyTorch；訓練在容器內執行。

```bash
PYTHONPATH=. .venv/bin/python -m scripts.run_causal_lm_benchmark \
  --context gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg \
  --name causal-lm-REPLACE_WITH_UNIQUE_RUN_ID \
  --output benchmark/results/causal-lm-REPLACE_WITH_UNIQUE_RUN_ID --execute
```

名稱需改成合法的小寫 Kubernetes 名稱，output 使用新目錄。工具以 create 建立
ConfigMap 與一個 GPU Pod，保存 README corpus 與程式快照；等待完成後取回 JSON、
兩份壓縮 CUDA trace、image digest／SHA-256，再清理這次 Pod／ConfigMap。
失敗時保留 Pod 與部分結果供排查，不會覆寫既有實驗目錄。

```bash
PYTHONPATH=. .venv/bin/python -m analysis.causal_lm_report \
  benchmark/results/causal-lm-REPLACE_WITH_UNIQUE_RUN_ID
```

分析器拒絕不足三次的比較或沒有 CUDA kernel event 的 trace。
讀取 [本輪分析報告](../performance/causal-lm-l4-20260922.md) 理解 byte-token 單位、
profiler overhead 與 time-sharing 限制。9/21 舊程式與結果保留；不可將不同模型的
throughput 差異直接當成優化成效。
